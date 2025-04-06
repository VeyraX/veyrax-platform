from fastapi import APIRouter, Body, Depends, HTTPException
from starlette.requests import Request as FastAPIRequest
from typing import Dict, Any
import os

from .schema import (
    SearchEverywhereParams,
    SearchEverywhereData,
    SearchRoundtripParams,
    SearchRoundtripData,
    SearchOneWayParams,
    SearchOneWayData,
    FlightDetailParams,
    FlightDetailData,
    PriceCalendarParams,
    PriceCalendarData,
    PriceCalendarReturnParams,
    CheapestOneWayParams,
    CheapestOneWayData,
    HotelSearchParams,
    HotelSearchData,
    HotelDetailParams,
    HotelDetailData,
    HotelPricesParams,
    HotelPricesData,
    HotelReviewsParams,
    HotelReviewsData,
    ApiResponse
)
from .service import SkyscannerService
from .client import SkyscannerClient
from ..common.input_schema_decorator import schema
from ..common.utils import apply_error_handler_to_service, apply_error_handler_to_router, apply_error_handler_to_client
from ..common.examples_handler import ExamplesLoader

router = APIRouter(prefix="/skyscanner", tags=["skyscanner"])
examples = ExamplesLoader()

async def get_skyscanner_service(request: FastAPIRequest):
    try:
        api_key = os.getenv("RAPID_API_SKYSCANNER_KEY")
        client = SkyscannerClient(api_key)
        apply_error_handler_to_client(client)
        service = SkyscannerService(client)
        
        apply_error_handler_to_service(service)
        
        return service
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Failed to initialize Skyscanner service: {str(e)}"
        )

@router.post("/search_everywhere", response_model=ApiResponse)
@schema(
    input_schema_class=SearchEverywhereParams,
    output_schema_class=SearchEverywhereData,
    examples=examples["/skyscanner/search_everywhere"]
)
async def search_everywhere(
    params: Dict[str, Any] = Body(...),
    service: SkyscannerService = Depends(get_skyscanner_service)
):
    validated_params = SearchEverywhereParams(**params)
    return service.search_everywhere(validated_params)

@router.post("/search_roundtrip", response_model=ApiResponse)
@schema(
    input_schema_class=SearchRoundtripParams,
    output_schema_class=SearchRoundtripData,
    examples=examples["/skyscanner/search_roundtrip"]
)
async def search_roundtrip(
    params: Dict[str, Any] = Body(...),
    service: SkyscannerService = Depends(get_skyscanner_service)
):
    validated_params = SearchRoundtripParams(**params)
    return service.search_roundtrip(validated_params)

@router.post("/search_one_way", response_model=ApiResponse)
@schema(
    input_schema_class=SearchOneWayParams,
    output_schema_class=SearchOneWayData,
    examples=examples["/skyscanner/search_one_way"]
)
async def search_one_way(
    params: Dict[str, Any] = Body(...),
    service: SkyscannerService = Depends(get_skyscanner_service)
):
    validated_params = SearchOneWayParams(**params)
    return service.search_one_way(validated_params)

@router.post("/get_flight_detail", response_model=ApiResponse)
@schema(
    input_schema_class=FlightDetailParams,
    output_schema_class=FlightDetailData,
    examples=examples["/skyscanner/get_flight_detail"]
)
async def flight_detail(
    params: Dict[str, Any] = Body(...),
    service: SkyscannerService = Depends(get_skyscanner_service)
):
    validated_params = FlightDetailParams(**params)
    return service.get_flight_detail(validated_params)

@router.post("/get_price_calendar", response_model=ApiResponse)
@schema(
    input_schema_class=PriceCalendarParams,
    output_schema_class=PriceCalendarData,
    examples=examples["/skyscanner/get_price_calendar"]
)
async def price_calendar(
    params: Dict[str, Any] = Body(...),
    service: SkyscannerService = Depends(get_skyscanner_service)
):
    validated_params = PriceCalendarParams(**params)
    return service.get_price_calendar(validated_params)

@router.post("/get_price_calendar_return", response_model=ApiResponse)
@schema(
    input_schema_class=PriceCalendarReturnParams,
    output_schema_class=PriceCalendarData,
    examples=examples["/skyscanner/get_price_calendar_return"]
)
async def get_price_calendar_return(
    params: Dict[str, Any] = Body(...),
    service: SkyscannerService = Depends(get_skyscanner_service)
):
    validated_params = PriceCalendarReturnParams(**params)
    return service.get_price_calendar_return(validated_params)

@router.post("/get_cheapest_one_way", response_model=ApiResponse)
@schema(
    input_schema_class=CheapestOneWayParams,
    output_schema_class=CheapestOneWayData,
    examples=examples["/skyscanner/get_cheapest_one_way"]
)
async def get_cheapest_one_way(
    params: Dict[str, Any] = Body(...),
    service: SkyscannerService = Depends(get_skyscanner_service)
):
    validated_params = CheapestOneWayParams(**params)
    return service.get_cheapest_one_way(validated_params)

@router.post("/search_hotels", response_model=ApiResponse)
@schema(
    input_schema_class=HotelSearchParams,
    output_schema_class=HotelSearchData,
    examples=examples["/skyscanner/search_hotels"]
)
async def search_hotels(
    params: Dict[str, Any] = Body(...),
    service: SkyscannerService = Depends(get_skyscanner_service)
):
    validated_params = HotelSearchParams(**params)
    return service.search_hotels(validated_params)

@router.post("/get_hotel_detail", response_model=ApiResponse)
@schema(
    input_schema_class=HotelDetailParams,
    output_schema_class=HotelDetailData,
    examples=examples["/skyscanner/get_hotel_detail"]
)
async def get_hotel_detail(
    params: Dict[str, Any] = Body(...),
    service: SkyscannerService = Depends(get_skyscanner_service)
):
    validated_params = HotelDetailParams(**params)
    return service.get_hotel_detail(validated_params)

@router.post("/get_hotel_prices", response_model=ApiResponse)
@schema(
    input_schema_class=HotelPricesParams,
    output_schema_class=HotelPricesData,
    examples=examples["/skyscanner/get_hotel_prices"]
)
async def get_hotel_prices(
    params: Dict[str, Any] = Body(...),
    service: SkyscannerService = Depends(get_skyscanner_service)
):
    validated_params = HotelPricesParams(**params)
    return service.get_hotel_prices(validated_params)

@router.post("/get_hotel_reviews", response_model=ApiResponse)
@schema(
    input_schema_class=HotelReviewsParams,
    output_schema_class=HotelReviewsData,
    examples=examples["/skyscanner/get_hotel_reviews"]
)
async def get_hotel_reviews(
    params: Dict[str, Any] = Body(...),
    service: SkyscannerService = Depends(get_skyscanner_service)
):
    validated_params = HotelReviewsParams(**params)
    return service.get_hotel_reviews(validated_params)

apply_error_handler_to_router(router)
