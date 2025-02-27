from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from fastapi import Query

class EventFilters(BaseModel):
    calendarId: Optional[str] = None
    keywords: Optional[str] = None
    attendees: Optional[str] = None 
    after_date: Optional[str] = None
    before_date: Optional[str] = None
    max_results: Optional[int] = 20

class EventBase(BaseModel):
    summary: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    attendees: Optional[List[Dict[str, Any]]] = None

class EventCreate(EventBase):
    summary: str
    start: Dict[str, str]
    end: Dict[str, str]

class EventUpdate(EventBase):
    start: Optional[Dict[str, str]] = None
    end: Optional[Dict[str, str]] = None

class Event(EventBase):
    id: str
    start: datetime
    end: datetime
    htmlLink: Optional[str] = None
    creator: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    component: Optional[Dict[str, Any]] = None

class EventList(BaseModel):
    items: List[Event]
    nextPageToken: Optional[str] = None

class Calendar(BaseModel):
    id: str
    summary: str
    description: Optional[str] = None
    primary: bool = False
    timeZone: Optional[str] = None
    backgroundColor: Optional[str] = None
    foregroundColor: Optional[str] = None

class CalendarList(BaseModel):
    items: List[Calendar]

class ApiResponse(BaseModel):
    data: Union[Event, EventList, CalendarList]
    component: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None

# New parameter schema classes
class ListEventsParams(BaseModel):
    pageToken: Optional[str] = None
    filters: Optional[EventFilters] = None

class GetEventParams(BaseModel):
    event_id: str
    calendar_id: Optional[str] = 'primary'

class CreateEventParams(BaseModel):
    event: EventCreate
    calendar_id: Optional[str] = 'primary'

class UpdateEventParams(BaseModel):
    event_id: str
    event_update: EventUpdate
    calendar_id: Optional[str] = 'primary'

class DeleteEventParams(BaseModel):
    event_id: str
    calendar_id: Optional[str] = 'primary'

class ListCalendarsParams(BaseModel):
    pass  # No parameters needed but keeping class for consistency