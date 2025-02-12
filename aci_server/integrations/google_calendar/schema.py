from pydantic import BaseModel, Field
from typing import List, Optional, Annotated
from datetime import datetime
from fastapi import Query

class EventBase(BaseModel):
    id: str
    summary: str
    description: Optional[str] = None
    start: datetime
    end: datetime
    htmlLink: Optional[str] = None
    location: Optional[str] = None
    creator: Optional[dict] = None
    attendees: Optional[List[dict]] = None
    status: Optional[str] = None

class Event(EventBase):
    pass

class EventCreate(BaseModel):
    summary: str
    description: Optional[str]
    location: Optional[str]
    start: dict 
    end: dict   
    attendees: Optional[List[dict]] = None 

class EventUpdate(BaseModel):
    summary: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    start: Optional[dict] = None
    end: Optional[dict] = None
    attendees: Optional[List[dict]] = None

class EventList(BaseModel):
    items: List[EventBase]
    nextPageToken: Optional[str]

class EventFilters(BaseModel):
    calendarId: Optional[str] = None
    keywords: Optional[str] = None
    attendees: Optional[str] = None 
    after_date: Optional[str] = None
    before_date: Optional[str] = None

class Calendar(BaseModel):
    id: str
    summary: str
    description: Optional[str]
    primary: bool = False
    timeZone: Optional[str]
    backgroundColor: Optional[str]
    foregroundColor: Optional[str]

class CalendarList(BaseModel):
    items: List[Calendar]