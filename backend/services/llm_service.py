import logging
import time

from langchain_core.language_models import BaseChatModel

from core.config import settings

logger = logging.getLogger(__name__)

# Cache one client per model name so fallbacks don't rebuild on every call.
_CLIENT_CACHE: dict[str, BaseChatModel] = {}

# Models seen returning a daily-quota error are parked here (model -> unix ts until
# which to skip them), so we don't waste a failed round-trip on every later call.
_COOLDOWN: dict[str, float] = {}
_COOLDOWN_SECONDS = 15 * 60  # daily free-tier quota won't recover fast; skip for a while


def _mark_exhausted(model: str) -> None:
    _COOLDOWN[model] = time.time() + _COOLDOWN_SECONDS


def _in_cooldown(model: str) -> bool:
    until = _COOLDOWN.get(model)
    return until is not None and time.time() < until


def _split(csv: str) -> list[str]:
    return [m.strip() for m in csv.split(",") if m.strip()]


def _dedup(models: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for m in models:
        if m and m not in seen:
            seen.add(m)
            ordered.append(m)
    return ordered


def text_models() -> list[str]:
    """Primary text model followed by configured quota fallbacks."""
    return _dedup([settings.llm_model, *_split(settings.llm_fallback_models)])


def vision_models() -> list[str]:
    """Primary vision model followed by configured quota fallbacks."""
    return _dedup([settings.llm_vision_model, *_split(settings.llm_vision_fallback_models)])


def _is_quota_error(exc: Exception) -> bool:
    message = str(exc)
    return "RESOURCE_EXHAUSTED" in message or "429" in message


def client_for(model: str) -> BaseChatModel:
    if model not in _CLIENT_CACHE:
        _CLIENT_CACHE[model] = _build_chat_model(model)
    return _CLIENT_CACHE[model]


def _build_chat_model(model: str) -> BaseChatModel:
    provider = settings.llm_provider.lower()

    if provider == "groq":
        from langchain_groq import ChatGroq
        logger.info("LLMService: using Groq (%s)", model)
        return ChatGroq(
            api_key=settings.groq_api_key,
            model=model,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,
        )

    if provider == "openai":
        from langchain_openai import ChatOpenAI
        logger.info("LLMService: using OpenAI (%s)", model)
        return ChatOpenAI(
            api_key=settings.openai_api_key,
            model=model,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,
        )

    if provider in {"google", "gemini"}:
        from langchain_google_genai import ChatGoogleGenerativeAI
        logger.info("LLMService: using Google Gemini (%s)", model)
        return ChatGoogleGenerativeAI(
            google_api_key=settings.google_api_key,
            model=model,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,
            retries=0,
            request_timeout=20,
        )

    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        logger.info("LLMService: using Anthropic (%s)", model)
        return ChatAnthropic(
            api_key=settings.anthropic_api_key,
            model=model,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,
        )

    raise ValueError(f"Unknown LLM provider: {provider}. Choose groq, openai, google, or anthropic.")


def get_llm_client() -> BaseChatModel:
    """Chat model using the configured (primary) text model."""
    return client_for(settings.llm_model)


def get_vision_client() -> BaseChatModel:
    """Chat model using the configured (primary) multimodal/vision model."""
    return client_for(settings.llm_vision_model)


def invoke_with_fallback(payload, models: list[str]) -> str:
    """Invoke ``payload`` against each model in turn, skipping models whose daily
    quota is exhausted. Returns the first non-empty text response.

    Raises the last exception if every model fails for a non-quota reason or all
    are quota-exhausted. ``payload`` is anything ``BaseChatModel.invoke`` accepts
    (a prompt string or a list of messages).
    """
    last_exc: Exception | None = None
    # Prefer models not currently parked in cooldown; fall back to all if every
    # candidate is parked (quota may have recovered since it was marked).
    ordered = [m for m in models if not _in_cooldown(m)] or list(models)
    for model in ordered:
        try:
            content = extract_text(client_for(model).invoke(payload))
            if content:
                if last_exc is not None:
                    logger.info("LLMService: recovered on fallback model %s", model)
                return content
            logger.warning("LLMService: empty response from %s, trying next.", model)
        except Exception as exc:  # noqa: BLE001 — provider errors vary by SDK
            last_exc = exc
            if _is_quota_error(exc):
                _mark_exhausted(model)
                logger.warning("LLMService: quota reached on %s, cooling down, trying next.", model)
                continue
            logger.error("LLMService: %s failed: %s", model, exc)
            continue
    if last_exc is not None:
        raise last_exc
    return ""


def generate_text(prompt: str, fallback: str, history: str = "") -> str:
    """Generate text with the configured LLM (with quota fallbacks), returning
    ``fallback`` on total failure.

    When ``history`` is provided it is prepended so the model has conversation
    context and does not re-introduce itself or ask for details already given.
    """
    if history:
        prompt = (
            "Recent conversation so far (use it for context; do NOT repeat greetings "
            "or introductions already given, and follow up on what was discussed):\n"
            f"{history}\n\n{prompt}"
        )
    try:
        content = invoke_with_fallback(prompt, text_models())
        if content:
            return content
        logger.warning("LLMService: empty model response, using fallback.")
    except Exception as exc:
        if _is_quota_error(exc):
            logger.warning("LLMService: all models quota-exhausted, using fallback.")
        else:
            logger.error("LLMService: generation failed, using fallback: %s", exc)
    return fallback


def extract_text(response: object) -> str:
    """Normalize LangChain provider responses into plain text."""
    content = getattr(response, "content", response)
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                value = item.get("text") or item.get("content")
                if isinstance(value, str):
                    parts.append(value)
            else:
                value = getattr(item, "text", None) or getattr(item, "content", None)
                if isinstance(value, str):
                    parts.append(value)
        return "\n".join(part.strip() for part in parts if part and part.strip()).strip()
    return str(content).strip() if content is not None else ""
