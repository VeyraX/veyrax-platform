from aci_server.integrations.common.tests.base import base_setup
import pytest


def test_google_calendar_list_events_health(base_setup):
    # Construct the URL for the list_events endpoint.
    calendar_url = f"{base_setup.api_url}/google_calendar/list_events"
    print(f"Constructed Calendar URL: {calendar_url}")

    headers = base_setup.get_headers()
    print(f"Request Headers: {headers}")

    # Prepare an example payload (adjust according to your expected input schema).
    payload = {
        "filters": {},
        "pageToken": None
    }

    # Note: The endpoint is defined as POST, so use POST.
    response = base_setup.client.post(calendar_url, headers=headers, json=payload)
    print(f"Response Status Code: {response.status_code}")
    print(f"Response Text: {response.text}")

    if response.status_code == 200:
        result = {
            "status": "healthy",
            "statusCode": response.status_code,
            "data": response.json()
        }
    else:
        result = {
            "status": "unhealthy",
            "statusCode": response.status_code,
            "message": f"Failed to call calendar endpoint: {response.text}"
        }
    print(f"Result: {result}")
    assert response.status_code == 200, f"Calendar endpoint unhealthy: {result}"