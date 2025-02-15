from fastapi import APIRouter, Depends, HTTPException, Request as FastAPIRequest
from typing import Optional
from .schema import EventList, Event, EventCreate, EventUpdate, EventFilters, CalendarList
from .service import CalendarService
from .client import CalendarClient
import pickle
import os
from datetime import datetime
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
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
        scopes=token_data['scopes'].split()
    )
    
    client = CalendarClient(creds)
    return CalendarService(client)

@router.get("/events", response_model=EventList)
async def list_events(
    pageToken: Optional[str] = None,
    filters: EventFilters = Depends(),  
    service: CalendarService = Depends(get_calendar_service)
):
    return service.list_events(pageToken=pageToken, filters=filters)

@router.get("/events/{event_id}", response_model=Event)
async def get_event(
    event_id: str,
    service: CalendarService = Depends(get_calendar_service)
):
    return service.get_event(event_id)

@router.post("/events", response_model=Event)
async def create_event(
    event: EventCreate,
    service: CalendarService = Depends(get_calendar_service)
):
    return service.create_event(event)

@router.patch("/events/{event_id}", response_model=Event)
async def update_event(
    event_id: str,
    event_update: EventUpdate,
    service: CalendarService = Depends(get_calendar_service)
):
    return service.update_event(event_id, event_update)

@router.delete("/events/{event_id}")
async def delete_event(
    event_id: str,
    service: CalendarService = Depends(get_calendar_service)
):
    service.delete_event(event_id)
    return {"status": "success"}

@router.get("/calendars", response_model=CalendarList)
async def list_calendars(
    service: CalendarService = Depends(get_calendar_service)
):
    return service.list_calendars()
