import logging
from datetime import datetime, timedelta

import httpx
from langchain_core.tools import tool

from core.config import settings

logger = logging.getLogger(__name__)

_AGMARKNET_BASE = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"


@tool
def get_mandi_prices(commodity: str, district: str, state: str) -> dict:
    """Fetch latest mandi prices for a commodity from AGMARKNET/data.gov.in."""
    if not settings.agmarknet_api_key:
        return _empty_result("missing_api_key", "AGMARKNET_API_KEY is not configured.")

    params = {
        "api-key": settings.agmarknet_api_key,
        "format": "json",
        "filters[commodity]": commodity.title(),
        "filters[district]": district,
        "filters[state]": state,
        "limit": 50,
    }

    try:
        resp = httpx.get(_AGMARKNET_BASE, params=params, timeout=20)
        resp.raise_for_status()
        payload = resp.json()
        records = payload.get("records", [])
    except Exception as exc:
        logger.error("MarketTool: AGMARKNET fetch failed: %s", exc)
        return _empty_result("api_error", f"AGMARKNET request failed: {exc}")

    if not records:
        logger.warning(
            "MarketTool: no AGMARKNET records for commodity=%s district=%s state=%s",
            commodity,
            district,
            state,
        )
        return _empty_result("no_records", "No AGMARKNET records matched this commodity and district.")

    prices = []
    for record in records:
        prices.append({
            "commodity": record.get("commodity") or commodity,
            "market": record.get("market") or "Unknown Mandi",
            "variety": record.get("variety") or "",
            "grade": record.get("grade") or "",
            "min": _to_float(record.get("min_price")),
            "max": _to_float(record.get("max_price")),
            "modal": _to_float(record.get("modal_price")),
            "date": record.get("arrival_date") or "",
            "state": record.get("state") or state,
            "district": record.get("district") or district,
        })

    return {
        "records": prices,
        "_mock": False,
        "_source_status": "live_agmarknet",
        "message": f"Found {len(prices)} live AGMARKNET record(s).",
    }


@tool
def get_price_trend(commodity: str, district: str, days: int = 30) -> dict:
    """Fetch local 30-day price trend from MongoDB market_prices collection."""
    try:
        import asyncio
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(_async_trend(commodity, district, days))
    except Exception as exc:
        logger.debug("MarketTool: trend fetch skipped: %s", exc)
        return {"trend": "unknown", "avg_30d": None, "data_points": []}


async def _async_trend(commodity: str, district: str, days: int) -> dict:
    from models.market_price import MarketPrice

    cutoff = datetime.utcnow() - timedelta(days=days)
    prices = await MarketPrice.find(
        MarketPrice.commodity == commodity,
        MarketPrice.district == district,
        MarketPrice.created_at >= cutoff,
    ).sort("-created_at").limit(30).to_list()

    if not prices:
        return {"trend": "unknown", "avg_30d": None, "data_points": []}

    modals = [p.modal_price for p in prices]
    avg = round(sum(modals) / len(modals), 2)
    first, last = modals[-1], modals[0]
    trend = "rising" if last > first * 1.03 else "falling" if last < first * 0.97 else "stable"
    return {"trend": trend, "avg_30d": avg, "data_points": modals[:7]}


def _empty_result(status: str, message: str) -> dict:
    return {"records": [], "_mock": False, "_source_status": status, "message": message}


def _to_float(value: object) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0
