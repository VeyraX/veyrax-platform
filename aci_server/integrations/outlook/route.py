from fastapi import APIRouter, Depends, HTTPException, Request as FastAPIRequest, Body
from typing import Optional, Dict, Any
from .schema import (
    MessageList, Message, DraftMessage, EventList, Event, 
    EventCreate, EventUpdate, EventFilters, MessageFilters,
    CalendarList, ApiResponse, CalendarDeleteEvent,
    GetMessagesParams, GetMessageParams,
    CreateDraftParams, SendMessageParams, DeleteMessageParams,
    ListCalendarsParams, ListEventsParams, GetEventParams,
    CreateEventParams, UpdateEventParams, DeleteEventParams,
    GetMessagesResponse, GetMessageResponse, CreateDraftResponse,
    SendMessageResponse, DeleteMessageResponse, ListCalendarsResponse,
    ListEventsResponse, GetEventResponse, CreateEventResponse,
    UpdateEventResponse, DeleteEventResponse
)
from .service import OutlookService
from .client import OutlookClient
from ..common.auth import TokenService, OutlookTokenRefresher
from ..common.input_schema_decorator import schema, input_schema, output_schema
from pydantic import ValidationError

router = APIRouter(prefix="/outlook", tags=["outlook"])

async def get_outlook_service(request: FastAPIRequest):
    try:
        token_data = await TokenService.get_user_token(request, 'outlook')
        
        if TokenService.is_token_expired(token_data):
            try:
                token_data = await OutlookTokenRefresher.refresh(request, token_data)
            except Exception as e:
                raise HTTPException(status_code=401, detail="Failed to refresh token")
        
        client = OutlookClient(token_data['access_token'])
        return OutlookService(client)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize Outlook service: {str(e)}")

@router.post("/get_messages", response_model=ApiResponse)
@schema(input_schema_class=GetMessagesParams, output_schema_class=GetMessagesResponse)
async def get_messages(
    params: Dict[str, Any] = Body(...),
    service: OutlookService = Depends(get_outlook_service)
):
    try:
        validated_params = GetMessagesParams(**params)
        return service.get_messages(
            validated_params.next_link, 
            validated_params.filters
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_message", response_model=ApiResponse)
@schema(input_schema_class=GetMessageParams, output_schema_class=GetMessageResponse)
async def get_message(
    params: Dict[str, Any] = Body(...),
    service: OutlookService = Depends(get_outlook_service)
):
    try:
        validated_params = GetMessageParams(**params)
        return service.get_message(validated_params.message_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create_draft", response_model=ApiResponse)
@schema(input_schema_class=CreateDraftParams, output_schema_class=CreateDraftResponse)
async def create_draft(
    params: Dict[str, Any] = Body(...),
    service: OutlookService = Depends(get_outlook_service)
):
    try:
        validated_params = CreateDraftParams(**params)
        return service.create_draft(validated_params.draft_args)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/send_message", response_model=ApiResponse)
@schema(input_schema_class=SendMessageParams, output_schema_class=SendMessageResponse)
async def send_message(
    params: Dict[str, Any] = Body(...),
    service: OutlookService = Depends(get_outlook_service)
):
    try:
        validated_params = SendMessageParams(**params)
        return service.send_message(validated_params.message_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/delete_message")
@schema(input_schema_class=DeleteMessageParams, output_schema_class=DeleteMessageResponse)
async def delete_message(
    params: Dict[str, Any] = Body(...),
    service: OutlookService = Depends(get_outlook_service)
):
    try:
        validated_params = DeleteMessageParams(**params)
        service.delete_message(validated_params.message_id)
        return {"status": "success"}
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/list_calendars", response_model=ApiResponse)
@schema(input_schema_class=ListCalendarsParams, output_schema_class=ListCalendarsResponse)
async def list_calendars(
    params: Dict[str, Any] = Body(...),
    service: OutlookService = Depends(get_outlook_service)
):
    try:
        validated_params = ListCalendarsParams(**params)
        return service.list_calendars()
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/list_events", response_model=ApiResponse)
@schema(input_schema_class=ListEventsParams, output_schema_class=ListEventsResponse)
async def list_events(
    params: Dict[str, Any] = Body(...),
    service: OutlookService = Depends(get_outlook_service)
):
    try:
        validated_params = ListEventsParams(**params)
        return service.list_events(
            validated_params.next_link, 
            validated_params.filters
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_event", response_model=ApiResponse)
@schema(input_schema_class=GetEventParams, output_schema_class=GetEventResponse)
async def get_event(
    params: Dict[str, Any] = Body(...),
    service: OutlookService = Depends(get_outlook_service)
):
    try:
        validated_params = GetEventParams(**params)
        return service.get_event(validated_params.event_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create_event", response_model=ApiResponse)
@schema(input_schema_class=CreateEventParams, output_schema_class=CreateEventResponse)
async def create_event(
    params: Dict[str, Any] = Body(...),
    service: OutlookService = Depends(get_outlook_service)
):
    try:
        print("[route] create_event params", params)
        validated_params = CreateEventParams(**params)
        print("[route] validated params",  validated_params)
        return service.create_event(
            event=validated_params.event,
            calendar_id=validated_params.calendar_id
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update_event", response_model=ApiResponse)
@schema(input_schema_class=UpdateEventParams, output_schema_class=UpdateEventResponse)
async def update_event(
    params: Dict[str, Any] = Body(...),
    service: OutlookService = Depends(get_outlook_service)
):
    try:
        validated_params = UpdateEventParams(**params)
        return service.update_event(
            validated_params.event_id, 
            validated_params.event_update
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/delete_event")
@schema(input_schema_class=DeleteEventParams, output_schema_class=DeleteEventResponse)
async def delete_event(
    params: Dict[str, Any] = Body(...),
    service: OutlookService = Depends(get_outlook_service)
):
    try:
        validated_params = DeleteEventParams(**params)
        service.delete_event(validated_params.event_id)
        return {"status": "success"}
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))