from fastapi import APIRouter, Depends, HTTPException, Request as FastAPIRequest, Query
from typing import Optional, Dict, Any
from .schema import (
    MessageList, Message, DraftMessage, EventList, Event, 
    EventCreate, EventUpdate, EventFilters, MessageFilters,
    CalendarList
)
from .service import OutlookService
from .client import OutlookClient
from ..common.auth import TokenService, OutlookTokenRefresher

router = APIRouter(prefix="/outlook", tags=["outlook"])

async def get_outlook_service(request: FastAPIRequest):
    token_data = await TokenService.get_user_token(request, 'outlook')
    
    if TokenService.is_token_expired(token_data):
        try:
            token_data = await OutlookTokenRefresher.refresh(request, token_data)
        except Exception as e:
            raise HTTPException(status_code=401, detail="Failed to refresh token")
    
    client = OutlookClient(token_data['access_token'])
    return OutlookService(client)

# Mail routes
@router.get("/messages", response_model=MessageList)
async def get_messages(
    next_link: Optional[str] = None,
    filters: MessageFilters = Depends(),
    service: OutlookService = Depends(get_outlook_service)
):
    """Get messages with optional filtering"""
    return service.get_messages(next_link, filters)

@router.get("/messages/{message_id}", response_model=Message)
async def get_message(
    message_id: str,
    service: OutlookService = Depends(get_outlook_service)
):
    """Get a specific message by ID"""
    return service.get_message(message_id)

@router.post("/messages/draft", response_model=Message)
async def create_draft(
    draft: DraftMessage,
    service: OutlookService = Depends(get_outlook_service)
):
    """Create a draft message"""
    return service.create_draft(draft)

@router.post("/messages/{message_id}/send", response_model=Dict[str, Any])
async def send_message(
    message_id: str,
    service: OutlookService = Depends(get_outlook_service)
):
    """Send an existing draft message"""
    return service.send_message(message_id)

@router.delete("/messages/{message_id}")
async def delete_message(
    message_id: str,
    service: OutlookService = Depends(get_outlook_service)
):
    """Delete a message"""
    service.delete_message(message_id)
    return {"status": "deleted", "message_id": message_id}

# Calendar routes
@router.get("/calendars", response_model=CalendarList)
async def list_calendars(
    service: OutlookService = Depends(get_outlook_service)
):
    """Get list of calendars"""
    return service.list_calendars()

@router.get("/events", response_model=EventList)
async def list_events(
    next_link: Optional[str] = None,
    filters: EventFilters = Depends(),
    service: OutlookService = Depends(get_outlook_service)
):
    """Get events with optional filtering"""
    return service.list_events(next_link, filters)

@router.get("/events/{event_id}", response_model=Event)
async def get_event(
    event_id: str,
    service: OutlookService = Depends(get_outlook_service)
):
    """Get a specific event by ID"""
    return service.get_event(event_id)

@router.post("/events", response_model=Event)
async def create_event(
    event: EventCreate,
    service: OutlookService = Depends(get_outlook_service)
):
    """Create a new event"""
    return service.create_event(event)

@router.patch("/events/{event_id}", response_model=Event)
async def update_event(
    event_id: str,
    event: EventUpdate,
    service: OutlookService = Depends(get_outlook_service)
):
    """Update an existing event"""
    return service.update_event(event_id, event)

@router.delete("/events/{event_id}")
async def delete_event(
    event_id: str,
    service: OutlookService = Depends(get_outlook_service)
):
    """Delete an event"""
    service.delete_event(event_id)
    return {"status": "deleted", "event_id": event_id}