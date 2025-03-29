import pytest
from datetime import datetime
from integrations.common.tests.base import base_setup

def test_domain_search(base_setup):
    """
    Tests domain search with required parameters
    """
    payload = {
        "domain": "hunter.io"
    }
    
    response = base_setup.post("/hunterio/domain_search", payload=payload)
    
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}. Response: {response.text}"
    )
    
    data = response.json().get("data", {})
    
    # Validate basic response structure
    assert "domain" in data, "Missing domain in response"
    assert "emails" in data, "Missing emails in response"
    assert isinstance(data["emails"], list), "Emails should be a list"

def test_domain_search_with_filters(base_setup):
    """
    Tests domain search with filters
    """
    payload = {
        "domain": "hunter.io",
        "limit": 5,
        "type": "personal",
        "department": "executive"
    }
    
    response = base_setup.post("/hunterio/domain_search", payload=payload)
    
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}. Response: {response.text}"
    )
    
    data = response.json().get("data", {})
    
    # Validate filtered response
    assert "domain" in data, "Missing domain in response"
    assert "emails" in data, "Missing emails in response"
    assert len(data["emails"]) <= 5, "Too many emails returned"

def test_email_finder(base_setup):
    """
    Tests email finder with required parameters
    """
    payload = {
        "domain": "stripe.com",
        "first_name": "Patrick",
        "last_name": "Collison"
    }
    
    response = base_setup.post("/hunterio/email_finder", payload=payload)
    
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}. Response: {response.text}"
    )
    
    data = response.json().get("data", {})
    
    # Validate basic response structure
    assert "email" in data, "Missing email in response"
    assert "first_name" in data, "Missing first_name in response"
    assert "last_name" in data, "Missing last_name in response"
    assert "score" in data, "Missing score in response"

def test_email_verifier(base_setup):
    """
    Tests email verifier with required parameters
    """
    payload = {
        "email": "patrick@stripe.com"
    }
    
    response = base_setup.post("/hunterio/email_verifier", payload=payload)
    
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}. Response: {response.text}"
    )
    
    data = response.json().get("data", {})
    
    # Validate basic response structure
    assert "email" in data, "Missing email in response"
    assert "status" in data, "Missing status in response"
    assert "score" in data, "Missing score in response"

def test_email_count(base_setup):
    """
    Tests email count with required parameters
    """
    payload = {
        "domain": "stripe.com"
    }
    
    response = base_setup.post("/hunterio/email_count", payload=payload)
    
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}. Response: {response.text}"
    )
    
    data = response.json().get("data", {})
    
    # Validate basic response structure
    assert "total" in data, "Missing total in response"
    assert "personal_emails" in data, "Missing personal_emails in response"
    assert "generic_emails" in data, "Missing generic_emails in response"

def test_email_enrichment(base_setup):
    """
    Tests email enrichment with required parameters
    """
    payload = {
        "email": "francois@hunter.io"
    }
    
    response = base_setup.post("/hunterio/email_enrichment", payload=payload)
    
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}. Response: {response.text}"
    )
    
    data = response.json().get("data", {})
    
    # Validate basic response structure
    assert "email" in data, "Missing email in response"
    assert "name" in data, "Missing name in response"

def test_company_enrichment(base_setup):
    """
    Tests company enrichment with required parameters
    """
    payload = {
        "domain": "hunter.io"
    }
    
    response = base_setup.post("/hunterio/company_enrichment", payload=payload)
    
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}. Response: {response.text}"
    )
    
    data = response.json().get("data", {})
    
    # Validate basic response structure
    assert "domain" in data, "Missing domain in response"

def test_combined_enrichment(base_setup):
    """
    Tests combined enrichment with required parameters
    """
    payload = {
        "email": "francois@hunter.io"
    }
    
    response = base_setup.post("/hunterio/combined_enrichment", payload=payload)
    
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}. Response: {response.text}"
    )
    
    data = response.json().get("data", {})
    
    # Validate basic response structure
    assert "person" in data, "Missing person in response"
    assert "company" in data, "Missing company in response"

def test_account_information(base_setup):
    """
    Tests account information endpoint
    """
    response = base_setup.post("/hunterio/account_information", payload={})
    
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}. Response: {response.text}"
    )
    
    data = response.json().get("data", {})
    
    # Validate basic response structure
    assert "email" in data, "Missing email in response"
    assert "plan_name" in data, "Missing plan_name in response" 