from fastapi import APIRouter, Depends, Body, HTTPException
from typing import Dict, Any, List
from .schema import (
    ApiResponse,
    AmazonSearchParam,
    AmazonSearchResponse
)
from .service import AmazonService
from .client import AmazonClient
from ..common.auth import validate_provider_api_key
from ..common.input_schema_decorator import schema
from ..common.utils import format_validation_error, apply_error_handler_to_service, apply_error_handler_to_router, apply_error_handler_to_client
from ..common.examples_handler import ExamplesLoader
from fastapi import Request


router = APIRouter(prefix="/brave", tags=["brave"])
examples = ExamplesLoader()

async def get_amazon_service(request: Request):
    try:
        params = await get_amazon_service(request, "amazon")
        client = AmazonClient(**params)
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
async def web_search(
    params: Dict[str, Any] = Body(...),
    service: AmazonService = Depends(get_amazon_service),
):
    validated_params = AmazonSearchParam(**params)
    return service.search_items(validated_params)
