from fastapi import APIRouter, Body, Depends, HTTPException
from starlette.requests import Request as FastAPIRequest
from typing import Dict, Any
from .schema import (
    GetBookingsParams,
    GetBookingParams,
    CreateBookingParams,
    RescheduleBookingParams,
    CancelBookingParams,
    GetScheduleParams,
    UpdateScheduleParams,
    GetSchedulesParams,
    GetProfileParams,
    GetEventTypesParams,
    GetBookingsResponse,
    GetBookingResponse,
    CreateBookingResponse,
    RescheduleBookingResponse,
    CancelBookingResponse,
    GetProfileResponse,
    GetSchedulesResponse,
    GetScheduleResponse,
    UpdateScheduleResponse,
    GetEventTypesResponse,
    ValidateKeyResponse,
    ApiResponse
)
from .service import CalService
from .client import CalClient
from ..common.auth import validate_provider_api_key
from ..common.input_schema_decorator import schema, input_schema, output_schema
from ..common.utils import apply_error_handler_to_service, apply_error_handler_to_router
from ..common.examples_handler import ExamplesLoader

router = APIRouter(prefix="/cal", tags=["cal"])
examples = ExamplesLoader()

async def get_cal_service(request: FastAPIRequest):
    try:
        #api_key = await validate_provider_api_key(request, "cal")
        api_key = '***REMOVED***'
        client = CalClient(api_key)
        service = CalService(client)
        
        apply_error_handler_to_service(service)
        
        return service
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Failed to initialize Cal service: {str(e)}"
        )

@router.post("/get_bookings", response_model=ApiResponse)
@schema(
    input_schema_class=GetBookingsParams,
    output_schema_class=GetBookingsResponse,
    examples=examples["/cal/get_bookings"]
)
async def get_bookings(
    params: Dict[str, Any] = Body(...),
    service: CalService = Depends(get_cal_service)
):
    validated_params = GetBookingsParams(**params)
    return service.get_bookings(validated_params)

@router.post("/get_booking", response_model=ApiResponse)
@schema(
    input_schema_class=GetBookingParams,
    output_schema_class=GetBookingResponse,
    examples=examples["/cal/get_booking"]
)
async def get_booking(
    params: Dict[str, Any] = Body(...),
    service: CalService = Depends(get_cal_service)
):
    validated_params = GetBookingParams(**params)
    return service.get_booking(validated_params)

@router.post("/create_booking", response_model=ApiResponse)
@schema(
    input_schema_class=CreateBookingParams,
    output_schema_class=CreateBookingResponse,
    examples=examples["/cal/create_booking"]
)
async def create_booking(
    params: Dict[str, Any] = Body(...),
    service: CalService = Depends(get_cal_service)
):
    validated_params = CreateBookingParams(**params)
    return service.create_booking(validated_params)

@router.post("/reschedule_booking", response_model=ApiResponse)
@schema(
    input_schema_class=RescheduleBookingParams,
    output_schema_class=RescheduleBookingResponse,
    examples=examples["/cal/reschedule_booking"]
)
async def reschedule_booking(
    params: Dict[str, Any] = Body(...),
    service: CalService = Depends(get_cal_service)
):
    validated_params = RescheduleBookingParams(**params)
    return service.reschedule_booking(validated_params)

@router.post("/cancel_booking", response_model=ApiResponse)
@schema(
    input_schema_class=CancelBookingParams,
    output_schema_class=CancelBookingResponse,
    examples=examples["/cal/cancel_booking"]
)
async def cancel_booking(
    params: Dict[str, Any] = Body(...),
    service: CalService = Depends(get_cal_service)
):
    validated_params = CancelBookingParams(**params)
    return service.cancel_booking(validated_params)

@router.post("/get_profile", response_model=ApiResponse)
@schema(
    input_schema_class=GetProfileParams,
    output_schema_class=GetProfileResponse,
    examples=examples["/cal/get_profile"]
)
async def get_profile(
    params: Dict[str, Any] = Body(...),
    service: CalService = Depends(get_cal_service)
):
    validated_params = GetProfileParams(**params)
    return service.get_profile()

@router.post("/get_schedules", response_model=ApiResponse)
@schema(
    input_schema_class=GetSchedulesParams,
    output_schema_class=GetSchedulesResponse,
    examples=examples["/cal/get_schedules"]
)
async def get_schedules(
    params: Dict[str, Any] = Body(...),
    service: CalService = Depends(get_cal_service)
):
    validated_params = GetSchedulesParams(**params)
    return service.get_schedules()

@router.post("/get_schedule", response_model=ApiResponse)
@schema(
    input_schema_class=GetScheduleParams,
    output_schema_class=GetScheduleResponse,
    examples=examples["/cal/get_schedule"]
)
async def get_schedule(
    params: Dict[str, Any] = Body(...),
    service: CalService = Depends(get_cal_service)
):
    validated_params = GetScheduleParams(**params)
    return service.get_schedule(validated_params)

@router.post("/update_schedule", response_model=ApiResponse)
@schema(
    input_schema_class=UpdateScheduleParams,
    output_schema_class=UpdateScheduleResponse,
    examples=examples["/cal/update_schedule"]
)
async def update_schedule(
    params: Dict[str, Any] = Body(...),
    service: CalService = Depends(get_cal_service)
):
    validated_params = UpdateScheduleParams(**params)
    return service.update_schedule(validated_params)

@router.post("/get_event_types", response_model=ApiResponse)
@schema(
    input_schema_class=GetEventTypesParams,
    output_schema_class=GetEventTypesResponse,
    examples=examples["/cal/get_event_types"]
)
async def get_event_types(
    params: Dict[str, Any] = Body(...),
    service: CalService = Depends(get_cal_service)
):
    validated_params = GetEventTypesParams(**params)
    return service.get_event_types(validated_params)

@router.post("/validate_key")
async def validate_key(
    params: Dict[str, Any] = Body(...),
):
    try:
        api_key = params.get("api_key")
        if not api_key:
            return {"valid": False, "message": "API key is required"}
        
        client = CalClient(api_key=api_key)
        try:
            response = client.get_me()
            return {"valid": True, "message": "API key is valid"}
        except Exception:
            return {"valid": False, "message": "Invalid API key"}
    except Exception as e:
        return {"valid": False, "message": f"Invalid API key: {str(e)}"}

apply_error_handler_to_router(router)
