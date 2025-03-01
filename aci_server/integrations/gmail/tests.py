from integrations.common.tests.base import base_setup
import pytest

#########################################
# Gmail Integration Tests
#########################################

# --- Gmail: Draft & Message Lifecycle ---

# Fixture providing a valid payload for creating a draft.
@pytest.fixture(scope="module")
def draft_payload():
    return {
        "recipient": "veyraxservice@gmail.com",
        "subject": "[Automatic Test] Draft Message",
        "body": "This is a test draft message"
    }

# Fixture to create and manage a test draft for draft lifecycle tests.
@pytest.fixture(scope="module")
def created_draft(base_setup, draft_payload):
    # Create draft via /gmail/create_draft.
    response = base_setup.post("/gmail/create_draft", payload={"draft_args": draft_payload})
    draft_data = response.json()["data"]

    # Correct extraction:
    draft_id = draft_data.get("draft_id")
    message_id = draft_data.get("id")
    
    assert draft_id, "Draft ID not found in create_draft response."
    assert message_id, "Message ID not found in create_draft response."
    
    yield {"draft_id": draft_id, "message_id": message_id}

    # Cleanup: attempt to delete the draft if still present.
    try:
        base_setup.post("/gmail/delete_draft", payload={"draft_id": draft_id})
    except Exception:
        pass

# New fixture to create a separate draft for sending messages.
@pytest.fixture(scope="module")
def draft_for_send(base_setup, draft_payload):
    response = base_setup.post("/gmail/create_draft", payload={"draft_args": draft_payload})
    draft_data = response.json()["data"]

    draft_id = draft_data.get("draft_id")
    message_id = draft_data.get("id")
    
    assert draft_id, "Draft ID not found in create_draft response for send."
    assert message_id, "Message ID not found in create_draft response for send."
    
    yield {"draft_id": draft_id, "message_id": message_id}

    # Cleanup: attempt to delete the draft if still present.
    try:
        base_setup.post("/gmail/delete_draft", payload={"draft_id": draft_id})
    except Exception:
        pass

# Health check endpoints.
def test_get_messages_health(base_setup):
    # Verify /gmail/get_messages returns a valid response.
    base_setup.post('/gmail/get_messages', payload={"filters": {"max_results": 1}})

def test_get_drafts_health(base_setup):
    # Verify /gmail/get_drafts returns a valid response.
    base_setup.post('/gmail/get_drafts')

# --- Draft Lifecycle Tests ---
def test_create_draft(created_draft):
    # Fixture already asserts IDs exist.
    assert created_draft["draft_id"], "Draft creation failed."
    assert created_draft["message_id"], "Message ID not returned."

def test_get_draft_message(base_setup, created_draft):
    # Retrieve the draft message details.
    response = base_setup.post("/gmail/get_message", payload={"message_id": created_draft["message_id"]})
    resp_json = response.json()
    data = resp_json["data"]
    assert data["id"] == created_draft["message_id"], "Draft message not found."
    # Optionally, check that key fields match expected values.
    assert data.get("subject") == "[Automatic Test] Draft Message", "Unexpected subject in draft."

def test_list_drafts_contains_created(base_setup, created_draft):
    # Verify that the created draft is in the list of drafts.
    response = base_setup.post("/gmail/get_drafts")
    drafts = response.json()["data"].get("messages", [])
    # Look for the expected message_id.
    assert any(d.get("id") == created_draft["message_id"] for d in drafts), "Created draft not found in list."

def test_modify_draft(base_setup, created_draft):
    # Update the draft with new subject, body, and required recipient.
    payload = {
        "draft_id": created_draft["draft_id"],
        "update_args": {
            "recipient": "veyraxservice@gmail.com",
            "subject": "Updated Subject",
            "body": "Updated content"
        }
    }
    response = base_setup.post("/gmail/modify_draft", payload=payload)
    assert response.status_code == 200, "Draft update failed."

def test_delete_draft(base_setup, created_draft):
    # Delete the created draft.
    response = base_setup.post("/gmail/delete_draft", payload={"draft_id": created_draft["draft_id"]})
    assert response.status_code == 200, "Draft deletion failed."

