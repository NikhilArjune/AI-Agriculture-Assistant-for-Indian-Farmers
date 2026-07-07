import pytest
from tools.scheme_tool import check_eligibility


def test_eligible_small_farmer():
    scheme = {
        "scheme_name": "PM-KISAN",
        "target_states": [],
        "target_crops": [],
        "max_land_acres": 5.0,
        "min_land_acres": 0.0,
    }
    profile = {
        "location": {"state": "UP"},
        "farm_size_acres": 2.0,
        "primary_crops": ["wheat"],
    }
    result = check_eligibility(scheme, profile)
    assert result["eligible"] is True


def test_ineligible_large_farm():
    scheme = {
        "scheme_name": "Small Farmer Scheme",
        "target_states": [],
        "target_crops": [],
        "max_land_acres": 3.0,
        "min_land_acres": 0.0,
    }
    profile = {
        "location": {"state": "Punjab"},
        "farm_size_acres": 10.0,
        "primary_crops": ["wheat"],
    }
    result = check_eligibility(scheme, profile)
    assert result["eligible"] is False


def test_state_restricted_scheme():
    scheme = {
        "scheme_name": "Kerala Farmer Scheme",
        "target_states": ["Kerala"],
        "target_crops": [],
        "max_land_acres": None,
        "min_land_acres": None,
    }
    profile = {
        "location": {"state": "Punjab"},
        "farm_size_acres": 3.0,
        "primary_crops": ["wheat"],
    }
    result = check_eligibility(scheme, profile)
    assert result["eligible"] is False


def test_crop_restricted_scheme():
    scheme = {
        "scheme_name": "Cotton Subsidy",
        "target_states": [],
        "target_crops": ["cotton"],
        "max_land_acres": None,
        "min_land_acres": None,
    }
    profile = {
        "location": {"state": "Rajasthan"},
        "farm_size_acres": 5.0,
        "primary_crops": ["wheat", "maize"],
    }
    result = check_eligibility(scheme, profile)
    assert result["eligible"] is False
