from fastapi import APIRouter, Body, Depends, HTTPException
from starlette.requests import Request as FastAPIRequest
from typing import Dict, Any
from .schema import (
    SearchParams,
    ContentsParams,
    FindSimilarParams,
    ApiResponse
)
from .service import ExaService
from .client import ExaClient
from ..common.auth import validate_provider_api_key
from ..common.input_schema_decorator import schema, input_schema, output_schema
from ..common.utils import apply_error_handler_to_service, apply_error_handler_to_router, format_validation_error
from ..common.examples_handler import ExamplesLoader

router = APIRouter(prefix="/exa", tags=["exa"])
examples = ExamplesLoader()

async def get_exa_service(request: FastAPIRequest):
    try:
        api_key = await validate_provider_api_key(request, "exa")
        client = ExaClient(api_key)
        service = ExaService(client)
        
        apply_error_handler_to_service(service)
        
        return service
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Failed to initialize Exa service: {str(e)}"
        )

@router.post("/search", response_model=ApiResponse)
@schema(
    input_schema_class=SearchParams,
    output_schema_class=ApiResponse,
    examples=examples["/exa/search"]
)
async def search(
    params: Dict[str, Any] = Body(...),
    service: ExaService = Depends(get_exa_service)
):
    validated_params = SearchParams(**params)
    return service.search(validated_params)

@router.post("/contents", response_model=ApiResponse)
@schema(
    input_schema_class=ContentsParams,
    output_schema_class=ApiResponse,
    examples=examples["/exa/contents"]
)
async def get_contents(
    params: Dict[str, Any] = Body(...),
    service: ExaService = Depends(get_exa_service)
):
    validated_params = ContentsParams(**params)
    return service.get_contents(validated_params)

@router.post("/find_similar", response_model=ApiResponse)
@schema(
    input_schema_class=FindSimilarParams,
    output_schema_class=ApiResponse,
    examples=examples["/exa/find_similar"]
)
async def find_similar(
    params: Dict[str, Any] = Body(...),
    service: ExaService = Depends(get_exa_service)
):
    validated_params = FindSimilarParams(**params)
    return service.find_similar(validated_params)

@router.post("/validate_key")
async def validate_key(
    params: Dict[str, Any] = Body(...),
):
    try:
        api_key = params.get("api_key")
        if not api_key:
            return {"valid": False, "message": "API key is required"}
        
        client = ExaClient(api_key=api_key)
        test_params = {"query": "test", "numResults": 1}
        test_response = client.search(test_params)
        return {"valid": True, "message": "API key is valid"}
    except Exception as e:
        return {"valid": False, "message": f"Invalid API key"}

apply_error_handler_to_router(router)