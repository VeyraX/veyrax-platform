from fastapi import APIRouter, Body, Depends, HTTPException
from starlette.requests import Request as FastAPIRequest
from typing import Dict, Any
from .schema import (
    SearchParams,
    GeneratePromptParams,
    ApiResponse,
    SearchResponse,
    PromptResponse
)
from .service import TwentyFirstDevService
from .client import TwentyFirstDevClient
from ..common.auth import validate_provider_api_key
from ..common.input_schema_decorator import schema
from ..common.utils import apply_error_handler_to_service, apply_error_handler_to_router, apply_error_handler_to_client
from ..common.examples_handler import ExamplesLoader

router = APIRouter(prefix="/twentyfirst_dev", tags=["twentyfirst_dev"])
examples = ExamplesLoader()

async def get_21st_dev_service(request: FastAPIRequest):
    try:
        api_key = await validate_provider_api_key(request, "twentyfirst_dev")
        client = TwentyFirstDevClient(api_key)
        apply_error_handler_to_client(client)
        service = TwentyFirstDevService(client)
        
        apply_error_handler_to_service(service)
        
        return service
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Failed to initialize twentyfirst.dev service: {str(e)}"
        )

@router.post("/search", response_model=ApiResponse)
@schema(
    input_schema_class=SearchParams,
    output_schema_class=SearchResponse,
    examples=examples["/twentyfirst_dev/search"]
)
async def search(
    params: Dict[str, Any] = Body(...),
    service: TwentyFirstDevService = Depends(get_21st_dev_service)
):
    validated_params = SearchParams(**params)
    return service.search(validated_params)

@router.post("/generate_prompt", response_model=ApiResponse)
@schema(
    input_schema_class=GeneratePromptParams,
    output_schema_class=PromptResponse,
    examples=examples["/twentyfirst_dev/generate_prompt"]
)
async def generate_prompt(
    params: Dict[str, Any] = Body(...),
    service: TwentyFirstDevService = Depends(get_21st_dev_service)
):
    validated_params = GeneratePromptParams(**params)
    return service.generate_prompt(validated_params)

@router.post("/validate_key")
async def validate_key(
    params: Dict[str, Any] = Body(...),
):
    try:
        api_key = params.get("api_key")
        if not api_key:
            return {"valid": False, "message": "API key is required"}
        
        client = TwentyFirstDevClient(api_key=api_key)
        test_params = {"search": "test component", "page": 1, "per_page": 1}
        client.search(test_params)
        return {"valid": True, "message": "API key is valid"}
    except Exception as e:
        return {"valid": False, "message": "Invalid API key"}

apply_error_handler_to_router(router)
