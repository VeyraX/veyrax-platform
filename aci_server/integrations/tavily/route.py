from fastapi import APIRouter, Depends, Body, HTTPException, Request
from typing import Dict, Any
from .schema import (
    SearchParams, 
    ExtractParams, 
    ApiResponse
)
from .service import TavilyService
from .client import TavilyClient
from ..common.auth import validate_provider_api_key
from ..common.input_schema_decorator import schema
from pydantic import ValidationError
from ..common.utils import format_validation_error, apply_error_handler_to_service, apply_error_handler_to_router
from ..common.examples_handler import ExamplesLoader

router = APIRouter(prefix="/tavily", tags=["tavily"])
examples = ExamplesLoader()

async def get_tavily_service(request: Request):
    try:
        api_key = await validate_provider_api_key(request, "tavily")
        client = TavilyClient(api_key)
        service = TavilyService(client)
        apply_error_handler_to_service(service)
        return service
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tavily service initialization failed: {str(e)}")

@router.post("/search", response_model=ApiResponse)
@schema(
    input_schema_class=SearchParams,
    output_schema_class=ApiResponse,
    examples=examples["/tavily/search"]
)
async def search(
    params: Dict[str, Any] = Body(...),
    service: TavilyService = Depends(get_tavily_service),
):
    validated_params = SearchParams(**params)
    return service.search(validated_params)

@router.post("/extract", response_model=ApiResponse)
@schema(
    input_schema_class=ExtractParams,
    output_schema_class=ApiResponse,
    examples=examples["/tavily/extract"]
)
async def extract(
    params: Dict[str, Any] = Body(...),
    service: TavilyService = Depends(get_tavily_service)
):
    validated_params = ExtractParams(**params)
    return service.extract(validated_params)

@router.post("/validate_key")
async def validate_key(
    params: Dict[str, Any] = Body(...),
):
    try:
        api_key = params.get("api_key")
        if not api_key:
            return {"valid": False, "message": "API key is required"}
        
        client = TavilyClient(api_key=api_key)
        test_params = {"query": "test", "max_results": 1}
        test_response = client.search(test_params)
        return {"valid": True, "message": "API key is valid"}
    except Exception as e:
        return {"valid": False, "message": f"Invalid API key"}

apply_error_handler_to_router(router)