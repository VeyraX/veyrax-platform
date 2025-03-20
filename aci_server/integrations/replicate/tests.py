import pytest
from datetime import datetime
from integrations.common.tests.base import base_setup

def test_basic_prediction(base_setup):
    """
    Tests basic prediction with required parameters only
    """
    payload = {
        "version": "5c7d5dc6dd8bf75c1acaa8565735e7986bc5b66206b55cca93cb72c9bf15ccaa",
        "input": {
            "text": "Hello world!"
        }
    }
    
    response = base_setup.post("/replicate/predictions", payload=payload)
    
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}. Response: {response.text}"
    )
    
    data = response.json().get("data", {})
    
    # Validate basic response structure
    assert "id" in data, "Missing id in response"
    assert "model" in data, "Missing model in response"
    assert "version" in data, "Missing version in response"
    assert "input" in data, "Missing input in response"
    assert "urls" in data, "Missing urls in response"
    assert "status" in data, "Missing status in response"

def test_prediction_with_advanced_params(base_setup):
    """
    Tests prediction with advanced parameters
    """
    payload = {
        "version": "5c7d5dc6dd8bf75c1acaa8565735e7986bc5b66206b55cca93cb72c9bf15ccaa",
        "input": {
            "text": "Hello world!"
        },
        "webhook": "https://example.com/webhook",
        "webhook_events_filter": ["start", "completed"],
        "stream": True
    }
    
    response = base_setup.post("/replicate/predictions", payload=payload)
    
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}. Response: {response.text}"
    )
    
    data = response.json().get("data", {})
    
    # Validate URLs in response
    assert "urls" in data, "Missing urls in response"
    urls = data.get("urls", {})
    assert "get" in urls, "Missing get URL in response"
    assert "cancel" in urls, "Missing cancel URL in response"
    
    # Stream URL may or may not be present depending on the model capability
    if "stream" in urls:
        assert urls["stream"], "Stream URL is empty"

def test_deployment_prediction(base_setup):
    """
    Tests prediction using a deployment
    """
    payload = {
        "input": {
            "prompt": "A photo of a cat riding a skateboard"
        }
    }
    
    deployment_owner = "acme"
    deployment_name = "my-app-image-generator"
    
    response = base_setup.post(f"/replicate/deployments/{deployment_owner}/{deployment_name}/predictions", payload=payload)
    
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}. Response: {response.text}"
    )
    
    data = response.json().get("data", {})
    
    # Validate basic response structure
    assert "id" in data, "Missing id in response"
    assert "model" in data, "Missing model in response"
    assert "version" in data, "Missing version in response"
    assert "input" in data, "Missing input in response"
    assert "urls" in data, "Missing urls in response"
    assert "status" in data, "Missing status in response"
    assert "deployment" in data, "Missing deployment in response"

def test_official_model_prediction(base_setup):
    """
    Tests prediction using an official model
    """
    payload = {
        "input": {
            "prompt": "Write a short poem about the weather."
        }
    }
    
    model_owner = "meta"
    model_name = "meta-llama-3-70b-instruct"
    
    response = base_setup.post(f"/replicate/models/{model_owner}/{model_name}/predictions", payload=payload)
    
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}. Response: {response.text}"
    )
    
    data = response.json().get("data", {})
    
    # Validate basic response structure
    assert "id" in data, "Missing id in response"
    assert "model" in data, "Missing model in response"
    assert "version" in data, "Missing version in response"
    assert "input" in data, "Missing input in response"
    assert "urls" in data, "Missing urls in response"
    assert "status" in data, "Missing status in response"
    
    # For official models, version should be "hidden"
    assert data.get("version") == "hidden", "Version should be 'hidden' for official models"

def test_get_prediction(base_setup):
    """
    Tests retrieving a prediction by ID
    """
    # First create a prediction
    payload = {
        "version": "5c7d5dc6dd8bf75c1acaa8565735e7986bc5b66206b55cca93cb72c9bf15ccaa",
        "input": {
            "text": "Hello world!"
        }
    }
    
    create_response = base_setup.post("/replicate/predictions", payload=payload)
    prediction_id = create_response.json().get("data", {}).get("id")
    
    # Now get the prediction
    response = base_setup.get(f"/replicate/predictions/{prediction_id}")
    
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}. Response: {response.text}"
    )
    
    data = response.json().get("data", {})
    
    # Validate ID matches
    assert data.get("id") == prediction_id, f"Prediction ID mismatch: expected {prediction_id}, got {data.get('id')}"

def test_cancel_prediction(base_setup):
    """
    Tests canceling a prediction
    """
    # First create a prediction
    payload = {
        "version": "5c7d5dc6dd8bf75c1acaa8565735e7986bc5b66206b55cca93cb72c9bf15ccaa",
        "input": {
            "text": "Hello world!"
        }
    }
    
    create_response = base_setup.post("/replicate/predictions", payload=payload)
    prediction_id = create_response.json().get("data", {}).get("id")
    
    # Now cancel the prediction
    response = base_setup.post(f"/replicate/predictions/{prediction_id}/cancel")
    
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}. Response: {response.text}"
    )
    
    data = response.json().get("data", {})
    
    # The status may be "canceled" or still in a transition state
    # depending on how quickly the API processes the cancel request
    assert data.get("id") == prediction_id, f"Prediction ID mismatch: expected {prediction_id}, got {data.get('id')}" 