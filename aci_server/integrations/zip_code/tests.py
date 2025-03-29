import pytest
from datetime import datetime
from integrations.common.tests.base import base_setup

def test_get_by_zipcode(base_setup):
    """
    Tests getting location information by zipcode
    """
    payload = {
        "country": "US",
        "postal_code": "90210"
    }
    
    response = base_setup.post("/zip_code/get_by_zipcode", payload=payload)
    
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}. Response: {response.text}"
    )
    
    data = response.json().get("data", {})
    
    # Validate basic response structure
    assert "post code" in data, "Missing post code in response"
    assert "country" in data, "Missing country in response"
    assert "country abbreviation" in data, "Missing country abbreviation in response"
    assert "places" in data, "Missing places in response"
    
    # Validate Beverly Hills data
    assert data["post code"] == "90210", "Wrong post code"
    assert data["country"] == "United States", "Wrong country"
    assert data["country abbreviation"] == "US", "Wrong country abbreviation"
    assert len(data["places"]) > 0, "No places returned"
    assert data["places"][0]["place name"] == "Beverly Hills", "Wrong place name"
    assert data["places"][0]["state"] == "California", "Wrong state"
    assert data["places"][0]["state abbreviation"] == "CA", "Wrong state abbreviation"

def test_get_by_city(base_setup):
    """
    Tests getting zipcode information by city name
    """
    payload = {
        "country": "US",
        "state": "MA",
        "city": "Belmont"
    }
    
    response = base_setup.post("/zip_code/get_by_city", payload=payload)
    
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}. Response: {response.text}"
    )
    
    data = response.json().get("data", {})
    
    # Validate basic response structure
    assert "places" in data, "Missing places in response"
    assert "country" in data, "Missing country in response"
    assert "country abbreviation" in data, "Missing country abbreviation in response"
    
    # Validate Belmont data
    assert data["country"] == "United States", "Wrong country"
    assert data["country abbreviation"] == "US", "Wrong country abbreviation"
    assert len(data["places"]) > 0, "No places returned"
    
    place_names = [place["place name"] for place in data["places"]]
    assert "Belmont" in place_names, "Belmont not found in places"
    
    states = [place["state"] for place in data["places"]]
    assert "Massachusetts" in states, "Massachusetts not found in states"

def test_invalid_zipcode(base_setup):
    """
    Tests handling of invalid zipcode
    """
    payload = {
        "country": "US",
        "postal_code": "99999999"  # Invalid zipcode
    }
    
    response = base_setup.post("/zip_code/get_by_zipcode", payload=payload)
    
    # API should return 404 for invalid zipcodes
    assert response.status_code == 404, (
        f"Expected 404 for invalid zipcode, got {response.status_code}"
    )

def test_invalid_country(base_setup):
    """
    Tests handling of invalid country code
    """
    payload = {
        "country": "ZZ",  # Invalid country code
        "postal_code": "90210"
    }
    
    response = base_setup.post("/zip_code/get_by_zipcode", payload=payload)
    
    # API should return 404 for invalid country codes
    assert response.status_code == 404, (
        f"Expected 404 for invalid country code, got {response.status_code}"
    ) 