# --- Message Lifecycle Tests (Sending) ---
# Fixture to send a message using the draft created specifically for sending.
@pytest.fixture(scope="module")
def sent_message(base_setup, draft_for_send):
    # Send the draft message using /gmail/send_message.
    response = base_setup.post("/gmail/send_message", payload={"message_id": draft_for_send["message_id"]})
    sent_data = response.json()["data"]
    message_id = sent_data.get("id")
    assert message_id, "Message sending failed: No message ID returned."
    
    yield message_id

    # Cleanup: attempt to delete the sent message if still present.
    try:
        base_setup.post("/gmail/delete_message", payload={"message_id": message_id})
    except Exception:
        pass

def test_send_message(sent_message):
    # Verify that sending a message returned a valid message ID.
    assert sent_message, "Message sending failed."

def test_get_sent_message(base_setup, sent_message):
    # Retrieve the sent message and verify its ID.
    response = base_setup.post("/gmail/get_message", payload={"message_id": sent_message})
    data = response.json()["data"]
    assert data["id"] == sent_message, "Sent message not found."

def test_delete_message(base_setup, sent_message):
    # Delete the sent message.
    response = base_setup.post("/gmail/delete_message", payload={"message_id": sent_message})
    assert response.status_code == 200, "Message deletion failed."

#########################################
# Calendar Integration Tests
#########################################

# Fixture providing a valid event payload.
@pytest.fixture(scope="module")
def event_payload():
    return {
        "event": {
            "summary": "Test Event",
            "description": "This is a test event",
            "location": "Conference Room",
            "attendees": [{"email": "test@example.com"}],
            "start": {"dateTime": "2025-02-26T19:00:00Z"},
            "end": {"dateTime": "2025-02-26T20:00:00Z"}
        },
        "calendar_id": "primary"
    }

# Fixture to create an event and yield its event ID.
@pytest.fixture(scope="module")
def created_event(base_setup, event_payload):
    # Create the event via /google_calendar/create_event.
    response = base_setup.post("/google_calendar/create_event", payload=event_payload)
    event_data = response.json()["data"]
    event_id = event_data.get("id")
    assert event_id, "Event creation failed: no event id returned."
    
    yield event_id

    # Cleanup: attempt to delete the event.
    try:
        base_setup.post("/google_calendar/delete_event", payload={"event_id": event_id, "calendar_id": "primary"})
    except Exception:
        pass

# --- Calendar Health Check ---
def test_list_calendars(base_setup):
    # Verify that /google_calendar/list_calendars returns a calendars list.
    response = base_setup.post("/google_calendar/list_calendars")
    data = response.json()["data"]
    assert "items" in data, "List calendars response missing 'items' key."

# --- Event Lifecycle Tests ---
def test_create_event(created_event):
    # Fixture already verifies creation.
    assert created_event, "Created event id should not be empty."

def test_get_event(base_setup, created_event):
    # Retrieve the event details.
    payload = {"event_id": created_event, "calendar_id": "primary"}
    response = base_setup.post("/google_calendar/get_event", payload=payload)
    data = response.json()["data"]
    assert data.get("id") == created_event, "Retrieved event id does not match created event id."

def test_update_event(base_setup, created_event):
    # Update the event details.
    update_payload = {
        "event_id": created_event,
        "event_update": {
            "summary": "Updated Test Event",
            "description": "Updated description",
            "start": {"dateTime": "2025-02-26T19:30:00Z"},
            "end": {"dateTime": "2025-02-26T20:30:00Z"}
        },
        "calendar_id": "primary"
    }
    response = base_setup.post("/google_calendar/update_event", payload=update_payload)
    assert response.status_code == 200, "Event update failed."

def test_list_events(base_setup, created_event):
    # List events filtering by updated summary.
    list_payload = {
        "pageToken": None,
        "filters": {
            "keywords": "Updated Test Event",
            "calendarId": "primary"
        }
    }
    response = base_setup.post("/google_calendar/list_events", payload=list_payload)
    events = response.json()["data"].get("items", [])
    matching_events = [e for e in events if e.get("id") == created_event]
    assert matching_events, "Created event not found in event list."

def test_delete_event(base_setup, created_event):
    # Delete the created event.
    response = base_setup.post("/google_calendar/delete_event", payload={"event_id": created_event, "calendar_id": "primary"})
    assert response.status_code == 200, "Event deletion failed."
