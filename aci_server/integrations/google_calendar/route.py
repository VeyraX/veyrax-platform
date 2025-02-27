from fastapi import APIRouter, Depends, HTTPException, Request as FastAPIRequest, Body
from typing import Optional, Dict, Any, List, Union
from .schema import (
    EventList, Event, EventCreate, EventUpdate, EventFilters, CalendarList, ApiResponse,
    ListEventsParams, GetEventParams, CreateEventParams, UpdateEventParams, 
    DeleteEventParams, ListCalendarsParams
)
from .service import CalendarService
from .client import CalendarClient
import os
from google.oauth2.credentials import Credentials
from ..common.auth import TokenService, GoogleTokenRefresher
from ..common.input_schema_decorator import input_schema
from pydantic import ValidationError
from ..common.utils import format_validation_error
router = APIRouter(prefix="/google_calendar", tags=["google_calendar"])

async def get_calendar_service(request: FastAPIRequest):
    try:
        token_data = await TokenService.get_user_token(request, 'google-calendar')
        
        if TokenService.is_token_expired(token_data):
            try:
                token_data = await GoogleTokenRefresher.refresh(request, token_data)
            except Exception as e:
                raise HTTPException(status_code=401, detail="Failed to refresh token")
            
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize Calendar service: {str(e)}")

@router.post("/list_events", response_model=ApiResponse)
@input_schema(schema_class=ListEventsParams)
async def list_events(
    params: Dict[str, Any] = Body(...),
    service: CalendarService = Depends(get_calendar_service)
):
    try:
        validated_params = ListEventsParams(**params)
        return service.list_events(
            pageToken=validated_params.pageToken, 
            filters=validated_params.filters
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'ListEventsParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/get_event", response_model=ApiResponse)
@input_schema(schema_class=GetEventParams)
async def get_event(
    params: Dict[str, Any] = Body(...),
    service: CalendarService = Depends(get_calendar_service)
):
    try:
        validated_params = GetEventParams(**params)
        return service.get_event(
            validated_params.event_id, 
            validated_params.calendar_id
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetEventParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create_event", response_model=ApiResponse)
@input_schema(schema_class=CreateEventParams)
async def create_event(
    params: Dict[str, Any] = Body(...),
    service: CalendarService = Depends(get_calendar_service)
):
    try:
        validated_params = CreateEventParams(**params)
        return service.create_event(
            validated_params.event, 
            validated_params.calendar_id
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'CreateEventParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update_event", response_model=ApiResponse)
@input_schema(schema_class=UpdateEventParams)
async def update_event(
    params: Dict[str, Any] = Body(...),
    service: CalendarService = Depends(get_calendar_service)
):
    try:
        validated_params = UpdateEventParams(**params)
        return service.update_event(
            validated_params.event_id, 
            validated_params.event_update, 
            validated_params.calendar_id
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'UpdateEventParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/delete_event")
@input_schema(schema_class=DeleteEventParams)
async def delete_event(
    params: Dict[str, Any] = Body(...),
    service: CalendarService = Depends(get_calendar_service)
):
    try:
        validated_params = DeleteEventParams(**params)
        service.delete_event(
            validated_params.event_id, 
            validated_params.calendar_id
        )
        return {"status": "success"}
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'DeleteEventParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/list_calendars", response_model=ApiResponse)
@input_schema(schema_class=ListCalendarsParams)
async def list_calendars(
    params: Dict[str, Any] = Body(...),
    service: CalendarService = Depends(get_calendar_service)
):
    try:
        validated_params = ListCalendarsParams(**params)
        return service.list_calendars()
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'ListCalendarsParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
