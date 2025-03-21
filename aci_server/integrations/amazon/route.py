from fastapi import APIRouter, Depends, Body, HTTPException
from typing import Dict, Any, List
from .schema import (
    ApiResponse,
    AmazonSearchParam,
    AmazonSearchResponse,
    AmazonGetItemsParam,
    AmazonItemsResponse,
    AmazonGetVariationsParam,
    AmazonVariationsResponse,
    AmazonGetBrowseNodesParam,
    AmazonBrowseNodesResponse,
    AmazonGetAsinParam,
    AmazonAsinResponse
)
from .service import AmazonService
from .client import AmazonClient
from ..common.auth import get_provider_custom_auth
from ..common.input_schema_decorator import schema
from ..common.utils import format_validation_error, apply_error_handler_to_service, apply_error_handler_to_router, apply_error_handler_to_client
from ..common.examples_handler import ExamplesLoader
from fastapi import Request


router = APIRouter(prefix="/amazon", tags=["amazon"])
examples = ExamplesLoader()

async def get_amazon_service(request: Request):
    try:
        auth_params = await get_provider_custom_auth(request, "amazon")
        
        # Filter only the parameters AmazonClient expects
        client_params = {
            "access_key": auth_params.get("access_key"),
            "secret_key": auth_params.get("secret_key"),
            "associate_tag": auth_params.get("associate_tag"),
        }
        
        # Add country only if it exists in auth_params
        if "country" in auth_params:
            client_params["country"] = auth_params.get("country")
            
        # Add throttling if specified
        if "throttling" in auth_params:
            client_params["throttling"] = auth_params.get("throttling")
        
        # Validate required parameters
        if not client_params.get("access_key") or not client_params.get("secret_key") or not client_params.get("associate_tag"):
            raise ValueError("Missing required Amazon API credentials: access_key, secret_key, or associate_tag")
            
        client = AmazonClient(**client_params)
        apply_error_handler_to_client(client)
        service = AmazonService(client)
        apply_error_handler_to_service(service)
        return service
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Amazon service initialization failed: {str(e)}")

@router.post("/search_items", response_model=ApiResponse)
@schema(
    input_schema_class=AmazonSearchParam,
    output_schema_class=AmazonSearchResponse,
    examples=examples["/amazon/search_items"]
)
async def search_items(
    params: Dict[str, Any] = Body(...),
    service: AmazonService = Depends(get_amazon_service),
):
    validated_params = AmazonSearchParam(**params)
    return service.search_items(validated_params)

@router.post("/get_items", response_model=ApiResponse)
@schema(
    input_schema_class=AmazonGetItemsParam,
    output_schema_class=AmazonItemsResponse,
    examples=examples["/amazon/get_items"]
)
async def get_items(
    params: Dict[str, Any] = Body(...),
    service: AmazonService = Depends(get_amazon_service),
):
    validated_params = AmazonGetItemsParam(**params)
    return service.get_items(validated_params)

@router.post("/get_variations", response_model=ApiResponse)
@schema(
    input_schema_class=AmazonGetVariationsParam,
    output_schema_class=AmazonVariationsResponse,
    examples=examples["/amazon/get_variations"]
)
async def get_variations(
    params: Dict[str, Any] = Body(...),
    service: AmazonService = Depends(get_amazon_service),
):
    validated_params = AmazonGetVariationsParam(**params)
    return service.get_variations(validated_params)

@router.post("/get_browse_nodes", response_model=ApiResponse)
@schema(
    input_schema_class=AmazonGetBrowseNodesParam,
    output_schema_class=AmazonBrowseNodesResponse,
    examples=examples["/amazon/get_browse_nodes"]
)
async def get_browse_nodes(
    params: Dict[str, Any] = Body(...),
    service: AmazonService = Depends(get_amazon_service),
):
    validated_params = AmazonGetBrowseNodesParam(**params)
    return service.get_browse_nodes(validated_params)

@router.post("/get_asin_from_url", response_model=ApiResponse)
@schema(
    input_schema_class=AmazonGetAsinParam,
    output_schema_class=AmazonAsinResponse,
    examples=examples["/amazon/get_asin_from_url"]
)
async def get_asin_from_url(
    params: Dict[str, Any] = Body(...),
    service: AmazonService = Depends(get_amazon_service),
):
    validated_params = AmazonGetAsinParam(**params)
    return service.get_asin_from_url(validated_params)

@router.post("/validate_key")
async def validate_key(
    params: Dict[str, Any] = Body(...),
):
    try:
        access_key = params.get("access_key")
        secret_key = params.get("secret_key")
        associate_tag = params.get("associate_tag")
        country = params.get("country", "US")
        
        if not access_key or not secret_key or not associate_tag:
            return {"valid": False, "message": "Access key, secret key, and associate tag are required"}
        
        client = AmazonClient(
            access_key=access_key,
            secret_key=secret_key,
            associate_tag=associate_tag,
            country=country
        )
        
        # Test the API key with a simple search
        client.search_items("test")
        return {"valid": True, "message": "API credentials are valid"}
    except Exception as e:
        return {"valid": False, "message": f"Invalid API credentials: {str(e)}"}

apply_error_handler_to_router(router)
