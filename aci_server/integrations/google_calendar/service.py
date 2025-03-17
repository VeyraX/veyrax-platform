from typing import Optional, Dict, Any, List, Union
from .client import CalendarClient
from .schema import EventList, Event, EventCreate, EventUpdate, Calendar, CalendarList, EventFilters, ApiResponse
from datetime import datetime
import os
from ..common.component_handler import load_components, prepare_components_auto

class CalendarService:
    def __init__(self, client: CalendarClient):
        self.client = client
        self.components_data = self._load_components()

    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
        
    def prepare_response(self, data: Union[Event, EventList, CalendarList], component_name: str = None) -> ApiResponse:
        tool_name = "google-calendar"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)

    def list_events(self, pageToken: Optional[str] = None, 
                   filters: Optional[EventFilters] = None) -> ApiResponse:
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
                params['timeMin'] = self._format_datetime_param(filters.after_date)
            
            if filters.before_date:
                params['timeMax'] = self._format_datetime_param(filters.before_date)

        if query_parts:
            params['q'] = ' '.join(query_parts)
        
        response = self.client.list_events(calendar_id=calendar_id, **params)
        events = []
        
        for event in response.get('items', []):
            event_data = event.copy()
            event_data['start'] = self._parse_datetime(event['start'])
            event_data['end'] = self._parse_datetime(event['end'])
            events.append(Event(**event_data))
            
        events_list = EventList(
            items=events,
            nextPageToken=response.get('nextPageToken')
        )
        
        return self.prepare_response(events_list, "GoogleCalendarEventCard")

    def get_event(self, event_id: str, calendar_id: str = 'primary') -> ApiResponse:
        event = self.client.get_event(event_id, calendar_id)
        event_data = event.copy()
        event_data['start'] = self._parse_datetime(event['start'])
        event_data['end'] = self._parse_datetime(event['end'])
        event_obj = Event(**event_data)
        return self.prepare_response(event_obj, "GoogleCalendarEventCard")

    def create_event(self, event_data: EventCreate, calendar_id: str = 'primary') -> ApiResponse:
        event_body = event_data.dict(exclude_unset=True)
        response = self.client.create_event(event_body, calendar_id)
        return self.get_event(response['id'], calendar_id)

    def update_event(self, event_id: str, event_data: EventUpdate, calendar_id: str = 'primary') -> ApiResponse:
        existing_event = self.client.get_event(event_id, calendar_id)
        
        update_data = event_data.dict(exclude_none=True, exclude_unset=True)
        
        for key, value in update_data.items():
            existing_event[key] = value
        
        response = self.client.update_event(event_id, existing_event, calendar_id)
        return self.get_event(response['id'], calendar_id)

    def delete_event(self, event_id: str, calendar_id: str = 'primary') -> None:
        self.client.delete_event(event_id, calendar_id)

    def _parse_datetime(self, dt_dict: Dict[str, str]) -> datetime:
        dt_str = dt_dict.get('dateTime', dt_dict.get('date'))
        return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
    
    def _format_datetime_param(self, date_str: str) -> str:
        try:
            if len(date_str) == 10 and date_str[4] == '-' and date_str[7] == '-':
                return f"{date_str}T00:00:00Z"
                
            if 'T' in date_str and not (date_str.endswith('Z') or '+' in date_str or date_str[-6] == '-'):
                return f"{date_str}Z"
                
            if '+' in date_str or (len(date_str) > 6 and date_str[-6] == '-'):
                dt = datetime.fromisoformat(date_str)
                return dt.isoformat().replace('+00:00', 'Z')
                
            if date_str.endswith('Z'):
                return date_str
                
            dt = datetime.fromisoformat(date_str)
            return dt.isoformat() + 'Z'
        
        except ValueError:
            try:
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                return dt.strftime('%Y-%m-%dT%H:%M:%SZ')
            except:
                return date_str

    def list_calendars(self) -> ApiResponse:
        response = self.client.list_calendars()
        calendars = []
        
        for calendar in response.get('items', []):
            calendars.append(Calendar(**calendar))
            
        calendar_list = CalendarList(items=calendars)
        return self.prepare_response(calendar_list, "GoogleCalendarEventCard")
