import os
from fastapi import APIRouter, Body, Depends, HTTPException
from starlette.requests import Request as FastAPIRequest
from typing import Dict, Any
from .schema import (
    SearchBusinessesParams,
    GetBusinessDetailsParams,
    GetBusinessReviewsParams,
    GetBusinessMenusParams,
    BusinessSearchResponse,
    BusinessDetailsResponse,
    BusinessReviewsResponse,
    BusinessMenusResponse,
    ApiResponse
)
from .service import YelpService
from .client import YelpClient
from ..common.input_schema_decorator import schema
from ..common.utils import apply_error_handler_to_service, apply_error_handler_to_router, apply_error_handler_to_client
from ..common.examples_handler import ExamplesLoader

router = APIRouter(prefix="/yelp", tags=["yelp"])
examples = ExamplesLoader()

async def get_yelp_service(request: FastAPIRequest):
    try:
        api_key = os.getenv("RAPIDAPI_KEY_YELP") or os.getenv("RAPIDAPI_KEY")
        
        client = YelpClient(api_key)
        apply_error_handler_to_client(client)
        
        service = YelpService(client)
        apply_error_handler_to_service(service)
        
        return service
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Failed to initialize Yelp service: {str(e)}"
        )

@router.post("/search_businesses", response_model=ApiResponse)
@schema(
    input_schema_class=SearchBusinessesParams,
    output_schema_class=BusinessSearchResponse,
    examples=examples["/yelp/search_businesses"]
)
async def search_businesses(
    params: Dict[str, Any] = Body(...),
    service: YelpService = Depends(get_yelp_service)
):
    validated_params = SearchBusinessesParams(**params)
    return service.search_businesses(validated_params)

@router.post("/get_business_details", response_model=ApiResponse)
@schema(
    input_schema_class=GetBusinessDetailsParams,
    output_schema_class=BusinessDetailsResponse,
    examples=examples["/yelp/get_business_details"]
)
async def get_business_details(
    params: Dict[str, Any] = Body(...),
    service: YelpService = Depends(get_yelp_service)
):
    validated_params = GetBusinessDetailsParams(**params)
    return service.get_business_details(validated_params)

@router.post("/get_business_reviews", response_model=ApiResponse)
@schema(
    input_schema_class=GetBusinessReviewsParams,
    output_schema_class=BusinessReviewsResponse,
    examples=examples["/yelp/get_business_reviews"]
)
async def get_business_reviews(
    params: Dict[str, Any] = Body(...),
    service: YelpService = Depends(get_yelp_service)
):
    validated_params = GetBusinessReviewsParams(**params)
    return service.get_business_reviews(validated_params)

@router.post("/get_business_menus", response_model=ApiResponse)
@schema(
    input_schema_class=GetBusinessMenusParams,
    output_schema_class=BusinessMenusResponse,
    examples=examples["/yelp/get_business_menus"]
)
async def get_business_menus(
    params: Dict[str, Any] = Body(...),
    service: YelpService = Depends(get_yelp_service)
):
    validated_params = GetBusinessMenusParams(**params)
    return service.get_business_menus(validated_params)

apply_error_handler_to_router(router) 