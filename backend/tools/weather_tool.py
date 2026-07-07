import logging

import httpx
from langchain_core.tools import tool

from core.config import settings

logger = logging.getLogger(__name__)

_OWM_BASE = "https://api.openweathermap.org/data/2.5"


@tool
def get_weather_forecast(lat: float, lng: float) -> dict:
    """Fetch 7-day weather forecast from OpenWeatherMap for given coordinates.

    Returns dict with: current (temp, humidity, description),
    daily (list of 7 days with min/max temp, rain, description).
    """
    if not settings.openweather_api_key:
        logger.warning("WeatherTool: OPENWEATHER_API_KEY not set, returning mock data.")
        return _mock_weather(lat, lng)

    try:
        params = {
            "lat": lat,
            "lon": lng,
            "appid": settings.openweather_api_key,
            "units": "metric",
            "exclude": "minutely,hourly,alerts",
        }
        resp = httpx.get(f"{_OWM_BASE}/onecall", params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        current = data.get("current", {})
        daily = data.get("daily", [])[:7]

        return {
            "current": {
                "temp": current.get("temp"),
                "humidity": current.get("humidity"),
                "description": current.get("weather", [{}])[0].get("description", ""),
            },
            "daily": [
                {
                    "date": d.get("dt"),
                    "min_temp": d["temp"]["min"],
                    "max_temp": d["temp"]["max"],
                    "humidity": d.get("humidity"),
                    "rain_mm": d.get("rain", 0),
                    "description": d.get("weather", [{}])[0].get("description", ""),
                }
                for d in daily
            ],
        }
    except Exception as exc:
        logger.error("WeatherTool: API call failed: %s", exc)
        return _mock_weather(lat, lng)


def _mock_weather(lat: float, lng: float) -> dict:
    return {
        "current": {"temp": 28, "humidity": 65, "description": "partly cloudy"},
        "daily": [
            {"date": None, "min_temp": 22, "max_temp": 34, "humidity": 60, "rain_mm": 0, "description": "sunny"},
            {"date": None, "min_temp": 21, "max_temp": 33, "humidity": 70, "rain_mm": 5, "description": "light rain"},
        ],
        "_mock": True,
    }
