import pytest
from datetime import datetime
from integrations.common.tests.base import base_setup

def test_forecast_valid_params(base_setup):
    """
    Tests the forecast endpoint with valid city and country parameters
    """
    payload = {
        "city": "London",
        "country": "GB"
    }
    
    response = base_setup.post("/weather/forecast", payload=payload)
    
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}. Response: {response.text}"
    )
    
    data = response.json().get("data", {})
    component = response.json().get("component", {})
    
    # Validate basic response structure
    assert "city_name" in data, "Missing city_name in response"
    assert "country" in data, "Missing country in response"
    assert "forecast" in data, "Missing forecast items in response"
    
    # Validate forecast items structure
    if data["forecast"]:
        first_item = data["forecast"][0]
        assert "date" in first_item, "Missing date in forecast item"
        assert "temperature" in first_item, "Missing temperature in forecast item"
        assert "description" in first_item, "Missing description in forecast item"
