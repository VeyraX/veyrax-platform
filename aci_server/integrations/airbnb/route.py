from fastapi import APIRouter, Body, Depends, HTTPException
from starlette.requests import Request as FastAPIRequest
from typing import Dict, Any
from .schema import (
    AirbnbSearchParams,
    AirbnbListingDetailsParams,
    SearchResponse,
    ListingDetailsResponse,
    ApiResponse
)
from .service import AirbnbService
from .client import AirbnbClient
from ..common.input_schema_decorator import schema
from ..common.utils import apply_error_handler_to_service, apply_error_handler_to_router, apply_error_handler_to_client
from ..common.examples_handler import ExamplesLoader

router = APIRouter(prefix="/airbnb", tags=["airbnb"])
examples = ExamplesLoader()

async def get_airbnb_service():
    try:
        client = AirbnbClient()
        apply_error_handler_to_client(client)
        service = AirbnbService(client)
        apply_error_handler_to_service(service)
        return service
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initialize Airbnb service: {str(e)}"
        )

@router.post("/search", response_model=ApiResponse)
@schema(
    input_schema_class=AirbnbSearchParams,
    output_schema_class=SearchResponse,
    examples=examples["/airbnb/search"]
)
async def search(
    params: Dict[str, Any] = Body(...),
    service: AirbnbService = Depends(get_airbnb_service)
):
    validated_params = AirbnbSearchParams(**params)
    return await service.search(validated_params)

@router.post("/listing_details", response_model=ApiResponse)
@schema(
    input_schema_class=AirbnbListingDetailsParams,
    output_schema_class=ListingDetailsResponse,
    examples=examples["/airbnb/listing_details"]
)
async def listing_details(
    params: Dict[str, Any] = Body(...),
    service: AirbnbService = Depends(get_airbnb_service)
):
    validated_params = AirbnbListingDetailsParams(**params)
    return await service.get_listing_details(validated_params)

apply_error_handler_to_router(router)
