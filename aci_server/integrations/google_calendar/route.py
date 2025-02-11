from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from .schema import EventList, Event, EventCreate, EventUpdate, EventFilters, CalendarList
from .service import CalendarService
from .client import CalendarClient
import pickle
import os
from datetime import datetime

router = APIRouter(prefix="/google_calendar", tags=["google_calendar"])

async def get_calendar_service():
    if os.path.exists('credentials/token.pickle'):
        with open('credentials/token.pickle', 'rb') as token:
            creds = pickle.load(token)
    else:
        raise HTTPException(status_code=404, detail="Credentials file not found")
    
    client = CalendarClient(creds)
    return CalendarService(client)

@router.get("/events", response_model=EventList)
async def list_events(
    page_token: Optional[str] = None,
    filters: EventFilters = Depends(),
    service: CalendarService = Depends(get_calendar_service)
):
    return service.list_events(
        page_token=page_token,
        time_min=filters.time_min,
        time_max=filters.time_max,
        query=filters.query,
        calendar_id=filters.calendar_id
    )

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
