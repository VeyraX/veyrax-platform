from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class EventBase(BaseModel):
    id: str
    summary: str
    description: Optional[str]
    start: datetime
    end: datetime

class Event(EventBase):
    location: Optional[str]
    creator: dict
    attendees: Optional[List[dict]]
    status: str
    html_link: str

class EventCreate(BaseModel):
    summary: str
    description: Optional[str]
    location: Optional[str]
    start_time: datetime
    end_time: datetime
    attendees: Optional[List[str]] = None

class EventUpdate(BaseModel):
    summary: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    attendees: Optional[List[str]] = None

class EventList(BaseModel):
    events: List[EventBase]
    next_page_token: Optional[str]

class EventFilters(BaseModel):
    calendar_id: Optional[str] = None
    time_min: Optional[datetime] = None
    time_max: Optional[datetime] = None
    query: Optional[str] = None

class Calendar(BaseModel):
    id: str
    summary: str
    description: Optional[str]
    primary: bool = False
    time_zone: Optional[str]
    background_color: Optional[str]
    foreground_color: Optional[str]

class CalendarList(BaseModel):
    calendars: List[Calendar]