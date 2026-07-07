from typing import Optional

from pydantic import BaseModel


class MarketPriceRequest(BaseModel):
    commodity: str
    district: str
    state: str
    session_id: str = ""


class PriceEntry(BaseModel):
    mandi_name: str
    min_price: float
    max_price: float
    modal_price: float
    unit: str = "quintal"
    price_date: str
    source_status: str = "unknown"


class MarketPriceResponse(BaseModel):
    commodity: str
    district: str
    prices: list[PriceEntry]
    recommendation: str
    trend: str = "stable"
    sources: list[str] = []
