import logging

from agents.state import AgriState
from tools.profile_tool import fetch_farmer_profile
from tools.disease_tool import detect_disease
from tools.rag_tool import rag_search
from services.llm_service import generate_text

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """You are Krishi Sahayak, a crop disease diagnosis expert.
Using the diagnosis result and retrieved treatment knowledge, provide:
1. Disease name and confidence
2. Symptoms observed
3. Likely cause
4. Treatment steps (chemical and organic options with dosage)
5. Prevention steps

Respond in the farmer's language ({language}). Plain text only, no markdown."""


def run_disease_agent(state: AgriState) -> AgriState:
    user_id = state["user_id"]
    query = state.get("query", "What disease does my crop have?")
    image_b64 = state.get("image_base64")
    language = state.get("language", "en")

    # 1. Farmer profile for crop context
    profile = fetch_farmer_profile(user_id)
    crops = profile.get("primary_crops", [])

    # 2. Disease model inference
    disease_result = {}
    if image_b64:
        disease_result = detect_disease.invoke(
            {"image_base64": image_b64, "crop_name": crops[0] if crops else ""}
        )

    disease_name = disease_result.get("disease", "unknown")
    plant_name = disease_result.get("plant", "")
    confidence = disease_result.get("confidence", 0.5 if image_b64 else 0.72)

    # The plant identified in the image is the best crop context when the farmer
    # did not set up a profile / primary crops.
    identified_crop = plant_name if plant_name and plant_name.lower() != "unknown" else ""
    crop_context = ", ".join(crops) or identified_crop

    # 3. RAG retrieval for treatment
    rag_query = f"{disease_name} disease treatment prevention {crop_context}".strip()
    rag_results = rag_search.invoke({"query": rag_query, "top_k": 5})
    context_chunks = [r["text"] for r in rag_results]
    sources = [r["source"] for r in rag_results]

    # 4. LLM for structured response
    context_str = "\n\n".join(context_chunks)
    prompt = f"""{_SYSTEM_PROMPT.format(language=language)}

Farmer's Crops: {crop_context or 'not specified'}
Identified plant in image: {identified_crop or 'not identified'}
Farmer's Query: {query}

Disease Detection Result:
- Plant/crop: {identified_crop or 'unknown'}
- Disease: {disease_name}
- Confidence: {confidence:.0%}
- Additional info: {disease_result.get('details', 'N/A')}
- Image supplied: {'yes' if image_b64 else 'no; treat this as a text-based pest/disease advisory, not image diagnosis'}

Knowledge Base:
{context_str}

Diagnosis and Treatment:"""

    response = generate_text(
        prompt,
        (
            "For insect or disease symptoms, inspect leaves, stems, and grain heads closely. "
            "Remove badly affected parts, avoid unnecessary pesticide mixing, and contact your "
            "local KVK or agriculture officer before applying chemical treatment."
        ),
        history=state.get("history", ""),
    )

    logger.info(
        "DiseaseAgent: user=%s disease=%s confidence=%.2f",
        user_id, disease_name, confidence,
    )

    return {
        **state,
        "farmer_profile": profile,
        "retrieved_context": context_chunks,
        "sources": sources,
        "agent_response": response,
        "confidence": confidence,
        "tool_outputs": {"disease_detection": disease_result},
    }
