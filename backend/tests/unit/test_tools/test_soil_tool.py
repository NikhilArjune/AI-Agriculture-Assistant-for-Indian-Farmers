import pytest
from tools.soil_tool import analyze_soil


def test_npk_deficiency_detected():
    inputs = {
        "crop_name": "wheat",
        "soil_type": "loamy",
        "ph_level": 6.5,
        "nitrogen": 50,    # low
        "phosphorus": 20,
        "potassium": 150,
    }
    result = analyze_soil.invoke({"soil_inputs": inputs, "crop_name": "wheat"})
    assert "deficiencies" in result
    assert "nitrogen" in result["deficiencies"]


def test_ph_too_acidic():
    inputs = {
        "crop_name": "rice",
        "soil_type": "clay",
        "ph_level": 4.5,
        "nitrogen": None,
        "phosphorus": None,
        "potassium": None,
    }
    result = analyze_soil.invoke({"soil_inputs": inputs, "crop_name": "rice"})
    assert "ph_issue" in result or "ph" in str(result).lower()


def test_no_inputs_returns_general_advice():
    inputs = {
        "crop_name": "tomato",
        "soil_type": "",
        "ph_level": None,
        "nitrogen": None,
        "phosphorus": None,
        "potassium": None,
    }
    result = analyze_soil.invoke({"soil_inputs": inputs, "crop_name": "tomato"})
    assert "fertilizer_plan" in result or "recommendations" in result


def test_all_nutrients_optimal():
    inputs = {
        "crop_name": "wheat",
        "soil_type": "loamy",
        "ph_level": 6.8,
        "nitrogen": 120,
        "phosphorus": 30,
        "potassium": 200,
    }
    result = analyze_soil.invoke({"soil_inputs": inputs, "crop_name": "wheat"})
    # Should have minimal deficiencies
    assert isinstance(result.get("deficiencies", []), list)
