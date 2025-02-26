from aci_server.integrations.common.tests.base import base_setup
import pytest

# This will automatically assert for 200 status code
def test_google_calendar_list_calendars_health(base_setup):
    base_setup.post('/google_calendar/list_calendars')

# Fixture that provides a payload for event creation
@pytest.fixture(scope="module")
def event_payload():
    return {
        "event": {
            "summary": "Test Event",
            "description": "This is a test event",
            "location": "Virtual",
            "attendees": [{"email": "veyraxservice@gmail.com"}],
            "start": {"dateTime": "2023-09-15T10:00:00Z"},
            "end": {"dateTime": "2023-09-15T11:00:00Z"}
        },
        "calendar_id": "primary"
    }

# Fixture to create an event and yield its ID for subsequent tests.
@pytest.fixture(scope="module")
def created_event(base_setup, event_payload):
    # Create the event.
    response = base_setup.post("/google_calendar/create_event", payload=event_payload)
    event_id = response.json()["data"]["id"]
    assert event_id, "Event creation failed: no event ID returned."
    
    yield event_id

    # we do it in test_delete_event
    # # Cleanup: try to delete the event if it hasn't been deleted already.
    # try:
    #     base_setup.post("/google_calendar/delete_event", payload={"event_id": event_id, "calendar_id": "primary"})
    # except Exception:
    #     pass

def test_create_event(base_setup, event_payload, created_event):
    # This test passes if the created_event fixture returns a valid event_id.
    assert created_event is not None

def test_get_event(base_setup, created_event):
    # Retrieve the event using its ID.
    payload = {
        "event_id": created_event,
        "calendar_id": "primary"
    }
    response = base_setup.post("/google_calendar/get_event", payload=payload)
    data = response.json()["data"]
    assert data["id"] == created_event, "Returned event does not match the created event."

def test_update_event(base_setup, created_event):
    # Update the event.
    payload = {
        "event_id": created_event,
        "event_update": {
            "summary": "Updated Test Event",
            "description": "Updated description",
            "start": {"dateTime": "2023-09-15T10:30:00Z"},
            "end": {"dateTime": "2023-09-15T11:30:00Z"}
        },
        "calendar_id": "primary"
    }
    base_setup.post("/google_calendar/update_event", payload=payload)

def test_list_events(base_setup, created_event):
    # List events and verify the updated event is included.
    payload = {
        "pageToken": None,
        "filters": {
            "keywords": "Updated Test Event",
            "calendarId": "primary"
        }
    }
    response = base_setup.post("/google_calendar/list_events", payload=payload)
    events = response.json()["data"].get("items", [])
    assert any(item["id"] == created_event for item in events), "Updated event not found in event list."

def test_delete_event(base_setup, created_event):
    # Delete the event.
    payload = {
        "event_id": created_event,
        "calendar_id": "primary"
    }
    base_setup.post("/google_calendar/delete_event", payload=payload)


def test_list_calendars(base_setup):
    # Call the list_calendars endpoint (no payload needed).
    base_setup.post("/google_calendar/list_calendars")
