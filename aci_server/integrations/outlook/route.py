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
from ..common.utils import format_validation_error, apply_error_handler_to_service, apply_error_handler_to_router
from ..common.examples_handler import ExamplesLoader

router = APIRouter(prefix="/outlook", tags=["outlook"])

examples = ExamplesLoader()  # Will automatically use /integrations/outlook directory

async def get_outlook_service(request: FastAPIRequest):
    try:
        token_data = await TokenService.get_user_token(request, 'outlook')
        
        if TokenService.is_token_expired(token_data):
            try:
                token_data = await OutlookTokenRefresher.refresh(request, token_data)
            except Exception as e:
                raise HTTPException(status_code=401, detail="Failed to refresh token")
        
        client = OutlookClient(token_data['access_token'])
        service = OutlookService(client)
        apply_error_handler_to_service(service)
        return service
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize Outlook service: {str(e)}")

@router.post("/get_messages", response_model=ApiResponse)
@schema(input_schema_class=GetMessagesParams, output_schema_class=GetMessagesResponse, examples=examples["/outlook/get_messages"])
async def get_messages(
    params: Dict[str, Any] = Body(...),
    service: OutlookService = Depends(get_outlook_service)
):
    validated_params = GetMessagesParams(**params)
    return service.get_messages(
        validated_params.next_link, 
        validated_params.filters
    )

@router.post("/get_message", response_model=ApiResponse)
@schema(input_schema_class=GetMessageParams, output_schema_class=GetMessageResponse, examples=examples["/outlook/get_message"])
async def get_message(
    params: Dict[str, Any] = Body(...),
    service: OutlookService = Depends(get_outlook_service)
):
    validated_params = GetMessageParams(**params)
    return service.get_message(validated_params.message_id)

@router.post("/create_draft", response_model=ApiResponse)
@schema(input_schema_class=CreateDraftParams, output_schema_class=CreateDraftResponse, examples=examples["/outlook/create_draft"])
async def create_draft(
    params: Dict[str, Any] = Body(...),
    service: OutlookService = Depends(get_outlook_service)
):
    validated_params = CreateDraftParams(**params)
    return service.create_draft(validated_params.draft_args)

@router.post("/send_message", response_model=ApiResponse)
@schema(input_schema_class=SendMessageParams, output_schema_class=SendMessageResponse, examples=examples["/outlook/send_message"])
async def send_message(
    params: Dict[str, Any] = Body(...),
    service: OutlookService = Depends(get_outlook_service)
):
    validated_params = SendMessageParams(**params)
    return service.send_message(validated_params.message_id)

@router.post("/delete_message")
@schema(input_schema_class=DeleteMessageParams, output_schema_class=DeleteMessageResponse, examples=examples["/outlook/delete_message"])
async def delete_message(
    params: Dict[str, Any] = Body(...),
    service: OutlookService = Depends(get_outlook_service)
):
    validated_params = DeleteMessageParams(**params)
    service.delete_message(validated_params.message_id)
    return {"status": "success"}

@router.post("/list_calendars", response_model=ApiResponse)
@schema(input_schema_class=ListCalendarsParams, output_schema_class=ListCalendarsResponse, examples=examples["/outlook/list_calendars"])
async def list_calendars(
    params: Dict[str, Any] = Body(...),
    service: OutlookService = Depends(get_outlook_service)
):
    validated_params = ListCalendarsParams(**params)
    return service.list_calendars()

@router.post("/list_events", response_model=ApiResponse)
@schema(input_schema_class=ListEventsParams, output_schema_class=ListEventsResponse, examples=examples["/outlook/list_events"])
async def list_events(
    params: Dict[str, Any] = Body(...),
    service: OutlookService = Depends(get_outlook_service)
):
    validated_params = ListEventsParams(**params)
    return service.list_events(
        validated_params.next_link, 
        validated_params.filters
    )

@router.post("/get_event", response_model=ApiResponse)
@schema(input_schema_class=GetEventParams, output_schema_class=GetEventResponse, examples=examples["/outlook/get_event"])
async def get_event(
    params: Dict[str, Any] = Body(...),
    service: OutlookService = Depends(get_outlook_service)
):
    validated_params = GetEventParams(**params)
    return service.get_event(validated_params.event_id)

@router.post("/create_event", response_model=ApiResponse)
@schema(input_schema_class=CreateEventParams, output_schema_class=CreateEventResponse, examples=examples["/outlook/create_event"])
async def create_event(
    params: Dict[str, Any] = Body(...),
    service: OutlookService = Depends(get_outlook_service)
):
    validated_params = CreateEventParams(**params)
    return service.create_event(
        event=validated_params.event,
        calendar_id=validated_params.calendar_id
    )

@router.post("/update_event", response_model=ApiResponse)
@schema(input_schema_class=UpdateEventParams, output_schema_class=UpdateEventResponse, examples=examples["/outlook/update_event"])
async def update_event(
    params: Dict[str, Any] = Body(...),
    service: OutlookService = Depends(get_outlook_service)
):
    validated_params = UpdateEventParams(**params)
    return service.update_event(
        validated_params.event_id, 
        validated_params.event_update
    )

@router.post("/delete_event")
@schema(input_schema_class=DeleteEventParams, output_schema_class=DeleteEventResponse, examples=examples["/outlook/delete_event"])
async def delete_event(
    params: Dict[str, Any] = Body(...),
    service: OutlookService = Depends(get_outlook_service)
):
    validated_params = DeleteEventParams(**params)
    service.delete_event(validated_params.event_id)
    return {"status": "success"}

apply_error_handler_to_router(router)