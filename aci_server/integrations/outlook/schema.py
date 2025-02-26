from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime

# Mail schemas
class MessageBase(BaseModel):
    id: str
    subject: Optional[str]
    body_preview: str
    body: Optional[str]
    from_address: Optional[str]
    to_recipients: Optional[List[str]]
    created_datetime: datetime
    web_link: str

class Message(MessageBase):
    importance: Optional[str]
    is_read: bool
    categories: Optional[List[str]]

class DraftMessage(BaseModel):
    to_recipients: List[str]
    subject: str
    body: str
    
class MessageList(BaseModel):
    messages: List[MessageBase]
    next_link: Optional[str]

class MessageFilters(BaseModel):
    search: Optional[str] = None
    to: Optional[str] = None
    subject: Optional[str] = None
    after_date: Optional[str] = None
    before_date: Optional[str] = None
    max_results: Optional[int] = 20

class EventTime(BaseModel):
    dateTime: str
    timeZone: str

class Location(BaseModel):
    displayName: Optional[str] = None
    address: Optional[Dict[str, Any]] = None
    coordinates: Optional[Dict[str, Any]] = None

class EmailAddress(BaseModel):
    name: Optional[str] = None
    address: str

class Organizer(BaseModel):
    emailAddress: EmailAddress

class EventBase(BaseModel):
    id: str
    subject: str
    body: Optional[Dict[str, str]]
    start: EventTime
    end: EventTime
    location: Optional[Location] = None
    web_link: str
    organizer: Optional[Organizer] = None

class Event(EventBase):
    attendees: Optional[List[Dict[str, Any]]] = None

class EventCreate(BaseModel):
    subject: str
    start: EventTime
    end: EventTime
    body: Optional[Dict[str, str]] = None
    location: Optional[Location] = None
    attendees: Optional[List[Dict[str, Any]]] = None
    importance: Optional[str] = None
    isReminderOn: Optional[bool] = None
    reminderMinutesBeforeStart: Optional[int] = None
    sensitivity: Optional[str] = None
    showAs: Optional[str] = None
    categories: Optional[List[str]] = None
    recurrence: Optional[Dict[str, Any]] = None
    onlineMeeting: Optional[Dict[str, Any]] = None
    isOnlineMeeting: Optional[bool] = None
    responseRequested: Optional[bool] = None
    allowNewTimeProposals: Optional[bool] = None

class EventUpdate(BaseModel):
    subject: Optional[str] = None
    body: Optional[Dict[str, str]] = None
    start: Optional[EventTime] = None
    end: Optional[EventTime] = None
    location: Optional[Dict[str, str]] = None
    attendees: Optional[List[Dict[str, str]]] = None

class EventList(BaseModel):
    events: List[EventBase]
    next_link: Optional[str]

class EventFilters(BaseModel):
    calendar_id: Optional[str] = None
    search: Optional[str] = None
    after_date: Optional[str] = None
    before_date: Optional[str] = None
    max_results: Optional[int] = 20

class Calendar(BaseModel):
    id: str
    name: str
    color: Optional[str]
    can_edit: bool
    owner: Optional[Dict[str, str]]

class CalendarList(BaseModel):
    calendars: List[Calendar]

class CalendarDeleteEvent(BaseModel):
    event_id: str

class ApiResponse(BaseModel):
    data: Union[Message, MessageList, EventList, CalendarList, CalendarDeleteEvent]
    component: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None
