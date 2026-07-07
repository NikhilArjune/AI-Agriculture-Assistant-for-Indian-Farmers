from datetime import datetime

from beanie import Document
from pydantic import Field


class MarketPrice(Document):
    commodity: str
    variety: str = ""
    district: str
    state: str
    mandi_name: str
    min_price: float = 0.0
    max_price: float = 0.0
    modal_price: float = 0.0
    unit: str = "quintal"
    price_date: datetime = Field(default_factory=datetime.utcnow)
    source: str = "agmarknet"
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "market_prices"
        indexes = [
            [("commodity", 1), ("district", 1), ("price_date", -1)],
            [("state", 1), ("price_date", -1)],
        ]
