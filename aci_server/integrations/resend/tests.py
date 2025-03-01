from integrations.common.tests.base import base_setup
import pytest
from datetime import datetime, timedelta
import time

#########################################
# Resend Integration Tests
#########################################

# --- Email Lifecycle Tests ---
@pytest.fixture(scope="module")
def email_payload():
    one_minute_from_now = (datetime.now() + timedelta(minutes=1)).isoformat()

    return {
        "from": "onboarding@resend.dev",
        "to": "veyraxservice@gmail.com",
        "subject": "[Test] Resend Email",
        "text": "This is a test email from Resend",
        "scheduled_at": one_minute_from_now
    }

@pytest.fixture(scope="module")
def created_email(base_setup, email_payload):
    # Create scheduled email
    response = base_setup.post("/resend/send_email", payload=email_payload)
    data = response.json()["data"]
    email_id = data.get("id")
    assert email_id, "Email ID not found in response"
    
    yield email_id

    # Cleanup: Cancel email if still exists
    try:
        base_setup.post("/resend/cancel_email", payload={"email_id": email_id})
    except Exception:
        pass

def test_send_email(created_email):
    assert created_email, "Email creation failed"

def test_get_email(base_setup, created_email):
    response = base_setup.post("/resend/get_email", payload={"email_id": created_email})
    assert response.status_code == 200
    assert response.json()["data"]["id"] == created_email

def test_update_email(base_setup, created_email):
    two_minute_from_now = (datetime.now() + timedelta(minutes=2)).isoformat()
    payload = {
        "email_id": created_email,
        "scheduled_at": two_minute_from_now
    }
    response = base_setup.post("/resend/update_email", payload=payload)
    assert response.status_code == 200

def test_cancel_email(base_setup, created_email):
    response = base_setup.post("/resend/cancel_email", payload={"email_id": created_email})
    assert response.status_code == 200

# --- Domain Lifecycle Tests ---
@pytest.fixture(scope="module")
def domain_payload():
    return {
        "name": "example.com",
        "region": "us-east-1"
    }

@pytest.fixture(scope="module")
def created_domain(base_setup, domain_payload):
    response = base_setup.post("/resend/create_domain", payload=domain_payload)
    data = response.json()["data"]
    domain_id = data.get("id")
    assert domain_id, "Domain ID not found in response"
    
    # Wait for domain to be provisioned
    time.sleep(5)  # Add short delay for domain setup
    
    yield domain_id

    # Cleanup: Delete domain
    try:
        base_setup.post("/resend/delete_domain", payload={"domain_id": domain_id})
    except AssertionError as e:
        if "404" not in str(e):  # Ignore not found errors
            raise
    except Exception:
        pass

def test_create_domain(created_domain):
    assert created_domain, "Domain creation failed"

def test_get_domain(base_setup, created_domain):
    response = base_setup.post("/resend/get_domain", payload={"domain_id": created_domain})
    assert response.status_code == 200
    assert response.json()["data"]["id"] == created_domain

def test_list_domains(base_setup, created_domain):
    response = base_setup.post("/resend/list_domains")
    assert response.status_code == 200
    domains = response.json()["data"]["data"]
    assert any(d["id"] == created_domain for d in domains)

def test_delete_domain(base_setup, created_domain):
    # Delete the created domain
    response = base_setup.post("/resend/delete_domain", payload={"domain_id": created_domain})
    assert response.status_code == 200

# --- API Key Lifecycle Tests ---
@pytest.fixture(scope="module")
def api_key_payload():
    return {
        "name": "Test API Key",
        "permission": "full_access"
    }

@pytest.fixture(scope="module")
def created_api_key(base_setup, api_key_payload):
    response = base_setup.post("/resend/create_api_key", payload=api_key_payload)
    data = response.json()["data"]
    api_key_id = data.get("id")
    assert api_key_id, "API Key ID not found in response"
    
    yield api_key_id

    # Cleanup: Delete API key
    try:
        base_setup.post("/resend/delete_api_key", payload={"api_key_id": api_key_id})
    except Exception:
        pass

def test_create_api_key(created_api_key):
    assert created_api_key, "API Key creation failed"

