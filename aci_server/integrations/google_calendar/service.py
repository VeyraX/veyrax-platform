from typing import Optional, Dict, Any, List
from .client import CalendarClient
from .schema import EventList, Event, EventCreate, EventUpdate, Calendar, CalendarList, EventFilters
from datetime import datetime

class CalendarService:
    def __init__(self, client: CalendarClient):
        self.client = client

    def list_events(self, pageToken: Optional[str] = None, 
                   filters: Optional[EventFilters] = None) -> EventList:
        params = {
            'maxResults': filters.max_results if filters and filters.max_results else 20,
            'singleEvents': True,
            'orderBy': 'startTime',
            'pageToken': pageToken
        }
        
        query_parts = []
        calendar_id = 'primary'
        
        if filters:
            if filters.calendarId:
                calendar_id = filters.calendarId
            
            if filters.keywords:
                query_parts.append(f'"{filters.keywords}"')
            
            if filters.attendees:
                query_parts.append(f"{filters.attendees}")
            
            if filters.after_date:
                after_date = datetime.fromisoformat(filters.after_date)
                params['timeMin'] = after_date.isoformat() + 'Z'
            
            if filters.before_date:
                before_date = datetime.fromisoformat(filters.before_date)
                params['timeMax'] = before_date.isoformat() + 'Z'

        if query_parts:
            params['q'] = ' '.join(query_parts)

        response = self.client.list_events(calendar_id=calendar_id, **params)
        events = []
        
        for event in response.get('items', []):
            event_data = event.copy()
            event_data['start'] = self._parse_datetime(event['start'])
            event_data['end'] = self._parse_datetime(event['end'])
            if filters:
                event_data['filters'] = {
                    'keywords': filters.keywords,
                    'attendees': filters.attendees,
                    'afterDate': filters.after_date,
                    'beforeDate': filters.before_date,
                    'calendarId': filters.calendarId
                }
            events.append(Event(**event_data))
            
        return EventList(
            items=events,
            nextPageToken=response.get('nextPageToken')
        )

    def get_event(self, event_id: str) -> Event:
        event = self.client.get_event(event_id)
        event_data = event.copy()
        event_data['start'] = self._parse_datetime(event['start'])
        event_data['end'] = self._parse_datetime(event['end'])
        return Event(**event_data)

    def create_event(self, event_data: EventCreate) -> Event:
        event_body = {
            'summary': event_data.summary,
            'start': event_data.start,
            'end': event_data.end
        }
        
        if event_data.description:
            event_body['description'] = event_data.description
        if event_data.location:
            event_body['location'] = event_data.location
        if event_data.attendees:
            event_body['attendees'] = event_data.attendees

        response = self.client.create_event(event_body)
        return self.get_event(response['id'])

    def update_event(self, event_id: str, event_data: EventUpdate) -> Event:
        event_body = event_data.dict(exclude_none=True)
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
            calendars.append(Calendar(**calendar))
            
        return CalendarList(items=calendars)
