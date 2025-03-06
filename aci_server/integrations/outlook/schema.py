from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime

# Mail schemas
class MessageBase(BaseModel):
    id: str
    subject: Optional[str]
    body_preview: str
    # body: Optional[str]  # body is a html string, can cause issues with rendering in the UI
    sender: Optional[str]
    recipient: Optional[str]
    date: datetime
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
    body: Optional[Dict[str, str]] = None
    description: Optional[str] = None
    location: Optional[str] = None
    start: str
    end: str
    web_link: str = Field(default="", alias="webLink")
    organizer: Optional[Dict[str, str]] = None
    status: Optional[str] = None
    is_recurring: Optional[bool] = Field(None, alias="isRecurring")
    attendees: Optional[List[Dict[str, str]]] = None

class Event(EventBase):
    pass

class EventCreate(BaseModel):
    subject: str
    start: str
    end: str
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
    start: Optional[str] = None
    end: Optional[str] = None
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
    data: Union[Message, MessageList, Event, EventList, CalendarList, CalendarDeleteEvent]
    component: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None

# New parameter schema classes
class GetMessagesParams(BaseModel):
    filters: Optional[MessageFilters] = None
    next_link: Optional[str] = None

class GetMessageParams(BaseModel):
    message_id: str

class CreateDraftParams(BaseModel):
    draft_args: DraftMessage

class SendMessageParams(BaseModel):
    message_id: str

class DeleteMessageParams(BaseModel):
    message_id: str

class ListCalendarsParams(BaseModel):
    pass  

class ListEventsParams(BaseModel):
    filters: Optional[EventFilters] = None
    next_link: Optional[str] = None

class GetEventParams(BaseModel):
    event_id: str

class CreateEventParams(BaseModel):
    event: EventCreate
    calendar_id: Optional[str] = Field(default=None, description="Optional calendar ID, uses default calendar if not provided")

class UpdateEventParams(BaseModel):
    event_id: str
    event_update: EventUpdate

class DeleteEventParams(BaseModel):
    event_id: str

# Response schema classes
class GetMessagesResponse(BaseModel):
    data: MessageList
    message: Optional[str] = None

class GetMessageResponse(BaseModel):
    data: Message
    message: Optional[str] = None

class CreateDraftResponse(BaseModel):
    data: Message
    message: Optional[str] = None

class SendMessageResponse(BaseModel):
    data: Dict[str, str]
    message: Optional[str] = None

class DeleteMessageResponse(BaseModel):
    status: str
    message: Optional[str] = None

class ListCalendarsResponse(BaseModel):
    data: CalendarList
    message: Optional[str] = None

class ListEventsResponse(BaseModel):
    data: EventList
    message: Optional[str] = None

class GetEventResponse(BaseModel):
    data: Event
    message: Optional[str] = None

class CreateEventResponse(BaseModel):
    data: Event
    message: Optional[str] = None

class UpdateEventResponse(BaseModel):
    data: Event
    message: Optional[str] = None

class DeleteEventResponse(BaseModel):
    status: str
    message: Optional[str] = None
