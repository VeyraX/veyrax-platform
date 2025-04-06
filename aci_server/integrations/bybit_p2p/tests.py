import pytest
from integrations.common.tests.base import base_setup
import os

def test_get_p2p_offers_sell(base_setup):
    """
    Tests retrieving USDT sell offers in UAH
    """
    payload = {
        "fiat": "uah",
        "crypto": "usdt",
        "trade_type": "sell",
        "page": 1
    }
    
    response = base_setup.post("/bybit_p2p/get_p2p_offers", payload=payload)
    
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}. Response: {response.text}"
    )
    
    data = response.json().get("data", {})
    
    # Validate basic response structure
    assert "offers" in data, "Missing offers in response"
    assert isinstance(data["offers"], list), "Offers should be a list"
    
    if len(data["offers"]) > 0:
        offer = data["offers"][0]
        assert "exchange" in offer, "Missing exchange in offer"
        assert "order_id" in offer, "Missing order_id in offer"
        assert "trade_type" in offer, "Missing trade_type in offer"
        assert "price" in offer, "Missing price in offer"
        assert "trader" in offer, "Missing trader in offer"

def test_get_p2p_offers_buy(base_setup):
    """
    Tests retrieving USDT buy offers in USD
    """
    payload = {
        "fiat": "usd",
        "crypto": "usdt",
        "trade_type": "buy",
        "page": 1
    }
    
    response = base_setup.post("/bybit_p2p/get_p2p_offers", payload=payload)
    
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}. Response: {response.text}"
    )
    
    data = response.json().get("data", {})
    
    # Validate basic response structure
    assert "offers" in data, "Missing offers in response"
    assert isinstance(data["offers"], list), "Offers should be a list"
    
    if len(data["offers"]) > 0:
        offer = data["offers"][0]
        assert "exchange" in offer, "Missing exchange in offer"
        assert "order_id" in offer, "Missing order_id in offer"
        assert "trade_type" in offer, "Missing trade_type in offer"
        assert "price" in offer, "Missing price in offer"
        assert "trader" in offer, "Missing trader in offer"

def test_validate_key(base_setup):
    """
    Tests the key validation endpoint
    """
    # Test with invalid key
    payload = {
        "api_key": "invalid_key_12345"
    }
    
    response = base_setup.post("/bybit_p2p/validate_key", payload=payload)
    
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}. Response: {response.text}"
    )
    
    data = response.json()
    
    assert "valid" in data, "Missing valid field in response"
    assert data["valid"] is False, "API key should be invalid"
    
    # Test with valid key (if available in environment)
    api_key = os.environ.get("RAPIDAPI_KEY")
    if api_key:
        payload = {
            "api_key": api_key
        }
        
        response = base_setup.post("/bybit_p2p/validate_key", payload=payload)
        
        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}. Response: {response.text}"
        )
        
        data = response.json()
        
        assert "valid" in data, "Missing valid field in response" 