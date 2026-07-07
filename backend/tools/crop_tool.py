import logging

from langchain_core.tools import tool

logger = logging.getLogger(__name__)

# Crop calendar: sowing windows and harvest duration by season and region
_CROP_CALENDAR: dict[str, dict] = {
    "wheat": {
        "season": "rabi",
        "sowing_window": "October – November",
        "harvest_window": "March – April",
        "duration_days": 120,
        "varieties": {
            "north": ["HD-2967", "PBW-343", "DBW-187"],
            "south": ["NW-1014", "K-9107"],
        },
    },
    "rice": {
        "season": "kharif",
        "sowing_window": "June – July",
        "harvest_window": "October – November",
        "duration_days": 120,
        "varieties": {
            "north": ["Pusa Basmati 1121", "MTU-7029"],
            "south": ["IR-64", "BPT-5204", "Swarna"],
        },
    },
    "maize": {
        "season": "kharif",
        "sowing_window": "June – July",
        "harvest_window": "September – October",
        "duration_days": 90,
        "varieties": {
            "north": ["Ganga-5", "HQPM-1"],
            "south": ["DHM-117", "NK-6240"],
        },
    },
    "cotton": {
        "season": "kharif",
        "sowing_window": "May – June",
        "harvest_window": "October – December",
        "duration_days": 180,
        "varieties": {
            "north": ["Bt Cotton RCH-2", "MRC-7918"],
            "south": ["Bunny BG-II", "Brahma BG-II"],
        },
    },
    "mustard": {
        "season": "rabi",
        "sowing_window": "October – November",
        "harvest_window": "February – March",
        "duration_days": 120,
        "varieties": {"north": ["Pusa Bold", "RH-749"], "south": ["Varuna", "Kranti"]},
    },
    "tomato": {
        "season": "all",
        "sowing_window": "June – July (kharif), October – November (rabi)",
        "harvest_window": "Approx. 60–70 days after transplant",
        "duration_days": 90,
        "varieties": {"north": ["Hybrid: Arka Rakshak"], "south": ["Arka Vikas", "PKM-1"]},
    },
}

_NORTH_STATES = {
    "Punjab", "Haryana", "Uttar Pradesh", "Uttarakhand", "Himachal Pradesh",
    "Rajasthan", "Bihar", "Jharkhand", "West Bengal",
}


@tool
def get_crop_calendar(crop_name: str, state: str = "") -> dict:
    """Get sowing/harvest calendar and recommended varieties for a crop.

    Args:
        crop_name: Name of the crop (lowercase).
        state: Farmer's state for regional variety recommendations.

    Returns:
        Dict with: season, sowing_window, harvest_window, duration_days, varieties.
    """
    key = crop_name.lower().strip()
    data = _CROP_CALENDAR.get(key)

    if not data:
        logger.debug("CropTool: no calendar for crop=%s", crop_name)
        return {
            "crop": crop_name,
            "message": "Calendar not available. Please consult your local KVK office.",
        }

    region = "north" if state in _NORTH_STATES else "south"
    varieties = data.get("varieties", {}).get(region, data.get("varieties", {}).get("north", []))

    return {
        "crop": crop_name,
        "season": data["season"],
        "sowing_window": data["sowing_window"],
        "harvest_window": data["harvest_window"],
        "duration_days": data["duration_days"],
        "recommended_varieties": varieties,
        "region": region,
    }
