from fastapi import APIRouter, Body, Depends, HTTPException, Request, Security
from starlette.requests import Request as FastAPIRequest
from fastapi.security import APIKeyHeader
from typing import Dict, Any
from .schema import (
    PropertyParams,
    PropertySearchParams,
    ZestimateParams,
    ZestimateHistoryParams,
    PriceAndTaxHistoryParams,
    PropertyCompsParams,
    PropertyValueRangeParams,
    SimilarPropertiesParams,
    SimilarSalesParams,
    SimilarRentalsParams,
    MarketLocationParams,
    MarketDataParams,
    PropertyResponse,
    PropertySearchResponseModel,
    ZestimateResponse,
    ZestimateHistoryResponse,
    PriceAndTaxHistoryResponse,
    PropertyCompsResponse,
    PropertyValueRangeResponse,
    SimilarPropertyResponse,
    SimilarSalesResponse,
    SimilarRentalsResponse,
    MarketLocationResponse,
    MarketDataResponse,
    ApiResponse
)
from .service import ZillowService
from .client import ZillowClient
from ..common.auth import validate_provider_api_key
from ..common.input_schema_decorator import schema, input_schema, output_schema
from ..common.utils import apply_error_handler_to_service, apply_error_handler_to_router, format_validation_error, apply_error_handler_to_client
from ..common.examples_handler import ExamplesLoader
import os 

router = APIRouter(prefix="/zillow", tags=["zillow"])
examples = ExamplesLoader()
api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)

async def get_zillow_service(request: FastAPIRequest):
    try:
        #api_key = await validate_provider_api_key(request, "zillow")
        api_key = os.getenv("RAPID_API_ZILLOW_KEY")
        client = ZillowClient(api_key)
        apply_error_handler_to_client(client)
        service = ZillowService(client)
        
        apply_error_handler_to_service(service)
        
        return service
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Failed to initialize Zillow service: {str(e)}"
        )

@router.post("/get_property", response_model=ApiResponse)
@schema(
    input_schema_class=PropertyParams,
    output_schema_class=PropertyResponse,
    examples=examples["/zillow/get_property"]
)
async def get_property(
    params: Dict[str, Any] = Body(...),
    service: ZillowService = Depends(get_zillow_service)
):
    validated_params = PropertyParams(**params)
    return service.get_property(validated_params)

@router.post("/search_properties", response_model=ApiResponse)
@schema(
    input_schema_class=PropertySearchParams,
    output_schema_class=PropertySearchResponseModel,
    examples=examples["/zillow/search_properties"]
)
async def search_properties(
    params: Dict[str, Any] = Body(...),
    service: ZillowService = Depends(get_zillow_service)
):
    validated_params = PropertySearchParams(**params)
    return service.search_properties(validated_params)

@router.post("/get_zestimate", response_model=ApiResponse)
@schema(
    input_schema_class=ZestimateParams,
    output_schema_class=ZestimateResponse,
    examples=examples["/zillow/get_zestimate"]
)
async def get_zestimate(
    params: Dict[str, Any] = Body(...),
    service: ZillowService = Depends(get_zillow_service)
):
    validated_params = ZestimateParams(**params)
    return service.get_zestimate(validated_params)

@router.post("/get_zestimate_history", response_model=ApiResponse)
@schema(
    input_schema_class=ZestimateHistoryParams,
    output_schema_class=ZestimateHistoryResponse,
    examples=examples["/zillow/get_zestimate_history"]
)
async def get_zestimate_history(
    params: Dict[str, Any] = Body(...),
    service: ZillowService = Depends(get_zillow_service)
):
    validated_params = ZestimateHistoryParams(**params)
    return service.get_zestimate_history(validated_params)

@router.post("/get_price_and_tax_history", response_model=ApiResponse)
@schema(
    input_schema_class=PriceAndTaxHistoryParams,
    output_schema_class=PriceAndTaxHistoryResponse,
    examples=examples["/zillow/get_price_and_tax_history"]
)
async def get_price_and_tax_history(
    params: Dict[str, Any] = Body(...),
    service: ZillowService = Depends(get_zillow_service)
):
    validated_params = PriceAndTaxHistoryParams(**params)
    return service.get_price_and_tax_history(validated_params)

@router.post("/get_property_comps", response_model=ApiResponse)
@schema(
    input_schema_class=PropertyCompsParams,
    output_schema_class=PropertyCompsResponse,
    examples=examples["/zillow/get_property_comps"]
)
async def get_property_comps(
    params: Dict[str, Any] = Body(...),
    service: ZillowService = Depends(get_zillow_service)
):
    validated_params = PropertyCompsParams(**params)
    return service.get_property_comps(validated_params)

@router.post("/get_property_value_range", response_model=ApiResponse)
@schema(
    input_schema_class=PropertyValueRangeParams,
    output_schema_class=PropertyValueRangeResponse,
    examples=examples["/zillow/get_property_value_range"]
)
async def get_property_value_range(
    params: Dict[str, Any] = Body(...),
    service: ZillowService = Depends(get_zillow_service)
):
    validated_params = PropertyValueRangeParams(**params)
    return service.get_property_value_range(validated_params)

@router.post("/get_similar_properties", response_model=ApiResponse)
@schema(
    input_schema_class=SimilarPropertiesParams,
    output_schema_class=SimilarPropertyResponse
)
async def get_similar_properties(
    params: Dict[str, Any] = Body(...),
    service: ZillowService = Depends(get_zillow_service)
):
    validated_params = SimilarPropertiesParams(**params)
    return service.get_similar_properties(validated_params)

@router.post("/get_similar_sales", response_model=ApiResponse)
@schema(
    input_schema_class=SimilarSalesParams,
    output_schema_class=SimilarSalesResponse
)
async def get_similar_sales(
    params: Dict[str, Any] = Body(...),
    service: ZillowService = Depends(get_zillow_service)
):
    validated_params = SimilarSalesParams(**params)
    return service.get_similar_sales(validated_params)

@router.post("/get_similar_rentals", response_model=ApiResponse)
@schema(
    input_schema_class=SimilarRentalsParams,
    output_schema_class=SimilarRentalsResponse
)
async def get_similar_rentals(
    params: Dict[str, Any] = Body(...),
    service: ZillowService = Depends(get_zillow_service)
):
    validated_params = SimilarRentalsParams(**params)
    return service.get_similar_rentals(validated_params)

@router.post("/get_market_location", response_model=ApiResponse)
@schema(
    input_schema_class=MarketLocationParams,
    output_schema_class=MarketLocationResponse
)
async def get_market_location(
    params: Dict[str, Any] = Body(...),
    service: ZillowService = Depends(get_zillow_service)
):
    validated_params = MarketLocationParams(**params)
    return service.get_market_location(validated_params)

@router.post("/get_market_data", response_model=ApiResponse)
@schema(
    input_schema_class=MarketDataParams,
    output_schema_class=MarketDataResponse
)
async def get_market_data(
    params: Dict[str, Any] = Body(...),
    service: ZillowService = Depends(get_zillow_service)
):
    validated_params = MarketDataParams(**params)
    return service.get_market_data(validated_params)

apply_error_handler_to_router(router)
