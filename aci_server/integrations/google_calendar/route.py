from fastapi import APIRouter, Depends, HTTPException, Request as FastAPIRequest, Body
from typing import Optional, Dict, Any, List, Union
from .schema import (
    EventList, Event, EventCreate, EventUpdate, EventFilters, CalendarList, ApiResponse,
    ListEventsParams, GetEventParams, CreateEventParams, UpdateEventParams, 
    DeleteEventParams, ListCalendarsParams,
    ListEventsResponse, GetEventResponse, CreateEventResponse, UpdateEventResponse,
    DeleteEventResponse, ListCalendarsResponse
)
from .service import CalendarService
from .client import CalendarClient
import os
from google.oauth2.credentials import Credentials
from ..common.auth import TokenService, GoogleTokenRefresher
from ..common.input_schema_decorator import schema, input_schema, output_schema
from pydantic import ValidationError
from ..common.utils import format_validation_error
from ..common.examples_handler import ExamplesLoader



router = APIRouter(prefix="/google-calendar", tags=["google-calendar"])

examples = ExamplesLoader() 

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
@schema(input_schema_class=ListEventsParams, output_schema_class=ListEventsResponse, examples=examples["/google-calendar/list_events"])
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
@schema(input_schema_class=GetEventParams, output_schema_class=GetEventResponse, examples=examples["/google-calendar/get_event"])
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
@schema(input_schema_class=CreateEventParams, output_schema_class=CreateEventResponse, examples=examples["/google-calendar/create_event"])
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
@schema(input_schema_class=UpdateEventParams, output_schema_class=UpdateEventResponse, examples=examples["/google-calendar/update_event"])
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
@schema(input_schema_class=DeleteEventParams, output_schema_class=DeleteEventResponse, examples=examples["/google-calendar/delete_event"])
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
@schema(input_schema_class=ListCalendarsParams, output_schema_class=ListCalendarsResponse, examples=examples["/google-calendar/list_calendars"])
async def list_calendars(
    params: Dict[str, Any] = Body(...),
    service: CalendarService = Depends(get_calendar_service)
):
    try:
        print(f"Listing calendars with params: {params}")
        validated_params = ListCalendarsParams(**params)
        print(f"Validated params: {validated_params}")
        return service.list_calendars()
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'ListCalendarsParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
