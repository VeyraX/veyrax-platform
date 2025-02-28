from fastapi import APIRouter, Depends, HTTPException, Request, Body
from typing import Dict, Any
from .schema import CompletionRequest, ApiResponse, CompletionResponseSchema
from .service import PerplexityService
from .client import PerplexityClient
from ..common.auth import validate_provider_api_key
from ..common.input_schema_decorator import schema, input_schema, output_schema
from pydantic import ValidationError
from ..common.utils import format_validation_error
import os

router = APIRouter(prefix="/perplexity", tags=["perplexity"])

async def get_perplexity_service(request: Request):
    try:
        api_key = await validate_provider_api_key(request, "perplexity")
        client = PerplexityClient(api_key)
        return PerplexityService(client)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize Perplexity service: {str(e)}")

@router.post("/create_completion", response_model=ApiResponse)
@schema(input_schema_class=CompletionRequest, output_schema_class=CompletionResponseSchema)
async def create_completion(
    params: Dict[str, Any] = Body(...),
    service: PerplexityService = Depends(get_perplexity_service)
):
    try:
        validated_params = CompletionRequest(**params)
        return service.create_completion(validated_params)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'CompletionRequest'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))