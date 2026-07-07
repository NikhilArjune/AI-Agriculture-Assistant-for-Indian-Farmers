import logging

from langchain_core.tools import tool

logger = logging.getLogger(__name__)

# NPK optimal ranges per crop (simplified lookup)
_CROP_NPK_RANGES: dict[str, dict] = {
    "wheat":     {"N": (120, 150), "P": (60, 80),  "K": (40, 60)},
    "rice":      {"N": (100, 120), "P": (50, 60),  "K": (50, 60)},
    "maize":     {"N": (150, 180), "P": (70, 90),  "K": (60, 80)},
    "cotton":    {"N": (100, 120), "P": (50, 60),  "K": (50, 60)},
    "sugarcane": {"N": (250, 300), "P": (80, 100), "K": (100, 120)},
    "tomato":    {"N": (120, 150), "P": (60, 80),  "K": (80, 100)},
    "potato":    {"N": (150, 180), "P": (80, 100), "K": (100, 120)},
    "default":   {"N": (100, 120), "P": (50, 60),  "K": (40, 60)},
}


@tool
def analyze_soil(soil_inputs: dict, crop_name: str = "") -> dict:
    """Analyze soil inputs and identify deficiencies against crop-specific requirements.

    Args:
        soil_inputs: Dict with keys: ph, nitrogen, phosphorus, potassium, moisture.
        crop_name: Primary crop name for targeted recommendation.

    Returns:
        Dict with: ph_status, deficiencies, recommendations.
    """
    ph = float(soil_inputs.get("ph", 7.0))
    n = float(soil_inputs.get("nitrogen", 0))
    p = float(soil_inputs.get("phosphorus", 0))
    k = float(soil_inputs.get("potassium", 0))

    crop_key = crop_name.lower() if crop_name.lower() in _CROP_NPK_RANGES else "default"
    optimal = _CROP_NPK_RANGES[crop_key]

    deficiencies = []
    recommendations = []

    # pH analysis
    if ph < 5.5:
        ph_status = "acidic"
        recommendations.append("Apply agricultural lime at 2–4 tonnes/hectare to raise pH.")
    elif ph > 8.0:
        ph_status = "alkaline"
        recommendations.append("Apply gypsum at 2–3 tonnes/hectare to lower pH.")
    else:
        ph_status = "optimal"

    # NPK deficiency check
    for nutrient, value, key in [("Nitrogen", n, "N"), ("Phosphorus", p, "P"), ("Potassium", k, "K")]:
        low, _ = optimal[key]
        if value < low * 0.7:
            deficiencies.append(f"{nutrient} (current: {value}, optimal: {low}+ kg/ha)")
            if key == "N":
                recommendations.append(f"Apply Urea at 45–50 kg/acre or DAP for nitrogen.")
            elif key == "P":
                recommendations.append(f"Apply SSP (Single Super Phosphate) at 25–30 kg/acre.")
            elif key == "K":
                recommendations.append(f"Apply MOP (Muriate of Potash) at 20–25 kg/acre.")

    logger.debug("SoilTool: crop=%s deficiencies=%s", crop_name, deficiencies)

    return {
        "ph": ph,
        "ph_status": ph_status,
        "deficiencies": deficiencies,
        "recommendations": recommendations,
        "crop_optimal_npk": optimal,
    }
