from typing import Optional

from pydantic import BaseModel


class SoilAdvisoryRequest(BaseModel):
    crop_name: str
    soil_type: str = ""
    ph_level: Optional[float] = None
    nitrogen: Optional[float] = None
    phosphorus: Optional[float] = None
    potassium: Optional[float] = None
    session_id: str = ""


class SoilAdvisoryResponse(BaseModel):
    advisory_text: str
    fertilizer_plan: str
    deficiencies: list[str] = []
    recommendations: list[str] = []
    sources: list[str] = []
    requires_human_help: bool = False
