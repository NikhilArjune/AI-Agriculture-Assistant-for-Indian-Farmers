import logging

from agents.state import AgriState

logger = logging.getLogger(__name__)

# Languages that are already Latin-script or where we keep English as-is
_NO_TRANSLATE = {"en"}


def run_translation(state: AgriState) -> AgriState:
    language = state.get("language", "en")
    response = state.get("agent_response", "")
    farmer_profile = state.get("farmer_profile", {})

    # Prefer profile language over detected language
    preferred_lang = farmer_profile.get("preferred_lang", language)

    if preferred_lang in _NO_TRANSLATE or not response:
        return state

    # Check if response already appears to be in the target language
    # (LLM agents are prompted to respond in the farmer's language, so
    # translation is a safety net for cases where they don't.)
    try:
        from services.llm_service import extract_text, get_llm_client
        llm = get_llm_client()

        lang_names = {
            "hi": "Hindi", "te": "Telugu", "ta": "Tamil",
            "mr": "Marathi", "pa": "Punjabi", "bn": "Bengali", "kn": "Kannada",
        }
        lang_name = lang_names.get(preferred_lang, preferred_lang)

        prompt = (
            f"Translate the following agricultural advisory text to {lang_name}. "
            f"Keep crop names, chemical names, and numbers unchanged. "
            f"Return ONLY the translated text.\n\n{response}"
        )
        translated = extract_text(llm.invoke(prompt))
        if translated:
            response = translated
            logger.info(
                "TranslationNode: translated to %s for user=%s",
                preferred_lang, state.get("user_id"),
            )
    except Exception as exc:
        logger.warning("TranslationNode: translation failed (%s), returning original.", exc)

    return {**state, "agent_response": response, "language": preferred_lang}
