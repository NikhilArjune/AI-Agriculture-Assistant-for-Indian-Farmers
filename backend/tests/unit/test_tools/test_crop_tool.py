import pytest
from tools.crop_tool import get_crop_calendar


def test_wheat_north_india():
    result = get_crop_calendar.invoke({"crop_name": "wheat", "state": "Punjab"})
    assert "sowing_window" in result
    assert "harvest_window" in result
    assert "varieties" in result
    assert len(result["varieties"]) > 0
    assert "Oct" in result["sowing_window"] or "Nov" in result["sowing_window"]


def test_rice_south_india():
    result = get_crop_calendar.invoke({"crop_name": "rice", "state": "Tamil Nadu"})
    assert "sowing_window" in result
    assert isinstance(result["varieties"], list)


def test_unknown_crop():
    result = get_crop_calendar.invoke({"crop_name": "unknowncrop999", "state": "UP"})
    assert "error" in result


def test_case_insensitive():
    result_lower = get_crop_calendar.invoke({"crop_name": "wheat", "state": "Haryana"})
    result_upper = get_crop_calendar.invoke({"crop_name": "WHEAT", "state": "Haryana"})
    assert result_lower["sowing_window"] == result_upper["sowing_window"]


def test_maize_returns_data():
    result = get_crop_calendar.invoke({"crop_name": "maize", "state": "Maharashtra"})
    assert "sowing_window" in result
    assert "error" not in result
