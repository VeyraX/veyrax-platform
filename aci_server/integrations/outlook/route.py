from fastapi import APIRouter, Depends, HTTPException, Request as FastAPIRequest, Query, Body
from typing import Optional, Dict, Any
from .schema import (
    MessageList, Message, DraftMessage, EventList, Event, 
    EventCreate, EventUpdate, EventFilters, MessageFilters,
    CalendarList, ApiResponse, GetMessagesParams, GetMessageParams,
    CreateDraftParams, SendMessageParams, DeleteMessageParams,
    ListCalendarsParams, ListEventsParams, GetEventParams,
    CreateEventParams, UpdateEventParams, DeleteEventParams
)
from .service import OutlookService
from .client import OutlookClient
from ..common.auth import TokenService, OutlookTokenRefresher
from ..common.input_schema_decorator import input_schema

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

@router.post("/get_messages", response_model=ApiResponse)
@input_schema(schema_class=GetMessagesParams)
async def get_messages(
    params: Dict[str, Any] = Body(...),
    service: OutlookService = Depends(get_outlook_service)
):
    try:
        filters_data = params.get('filters', {})
        next_link = params.get('next_link')
        
        filters = MessageFilters(**filters_data)
        return service.get_messages(next_link, filters)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_message", response_model=ApiResponse)
@input_schema(schema_class=GetMessageParams)
async def get_message(
    params: Dict[str, Any] = Body(...),
    service: OutlookService = Depends(get_outlook_service)
):
    try:
        message_id = params.get('message_id')
        if not message_id:
            raise HTTPException(status_code=400, detail="message_id is required")
            
        return service.get_message(message_id)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create_draft", response_model=ApiResponse)
@input_schema(schema_class=CreateDraftParams)
async def create_draft(
    params: Dict[str, Any] = Body(...),
    service: OutlookService = Depends(get_outlook_service)
):
    try:
        draft_data = params.get('draft_args', params)
        draft = DraftMessage(**draft_data)
        return service.create_draft(draft)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/send_message", response_model=ApiResponse)
@input_schema(schema_class=SendMessageParams)
async def send_message(
    params: Dict[str, Any] = Body(...),
    service: OutlookService = Depends(get_outlook_service)
):
    try:
        message_id = params.get('message_id')
        if not message_id:
            raise HTTPException(status_code=400, detail="message_id is required")
            
        return service.send_message(message_id)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/delete_message")
@input_schema(schema_class=DeleteMessageParams)
async def delete_message(
    params: Dict[str, Any] = Body(...),
    service: OutlookService = Depends(get_outlook_service)
):
    try:
        message_id = params.get('message_id')
        if not message_id:
            raise HTTPException(status_code=400, detail="message_id is required")
            
        service.delete_message(message_id)
        return {"status": "success"}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/list_calendars", response_model=ApiResponse)
@input_schema(schema_class=ListCalendarsParams)
async def list_calendars(
    params: Dict[str, Any] = Body(...),
    service: OutlookService = Depends(get_outlook_service)
):
    try:
        return service.list_calendars()
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/list_events", response_model=ApiResponse)
@input_schema(schema_class=ListEventsParams)
async def list_events(
    params: Dict[str, Any] = Body(...),
    service: OutlookService = Depends(get_outlook_service)
):
    try:
        filters_data = params.get('filters', {})
        next_link = params.get('next_link')
        
        filters = EventFilters(**filters_data)
        return service.list_events(next_link, filters)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_event", response_model=ApiResponse)
@input_schema(schema_class=GetEventParams)
async def get_event(
    params: Dict[str, Any] = Body(...),
    service: OutlookService = Depends(get_outlook_service)
):
    try:
        event_id = params.get('event_id')
        if not event_id:
            raise HTTPException(status_code=400, detail="event_id is required")
            
        return service.get_event(event_id)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create_event", response_model=ApiResponse)
@input_schema(schema_class=CreateEventParams)
async def create_event(
    params: Dict[str, Any] = Body(...),
    service: OutlookService = Depends(get_outlook_service)
):
    try:
        event_data = params.get('event', params)
        event = EventCreate(**event_data)
        return service.create_event(event)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update_event", response_model=ApiResponse)
@input_schema(schema_class=UpdateEventParams)
async def update_event(
    params: Dict[str, Any] = Body(...),
    service: OutlookService = Depends(get_outlook_service)
):
    try:
        event_id = params.get('event_id')
        event_data = params.get('event_update', {})
        
        if not event_id:
            raise HTTPException(status_code=400, detail="event_id is required")
            
        event = EventUpdate(**event_data)
        return service.update_event(event_id, event)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/delete_event")
@input_schema(schema_class=DeleteEventParams)
async def delete_event(
    params: Dict[str, Any] = Body(...),
    service: OutlookService = Depends(get_outlook_service)
):
    try:
        event_id = params.get('event_id')
        if not event_id:
            raise HTTPException(status_code=400, detail="event_id is required")
            
        service.delete_event(event_id)
        return {"status": "success"}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))