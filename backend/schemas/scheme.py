from typing import Optional

from pydantic import BaseModel


class SchemeSearchRequest(BaseModel):
    query: str = ""
    state: Optional[str] = None
    crop: Optional[str] = None
    session_id: str = ""


class SchemeResult(BaseModel):
    scheme_id: str
    scheme_name: str
    ministry: str
    benefits: str
    eligibility_criteria: str
    application_url: str
    is_eligible: Optional[bool] = None


class SchemeSearchResponse(BaseModel):
    schemes: list[SchemeResult]
    advisory_text: str
    sources: list[str] = []
