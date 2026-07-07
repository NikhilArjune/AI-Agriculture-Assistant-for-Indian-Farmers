import logging

from agents.state import AgriState
from tools.profile_tool import fetch_farmer_profile
from tools.weather_tool import get_weather_forecast
from services.llm_service import generate_text

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """You are Krishi Sahayak, a weather advisory expert for Indian farmers.
Using the weather forecast data and the farmer's crop profile, provide:
1. Weather summary (next 7 days)
2. Irrigation recommendation
3. Pest/disease risk based on humidity and temperature
4. Best window for sowing or spraying
5. Any alerts (rain, heat, frost)

Respond in the farmer's language ({language}). Plain text only."""


def run_weather_agent(state: AgriState) -> AgriState:
    user_id = state["user_id"]
    query = state.get("query", "What is the weather forecast?")
    language = state.get("language", "en")

    profile = fetch_farmer_profile(user_id)
    location = profile.get("location", {})
    crops = profile.get("primary_crops", [])
    lat = location.get("coordinates", {}).get("lat", 20.5937)
    lng = location.get("coordinates", {}).get("lng", 78.9629)

    weather_data = get_weather_forecast.invoke({"lat": lat, "lng": lng})

    prompt = f"""{_SYSTEM_PROMPT.format(language=language)}

Farmer Location: {location.get('district', '')}, {location.get('state', '')}
Farmer's Crops: {', '.join(crops)}
Farmer's Query: {query}

Weather Forecast:
{weather_data}

Advisory:"""

    current = weather_data.get("current", {})
    response = generate_text(
        prompt,
        (
            f"Weather summary: {current.get('description', 'weather data available')}. "
            f"Temperature is about {current.get('temp', 0)}°C and humidity is "
            f"{current.get('humidity', 0)}%. Monitor local rainfall before irrigation "
            "or spraying, and consult your local KVK for field-specific advice."
        ),
        history=state.get("history", ""),
    )

    logger.info("WeatherAgent: user=%s location=%s", user_id, location.get("district"))

    return {
        **state,
        "farmer_profile": profile,
        "retrieved_context": [],
        "sources": ["OpenWeatherMap API"],
        "agent_response": response,
        "confidence": 0.9,
        "tool_outputs": {"weather": weather_data},
    }
