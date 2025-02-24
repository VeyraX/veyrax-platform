from fastapi import APIRouter, Depends, HTTPException, Request as FastAPIRequest, Body
from typing import Optional, Dict, Any, List, Union
from .schema import EventList, Event, EventCreate, EventUpdate, EventFilters, CalendarList, ApiResponse
from .service import CalendarService
from .client import CalendarClient
import os
from google.oauth2.credentials import Credentials
from ..common.auth import TokenService, GoogleTokenRefresher

router = APIRouter(prefix="/google_calendar", tags=["google_calendar"])

async def get_calendar_service(request: FastAPIRequest):
    token_data = await TokenService.get_user_token(request, 'google-calendar')
    if TokenService.is_token_expired(token_data):
        token_data = await GoogleTokenRefresher.refresh(request, token_data)
    
    creds = Credentials(
        token=token_data['access_token'],
        refresh_token=token_data['refresh_token'],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv('GOOGLE_CLIENT_ID'),
        client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
        scopes=token_data['scopes'].split(',')
    )
    client = CalendarClient(creds)
    return CalendarService(client)

@router.post("/list_events", response_model=ApiResponse)
async def list_events(
    params: Dict[str, Any] = Body(...),
    service: CalendarService = Depends(get_calendar_service)
):
    try:
        filters_data = params.get('filters', {})
        page_token = params.get('pageToken')
        
        filters = EventFilters(**filters_data)
        return service.list_events(pageToken=page_token, filters=filters)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_event", response_model=ApiResponse)
async def get_event(
    params: Dict[str, Any] = Body(...),
    service: CalendarService = Depends(get_calendar_service)
):
    try:
        event_id = params.get('event_id')
        calendar_id = params.get('calendar_id', 'primary')
            
        return service.get_event(event_id, calendar_id)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create_event", response_model=ApiResponse)
async def create_event(
    params: Dict[str, Any] = Body(...),
    service: CalendarService = Depends(get_calendar_service)
):
    try:
        event_data = params.get('event', params)
        calendar_id = params.get('calendar_id', 'primary')
        
        event = EventCreate(**event_data)
        return service.create_event(event, calendar_id)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update_event", response_model=ApiResponse)
async def update_event(
    params: Dict[str, Any] = Body(...),
    service: CalendarService = Depends(get_calendar_service)
):
    try:
        event_id = params.get('event_id')
        event_data = params.get('event_update', {})
        calendar_id = params.get('calendar_id', 'primary')
                
        event_update = EventUpdate(**event_data)
        return service.update_event(event_id, event_update, calendar_id)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/delete_event")
async def delete_event(
    params: Dict[str, Any] = Body(...),
    service: CalendarService = Depends(get_calendar_service)
):
    try:
        event_id = params.get('event_id')
        calendar_id = params.get('calendar_id', 'primary')
            
        service.delete_event(event_id, calendar_id)
        return {"status": "success"}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/list_calendars", response_model=ApiResponse)
async def list_calendars(
    params: Dict[str, Any] = Body(...),
    service: CalendarService = Depends(get_calendar_service)
):
    try:
        return service.list_calendars()
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
