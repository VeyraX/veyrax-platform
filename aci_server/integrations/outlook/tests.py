from integrations.common.tests.base import base_setup
import pytest

#########################################
# Outlook Integration Tests
#########################################

# --- Message Lifecycle Fixtures ---
@pytest.fixture(scope="module")
def draft_payload():
    return {
        "to_recipients": ["test@example.com"],
        "subject": "[TEST] Outlook Draft",
        "body": "Test draft content"
    }

@pytest.fixture(scope="module")
def created_draft(base_setup, draft_payload):
    response = base_setup.post("/outlook/create_draft", payload={"draft_args": draft_payload})
    data = response.json()["data"]
    message_id = data.get("id")
    assert message_id, "No message ID in draft response"
    yield message_id
    
    # Cleanup
    try:
        base_setup.post("/outlook/delete_message", payload={"message_id": message_id})
    except Exception:
        pass

# --- Calendar Event Fixtures ---
@pytest.fixture(scope="module")
def event_payload():
    return {
        "subject": "Test Event",
        "start": {"dateTime": "2025-01-01T09:00:00Z", "timeZone": "UTC"},
        "end": {"dateTime": "2025-01-01T10:00:00Z", "timeZone": "UTC"}
    }

@pytest.fixture(scope="module")
def created_event(base_setup, event_payload):
    response = base_setup.post("/outlook/create_event", payload={"event": event_payload})
    data = response.json()["data"]
    event_id = data.get("id")
    assert event_id, "No event ID in creation response"
    yield event_id
    
    # Cleanup
    try:
        base_setup.post("/outlook/delete_event", payload={"event_id": event_id})
    except Exception:
        pass

#########################################
# Basic Health Checks
#########################################
def test_get_messages_health(base_setup):
    response = base_setup.post("/outlook/get_messages", payload={"filters": {"max_results": 1}})
    assert response.status_code == 200

def test_list_calendars_health(base_setup):
    response = base_setup.post("/outlook/list_calendars")
    assert response.status_code == 200

#########################################
# Message Lifecycle Tests
#########################################
def test_create_draft(created_draft):
    assert created_draft, "Draft creation failed"

def test_get_draft(base_setup, created_draft):
    response = base_setup.post("/outlook/get_message", payload={"message_id": created_draft})
    data = response.json()["data"]
    assert data["id"] == created_draft

def test_delete_draft(base_setup, created_draft):
    response = base_setup.post("/outlook/delete_message", payload={"message_id": created_draft})
    assert response.status_code == 200

#########################################
# Calendar Event Lifecycle Tests  
#########################################
def test_create_event(created_event):
    assert created_event, "Event creation failed"

def test_get_event(base_setup, created_event):
    response = base_setup.post("/outlook/get_event", payload={"event_id": created_event})
    data = response.json()["data"]
    assert data["id"] == created_event

def test_update_event(base_setup, created_event):
    update_payload = {
        "subject": "Updated Event",
        "start": {"dateTime": "2025-01-01T09:30:00Z", "timeZone": "UTC"}
    }
    response = base_setup.post("/outlook/update_event", payload={
        "event_id": created_event,
        "event_update": update_payload
    })
    assert response.status_code == 200

def test_list_events(base_setup, created_event):
    response = base_setup.post("/outlook/list_events", payload={
        "filters": {
            "after_date": "2025-01-01T08:00:00Z",
            "before_date": "2025-01-01T11:00:00Z"
        }
    })
    events = response.json()["data"].get("events", [])
    assert any(e["id"] == created_event for e in events)

def test_delete_event(base_setup, created_event):
    response = base_setup.post("/outlook/delete_event", payload={"event_id": created_event})
    assert response.status_code == 200 