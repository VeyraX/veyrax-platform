from fastapi import APIRouter, Depends, HTTPException, Request, Body
from typing import Dict, Any
from .schema import CompletionRequest, ApiResponse, CompletionResponseSchema
from .service import PerplexityService
from .client import PerplexityClient
from ..common.auth import validate_provider_api_key
from ..common.input_schema_decorator import schema, input_schema, output_schema
from pydantic import ValidationError
from ..common.utils import format_validation_error, apply_error_handler_to_service, apply_error_handler_to_router, apply_error_handler_to_client
from ..common.examples_handler import ExamplesLoader
import os
from requests import HTTPError

router = APIRouter(prefix="/perplexity", tags=["perplexity"])

examples = ExamplesLoader() 

async def get_perplexity_service(request: Request):
    try:
        api_key = await validate_provider_api_key(request, "perplexity")
        client = PerplexityClient(api_key)
        apply_error_handler_to_client(client)
        service = PerplexityService(client)
        apply_error_handler_to_service(service)
        return service
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize Perplexity service: {str(e)}")

@router.post("/create_completion", response_model=ApiResponse)
@schema(input_schema_class=CompletionRequest, output_schema_class=CompletionResponseSchema, examples=examples["/perplexity/create_completion"])
async def create_completion(
    params: Dict[str, Any] = Body(...),
    service: PerplexityService = Depends(get_perplexity_service)
):
    validated_params = CompletionRequest(**params)
    return service.create_completion(validated_params)

@router.post("/validate_key")
async def validate_key(
    params: Dict[str, Any] = Body(...),
):
    try:
        api_key = params.get("api_key")
        if not api_key:
            return {"valid": False, "message": "API key is required"}
        
        client = PerplexityClient(api_key=api_key)
        test_response = client.create_completion(
            messages=[{"role": "user", "content": "Hello"}],
            model="sonar",
            max_tokens=5
        )
        return {"valid": True, "message": "API key is valid"}
    except Exception as e:
        return {"valid": False, "message": f"Invalid API key"}

apply_error_handler_to_router(router)