def test_list_api_keys(base_setup, created_api_key):
    response = base_setup.post("/resend/list_api_keys")
    assert response.status_code == 200
    api_keys = response.json()["data"]["data"]
    assert any(k["id"] == created_api_key for k in api_keys)

def test_delete_api_key(base_setup, created_api_key):
    response = base_setup.post("/resend/delete_api_key", payload={"api_key_id": created_api_key})
    assert response.status_code == 200

# --- Broadcast Lifecycle Tests ---
@pytest.fixture(scope="module")
def broadcast_payload(base_setup):
    # Create required audience first
    audience_response = base_setup.post("/resend/create_audience", payload={"name": "Test Audience"})
    audience_id = audience_response.json()["data"]["id"]

    return {
        "audience_id": audience_id,
        "from": "onboarding@resend.dev",
        "subject": "Test Broadcast",
        "html": "<p>Test content</p>"
    }

@pytest.fixture(scope="module")
def created_broadcast(base_setup, broadcast_payload):
    response = base_setup.post("/resend/create_broadcast", payload=broadcast_payload)
    data = response.json()["data"]
    broadcast_id = data.get("id")
    assert broadcast_id, "Broadcast ID not found in response"
    
    yield broadcast_id

    # Cleanup: Delete broadcast
    try:
        base_setup.post("/resend/delete_broadcast", payload={"broadcast_id": broadcast_id})
    except Exception:
        pass

def test_create_broadcast(created_broadcast):
    assert created_broadcast, "Broadcast creation failed"

def test_get_broadcast(base_setup, created_broadcast):
    response = base_setup.post("/resend/get_broadcast", payload={"broadcast_id": created_broadcast})
    assert response.status_code == 200
    assert response.json()["data"]["id"] == created_broadcast

def test_list_broadcasts(base_setup, created_broadcast):
    response = base_setup.post("/resend/list_broadcasts")
    assert response.status_code == 200
    broadcasts = response.json()["data"]["data"]
    assert any(b["id"] == created_broadcast for b in broadcasts)

# --- Audience Lifecycle Tests ---
@pytest.fixture(scope="module")
def audience_payload():
    return {"name": "Test Audience"}

@pytest.fixture(scope="module")
def created_audience(base_setup, audience_payload):
    response = base_setup.post("/resend/create_audience", payload=audience_payload)
    data = response.json()["data"]
    audience_id = data.get("id")
    assert audience_id, "Audience ID not found in response"
    
    yield audience_id

    # Cleanup: Delete audience
    try:
        base_setup.post("/resend/delete_audience", payload={"audience_id": audience_id})
    except Exception:
        pass

def test_create_audience(created_audience):
    assert created_audience, "Audience creation failed"

def test_list_audiences(base_setup, created_audience):
    response = base_setup.post("/resend/list_audiences")
    assert response.status_code == 200
    audiences = response.json()["data"]["data"]
    assert any(a["id"] == created_audience for a in audiences)

# --- Contact Lifecycle Tests ---
@pytest.fixture(scope="module")
def contact_payload(base_setup):
    # Create audience first
    audience_response = base_setup.post("/resend/create_audience", payload={"name": "Contact Test Audience"})
    audience_id = audience_response.json()["data"]["id"]

    return {
        "audienceId": audience_id,
        "email": "veyraxservice@gmail.com",
        "firstName": "Test",
        "lastName": "User"
    }

@pytest.fixture(scope="module")
def created_contact(base_setup, contact_payload):
    response = base_setup.post("/resend/create_contact", payload=contact_payload)
    data = response.json()["data"]
    contact_id = data.get("id")
    assert contact_id, "Contact ID not found in response"
    
    yield {
        "contact_id": contact_id,
        "audience_id": contact_payload["audienceId"]
    }

    # Cleanup: Delete contact
    try:
        base_setup.post("/resend/delete_contact", payload={
            "audienceId": contact_payload["audienceId"],
            "id": contact_id
        })
    except Exception:
        pass

def test_create_contact(created_contact):
    assert created_contact["contact_id"], "Contact creation failed"

def test_list_contacts(base_setup, created_contact):
    response = base_setup.post("/resend/list_contacts", payload={
        "audienceId": created_contact["audience_id"]
    })
    assert response.status_code == 200
    contacts = response.json()["data"]["data"]
    assert any(c["id"] == created_contact["contact_id"] for c in contacts) 