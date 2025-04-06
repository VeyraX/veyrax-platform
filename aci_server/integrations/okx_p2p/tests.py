import pytest
import os
from ..common.tests import base_setup

# Test getting USDT sell offers in UAH
def test_get_p2p_offers_sell():
    response = base_setup.client.post(
        "/okx_p2p/get_p2p_offers",
        json={
            "fiat_currency": "uah",
            "crypto_currency": "usdt",
            "trade_type": "sell",
            "page": 1
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Validate response structure
    assert "data" in data
    assert "offers" in data["data"]
    assert isinstance(data["data"]["offers"], list)
    
    # If we have any offers, validate their structure
    if data["data"]["offers"]:
        first_offer = data["data"]["offers"][0]
        assert "order_id" in first_offer
        assert "price" in first_offer
        assert "available_amount" in first_offer
        assert "trader" in first_offer
        assert "payment_methods" in first_offer

# Test getting USDT buy offers in USD
def test_get_p2p_offers_buy():
    response = base_setup.client.post(
        "/okx_p2p/get_p2p_offers",
        json={
            "fiat_currency": "usd",
            "crypto_currency": "usdt",
            "trade_type": "buy",
            "page": 1
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Validate response structure
    assert "data" in data
    assert "offers" in data["data"]
    assert isinstance(data["data"]["offers"], list)
    
    # If we have any offers, validate their structure
    if data["data"]["offers"]:
        first_offer = data["data"]["offers"][0]
        assert "order_id" in first_offer
        assert "price" in first_offer
        assert "available_amount" in first_offer
        assert "trader" in first_offer
        assert "payment_methods" in first_offer

# Test API key validation
def test_validate_key():
    # Test with an invalid key
    response = base_setup.client.post(
        "/okx_p2p/validate_key",
        json={"api_key": "invalid_key_for_testing"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "valid" in data
    assert data["valid"] is False
    
    # Test with a valid key if we have one in environment
    api_key = os.environ.get("RAPIDAPI_KEY")
    if api_key:
        response = base_setup.client.post(
            "/okx_p2p/validate_key",
            json={"api_key": api_key}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "valid" in data
        assert data["valid"] is True 