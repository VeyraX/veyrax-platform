from fastapi import APIRouter, Body, Depends, HTTPException, Query
from starlette.requests import Request as FastAPIRequest
from typing import Dict, Any, Optional
from .schema import (
    SearchOneWayParams,
    SearchRoundtripParams,
    SearchMultiCityParams,
    FlightDetailsParams,
    PriceCalendarParams,
    PriceCalendarReturnParams,
    CheapestOneWayParams,
    SearchOneWayResponse,
    SearchRoundtripResponse,
    SearchMultiCityResponse,
    FlightDetailsResponse,
    PriceCalendarResponse,
    PriceCalendarReturnResponse,
    CheapestOneWayResponse,
    ApiResponse,
    HotelSearchParams,
    HotelSearchResponse,
    HotelDetailParams,
    HotelDetailResponse,
    HotelPricesParams,
    HotelPricesResponse,
    HotelReviewsParams,
    HotelReviewsResponse
)
from .service import SkyscannerService
from .client import SkyscannerClient
from ..common.auth import validate_provider_api_key
from ..common.input_schema_decorator import schema, input_schema, output_schema
from ..common.utils import apply_error_handler_to_service, apply_error_handler_to_router, apply_error_handler_to_client, format_validation_error
from ..common.examples_handler import ExamplesLoader

router = APIRouter(prefix="/skyscanner", tags=["skyscanner"])
examples = ExamplesLoader()

async def get_skyscanner_service(request: FastAPIRequest):
    try:
        api_key = await validate_provider_api_key(request, "skyscanner")
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

@router.post("/search_one_way", response_model=ApiResponse)
@schema(
    input_schema_class=SearchOneWayParams,
    output_schema_class=SearchOneWayResponse,
    examples=examples["/skyscanner/search_one_way"]
)
async def search_one_way(
    params: Dict[str, Any] = Body(...),
    service: SkyscannerService = Depends(get_skyscanner_service)
):
    validated_params = SearchOneWayParams(**params)
    return service.search_one_way(validated_params)

@router.post("/search_roundtrip", response_model=ApiResponse)
@schema(
    input_schema_class=SearchRoundtripParams,
    output_schema_class=SearchRoundtripResponse,
    examples=examples["/skyscanner/search_roundtrip"]
)
async def search_roundtrip(
    params: Dict[str, Any] = Body(...),
    service: SkyscannerService = Depends(get_skyscanner_service)
):
    validated_params = SearchRoundtripParams(**params)
    return service.search_roundtrip(validated_params)

@router.post("/search_multi_city", response_model=ApiResponse)
@schema(
    input_schema_class=SearchMultiCityParams,
    output_schema_class=SearchMultiCityResponse,
    examples=examples["/skyscanner/search_multi_city"]
)
async def search_multi_city(
    params: Dict[str, Any] = Body(...),
    service: SkyscannerService = Depends(get_skyscanner_service)
):
    validated_params = SearchMultiCityParams(**params)
    return service.search_multi_city(validated_params)

@router.post("/price_calendar", response_model=ApiResponse)
@schema(
    input_schema_class=PriceCalendarParams,
    output_schema_class=PriceCalendarResponse,
    examples=examples["/skyscanner/price_calendar"]
)
async def price_calendar(
    params: Dict[str, Any] = Body(...),
    service: SkyscannerService = Depends(get_skyscanner_service)
):
    validated_params = PriceCalendarParams(**params)
    return service.price_calendar(validated_params)

@router.post("/price_calendar_return", response_model=ApiResponse)
@schema(
    input_schema_class=PriceCalendarReturnParams,
    output_schema_class=PriceCalendarReturnResponse,
    examples=examples["/skyscanner/price_calendar_return"]
)
async def price_calendar_return(
    params: Dict[str, Any] = Body(...),
    service: SkyscannerService = Depends(get_skyscanner_service)
):
    validated_params = PriceCalendarReturnParams(**params)
    return service.price_calendar_return(validated_params)

@router.post("/cheapest_one_way", response_model=ApiResponse)
@schema(
    input_schema_class=CheapestOneWayParams,
    output_schema_class=CheapestOneWayResponse,
    examples=examples["/skyscanner/cheapest_one_way"]
)
async def cheapest_one_way(
    params: Dict[str, Any] = Body(...),
    service: SkyscannerService = Depends(get_skyscanner_service)
):
    validated_params = CheapestOneWayParams(**params)
    return service.cheapest_one_way(validated_params)

@router.post("/flight_details", response_model=ApiResponse)
@schema(
    input_schema_class=FlightDetailsParams,
    output_schema_class=FlightDetailsResponse,
    examples=examples["/skyscanner/flight_details"]
)
async def flight_details(
    params: Dict[str, Any] = Body(...),
    service: SkyscannerService = Depends(get_skyscanner_service)
):
    validated_params = FlightDetailsParams(**params)
    return service.flight_details(validated_params)

@router.post("/hotels_search", response_model=ApiResponse)
@schema(
    input_schema_class=HotelSearchParams,
    output_schema_class=HotelSearchResponse,
    examples=examples["/skyscanner/hotels_search"]
)
async def hotels_search(
    params: Dict[str, Any] = Body(...),
    service: SkyscannerService = Depends(get_skyscanner_service)
):
    validated_params = HotelSearchParams(**params)
    return service.search_hotels(validated_params)

@router.post("/hotel_detail", response_model=ApiResponse)
@schema(
    input_schema_class=HotelDetailParams,
    output_schema_class=HotelDetailResponse,
    examples=examples["/skyscanner/hotel_detail"]
)
async def hotel_detail(
    params: Dict[str, Any] = Body(...),
    service: SkyscannerService = Depends(get_skyscanner_service)
):
    validated_params = HotelDetailParams(**params)
    return service.hotel_detail(validated_params)

@router.post("/hotel_prices", response_model=ApiResponse)
@schema(
    input_schema_class=HotelPricesParams,
    output_schema_class=HotelPricesResponse,
    examples=examples["/skyscanner/hotel_prices"]
)
async def hotel_prices(
    params: Dict[str, Any] = Body(...),
    service: SkyscannerService = Depends(get_skyscanner_service)
):
    """
    Get pricing information for a specific hotel
    """
    validated_params = HotelPricesParams(**params)
    return service.hotel_prices(validated_params)

@router.post("/hotel_reviews", response_model=ApiResponse)
@schema(
    input_schema_class=HotelReviewsParams,
    output_schema_class=HotelReviewsResponse,
    examples=examples["/skyscanner/hotel_reviews"]
)
async def hotel_reviews(
    params: Dict[str, Any] = Body(...),
    service: SkyscannerService = Depends(get_skyscanner_service)
):
    """
    Get reviews for a specific hotel with filtering and sorting options
    """
    validated_params = HotelReviewsParams(**params)
    return service.hotel_reviews(validated_params)

apply_error_handler_to_router(router)
