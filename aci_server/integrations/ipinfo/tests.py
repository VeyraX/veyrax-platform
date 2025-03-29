import pytest
from integrations.common.tests.base import base_setup

def test_get_ip_info(base_setup):
    """
    Tests retrieving information for a specific IP address
    """
    payload = {
        "ip_address": "8.8.8.8"
    }
    
    response = base_setup.post("/ipinfo/get_ip_info", payload=payload)
    
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}. Response: {response.text}"
    )
    
    data = response.json().get("data", {})
    
    # Validate basic response structure
    assert "ip" in data, "Missing ip in response"
    assert data["ip"] == "8.8.8.8", "Incorrect IP address in response"
    assert "country" in data, "Missing country in response"

def test_get_ip_info_no_address(base_setup):
    """
    Tests retrieving information for the caller's IP (no IP specified)
    """
    payload = {}
    
    response = base_setup.post("/ipinfo/get_ip_info", payload=payload)
    
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}. Response: {response.text}"
    )
    
    data = response.json().get("data", {})
    
    # Validate basic response structure
    assert "ip" in data, "Missing ip in response"
    assert "country" in data, "Missing country in response"

def test_get_bulk_info(base_setup):
    """
    Tests retrieving information for multiple IP addresses
    """
    payload = {
        "ip_addresses": ["8.8.8.8", "1.1.1.1"]
    }
    
    response = base_setup.post("/ipinfo/get_bulk_info", payload=payload)
    
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}. Response: {response.text}"
    )
    
    data = response.json().get("data", {})
    
    # Validate basic response structure
    assert "items" in data, "Missing items in response"
    items = data.get("items", {})
    assert "8.8.8.8" in items, "Missing 8.8.8.8 in response items"
    assert "1.1.1.1" in items, "Missing 1.1.1.1 in response items"
    assert items["8.8.8.8"]["ip"] == "8.8.8.8", "Incorrect IP address in response"

def test_get_asn_info(base_setup):
    """
    Tests retrieving information for an ASN
    """
    payload = {
        "asn": "AS15169"
    }
    
    response = base_setup.post("/ipinfo/get_asn_info", payload=payload)
    
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}. Response: {response.text}"
    )
    
    data = response.json().get("data", {})
    
    # Validate basic response structure
    assert "asn" in data, "Missing asn in response"
    assert data["asn"] == "AS15169", "Incorrect ASN in response"
    assert "name" in data, "Missing name in response"
    assert "country" in data, "Missing country in response" 