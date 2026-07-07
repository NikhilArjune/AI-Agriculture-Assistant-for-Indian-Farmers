from pydantic import BaseModel


class WeatherAdvisoryRequest(BaseModel):
    lat: float
    lng: float
    session_id: str = ""


class WeatherAdvisoryResponse(BaseModel):
    advisory_text: str
    temperature_c: float = 0.0
    humidity_percent: float = 0.0
    rainfall_mm: float = 0.0
    wind_speed_kmh: float = 0.0
    alert_type: str = "general"
    severity: str = "low"
    sources: list[str] = []
