import pytest
from datetime import datetime
from integrations.common.tests.base import base_setup

def test_basic_completion(base_setup):
    """
    Tests basic completion with required parameters only
    """
    payload = {
        "messages": [{"role": "user", "content": "What is AI?"}],
        "model": "sonar"
    }
    
    response = base_setup.post("/perplexity/create_completion", payload=payload)
    
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}. Response: {response.text}"
    )
    
    data = response.json().get("data", {})
    
    # Validate basic response structure
    assert "id" in data, "Missing id in response"
    assert "model" in data, "Missing model in response"
    assert "choices" in data, "Missing choices in response"
    assert "usage" in data, "Missing usage in response"

def test_full_parameters_completion(base_setup):
    """
    Tests completion with all available parameters
    """
    payload = {
        "messages": [{"role": "user", "content": "Explain quantum computing"}],
        "model": "sonar",
        "max_tokens": 500,
        "temperature": 0.7,
        "top_p": 0.95,
        # "search_domain_filter": "academic", # only available in certain tiers
        "return_images": True,
        "return_related_questions": True,
        "top_k": 3,
        "stream": False
    }
    
    response = base_setup.post("/perplexity/create_completion", payload=payload)
    
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}. Response: {response.text}"
    )
    
    data = response.json().get("data", {})
    
    # Validate extended response structure
    assert "citations" in data, "Missing citations in response"
    assert isinstance(data["choices"], list), "Choices should be a list"
    if data.get("citations"):
        assert isinstance(data["citations"], list), "Citations should be a list"
