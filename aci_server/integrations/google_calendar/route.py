from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from .schema import EventList, Event, EventCreate, EventUpdate, EventFilters, CalendarList
from .service import CalendarService
from .client import CalendarClient
import pickle
import os
from datetime import datetime
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

router = APIRouter(prefix="/google_calendar", tags=["google_calendar"])

async def get_calendar_service():
    if os.path.exists('credentials/google_token.pickle'):
        with open('credentials/google_token.pickle', 'rb') as token:
            creds_dict = pickle.load(token)
            creds = Credentials(
                token=creds_dict['access_token'],
                refresh_token=creds_dict['refresh_token'],
                token_uri="https://oauth2.googleapis.com/token",
                client_id=os.getenv('GOOGLE_CLIENT_ID'),
                client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
                scopes=creds_dict['scope'].split()
            )
            
            if creds.expired:
                creds.refresh(Request())
                updated_creds_dict = {
                    'access_token': creds.token,
                    'refresh_token': creds.refresh_token,
                    'scope': ' '.join(creds.scopes),
                }
                with open('credentials/google_token.pickle', 'wb') as token:
                    pickle.dump(updated_creds_dict, token)
    else:
        raise HTTPException(status_code=404, detail="Credentials file not found")
    
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
