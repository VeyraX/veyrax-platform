from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from typing import Optional, Dict, Any

class CalendarClient:
    def __init__(self, credentials: Credentials):
        self.service = build('calendar', 'v3', credentials=credentials)

    def list_calendars(self) -> Dict[str, Any]:
        return self.service.calendarList().list().execute()

    def list_events(self, calendar_id: str = 'primary', **kwargs) -> Dict[str, Any]:
        return self.service.events().list(
            calendarId=calendar_id,
            **kwargs
        ).execute()

    def get_event(self, event_id: str, calendar_id: str = 'primary') -> Dict[str, Any]:
        return self.service.events().get(
            calendarId=calendar_id,
            eventId=event_id
        ).execute()

    def create_event(self, event_body: Dict[str, Any], calendar_id: str = 'primary') -> Dict[str, Any]:
        return self.service.events().insert(
            calendarId=calendar_id,
            body=event_body
        ).execute()

    def update_event(self, event_id: str, event_body: Dict[str, Any], calendar_id: str = 'primary') -> Dict[str, Any]:
        return self.service.events().update(
            calendarId=calendar_id,
            eventId=event_id,
            body=event_body
        ).execute()

    def delete_event(self, event_id: str, calendar_id: str = 'primary') -> None:
        self.service.events().delete(
            calendarId=calendar_id,
            eventId=event_id
        ).execute()