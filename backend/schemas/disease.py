from typing import Optional

from pydantic import BaseModel


class DiseaseDetectRequest(BaseModel):
    image_base64: str
    crop_name: Optional[str] = None
    session_id: Optional[str] = None
    language: Optional[str] = None


class DiseaseDetectResponse(BaseModel):
    detected_plant: str = ""
    detected_disease: str
    confidence: float
    treatment_plan: str
    prevention_tips: str
    sources: list[str]
    report_id: Optional[str] = None
    requires_human_help: bool = False
