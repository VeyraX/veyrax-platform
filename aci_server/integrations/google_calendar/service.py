from typing import Optional, Dict, Any, List
from .client import CalendarClient
from .schema import EventList, Event, EventCreate, EventUpdate, Calendar, CalendarList
from datetime import datetime

class CalendarService:
    def __init__(self, client: CalendarClient):
        self.client = client

    def list_events(self, page_token: Optional[str] = None, 
                   time_min: Optional[datetime] = None,
                   time_max: Optional[datetime] = None,
                   query: Optional[str] = None,
                   calendar_id: Optional[str] = None) -> EventList:
        params = {
            'pageToken': page_token,
            'maxResults': 20,
            'singleEvents': True,
            'orderBy': 'startTime',
            'calendarId': calendar_id or 'primary'
        }
        
        if time_min:
            params['timeMin'] = time_min.isoformat() + 'Z'
        if time_max:
            params['timeMax'] = time_max.isoformat() + 'Z'
        if query:
            params['q'] = query

        calendar_id = params.pop('calendarId')
        response = self.client.list_events(calendar_id=calendar_id, **params)
        events = []
        
        for event in response.get('items', []):
            events.append({
                'id': event['id'],
                'summary': event.get('summary', ''),
                'description': event.get('description'),
                'start': self._parse_datetime(event['start']),
                'end': self._parse_datetime(event['end'])
            })
            
        return EventList(
            events=events,
            next_page_token=response.get('nextPageToken')
        )

    def get_event(self, event_id: str) -> Event:
        event = self.client.get_event(event_id)
        return Event(
            id=event['id'],
            summary=event.get('summary', ''),
            description=event.get('description'),
            location=event.get('location'),
            start=self._parse_datetime(event['start']),
            end=self._parse_datetime(event['end']),
            creator=event['creator'],
            attendees=event.get('attendees'),
            status=event['status'],
            html_link=event['htmlLink']
        )

    def create_event(self, event_data: EventCreate) -> Event:
        event_body = {
            'summary': event_data.summary,
            'description': event_data.description,
            'start': {'dateTime': event_data.start_time.isoformat()},
            'end': {'dateTime': event_data.end_time.isoformat()}
        }

        if event_data.location:
            event_body['location'] = event_data.location
        
        if event_data.attendees:
            event_body['attendees'] = [{'email': email} for email in event_data.attendees]

        response = self.client.create_event(event_body)
        return self.get_event(response['id'])

    def update_event(self, event_id: str, event_data: EventUpdate) -> Event:
        current_event = self.client.get_event(event_id)
        event_body = {}

        if event_data.summary is not None:
            event_body['summary'] = event_data.summary
        if event_data.description is not None:
            event_body['description'] = event_data.description
        if event_data.location is not None:
            event_body['location'] = event_data.location
        if event_data.start_time is not None:
            event_body['start'] = {'dateTime': event_data.start_time.isoformat()}
        if event_data.end_time is not None:
            event_body['end'] = {'dateTime': event_data.end_time.isoformat()}
        if event_data.attendees is not None:
            event_body['attendees'] = [{'email': email} for email in event_data.attendees]

        response = self.client.update_event(event_id, event_body)
        return self.get_event(response['id'])

    def delete_event(self, event_id: str) -> None:
        self.client.delete_event(event_id)

    def _parse_datetime(self, dt_dict: Dict[str, str]) -> datetime:
        dt_str = dt_dict.get('dateTime', dt_dict.get('date'))
        return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))

    def list_calendars(self) -> CalendarList:
        response = self.client.list_calendars()
        calendars = []
        
        for calendar in response.get('items', []):
            calendars.append(Calendar(
                id=calendar['id'],
                summary=calendar.get('summary', ''),
                description=calendar.get('description'),
                primary=calendar.get('primary', False),
                time_zone=calendar.get('timeZone'),
                background_color=calendar.get('backgroundColor'),
                foreground_color=calendar.get('foregroundColor')
            ))
            
        return CalendarList(calendars=calendars)
