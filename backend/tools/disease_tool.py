import base64
import io
import logging

from langchain_core.tools import tool

logger = logging.getLogger(__name__)


@tool
def detect_disease(image_base64: str, crop_name: str = "") -> dict:
    """Detect crop disease from a base64-encoded image.

    Tries CNN model first (PlantVillage), falls back to Vision LLM.

    Returns dict with: disease, confidence, details.
    """
    if not image_base64:
        return {"disease": "unknown", "confidence": 0.0, "details": "No image provided."}

    # Option A: CNN model inference
    result = _cnn_detect(image_base64, crop_name)
    if result.get("confidence", 0) >= 0.7:
        return result

    # Option B: Vision LLM fallback
    return _vision_llm_detect(image_base64, crop_name)


def _cnn_detect(image_base64: str, crop_name: str) -> dict:
    """PlantVillage CNN model inference (placeholder — swap with real model)."""
    try:
        from PIL import Image
        image_bytes = base64.b64decode(image_base64)
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img = img.resize((224, 224))

        # TODO: Load trained PlantVillage model and run inference
        # model = load_plantvillage_model()
        # prediction = model.predict(preprocess(img))
        # return {"disease": CLASS_NAMES[prediction.argmax()], "confidence": float(prediction.max()), "details": "CNN"}

        logger.info("DiseasonTool: CNN model not loaded yet, returning low confidence.")
        return {"disease": "unknown", "confidence": 0.3, "details": "CNN model not configured."}
    except Exception as exc:
        logger.error("DiseasonTool: CNN error: %s", exc)
        return {"disease": "unknown", "confidence": 0.0, "details": str(exc)}


def _vision_llm_detect(image_base64: str, crop_name: str) -> dict:
    """Vision LLM fallback using the configured provider's multimodal model."""
    try:
        import json

        from langchain_core.messages import HumanMessage

        from services.llm_service import invoke_with_fallback, vision_models

        crop_ctx = f" The farmer says the crop is {crop_name}." if crop_name else ""
        message = HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": (
                        "You are a plant pathologist. Look at this image and (1) identify the "
                        f"fruit / vegetable / crop plant shown, and (2) analyze it for disease.{crop_ctx} "
                        "Respond ONLY with JSON: {\"plant\": \"<fruit/vegetable/crop name, or unknown>\", "
                        "\"disease\": \"<disease name, or healthy>\", "
                        "\"confidence\": <0.0-1.0>, \"details\": \"<brief explanation of visible symptoms>\"}"
                    ),
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                },
            ]
        )

        content = invoke_with_fallback([message], vision_models())

        # Extract JSON object from the response
        start = content.find("{")
        end = content.rfind("}") + 1
        if start >= 0 and end > start:
            parsed = json.loads(content[start:end])
            parsed.setdefault("plant", "unknown")
            parsed.setdefault("disease", "unable to determine")
            parsed.setdefault("confidence", 0.5)
            parsed.setdefault("details", "")
            return parsed

        return {"plant": "unknown", "disease": "unable to determine", "confidence": 0.4, "details": content[:300]}

    except Exception as exc:
        logger.error("DiseaseTool: Vision LLM error: %s", exc)
        message = str(exc)
        if "RESOURCE_EXHAUSTED" in message or "429" in message:
            details = (
                "Image analysis is temporarily unavailable because the daily AI quota "
                "was reached. Please try again later."
            )
        else:
            details = "Image could not be analyzed automatically."
        return {"plant": "unknown", "disease": "unknown", "confidence": 0.0, "details": details}
