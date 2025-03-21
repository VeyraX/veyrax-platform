from fastapi import APIRouter, Depends, Body, HTTPException
from typing import Dict, Any, List
from .schema import (
    ApiResponse,
    CreateVideoInput,
    CreateVideoOutput
)
from .service import RevidAIService
from .client import RevidAIClient
from ..common.auth import validate_provider_api_key
from ..common.input_schema_decorator import schema
from ..common.utils import format_validation_error, apply_error_handler_to_service, apply_error_handler_to_router, apply_error_handler_to_client
from ..common.examples_handler import ExamplesLoader
from fastapi import Request


router = APIRouter(prefix="/brave", tags=["brave"])
examples = ExamplesLoader()

async def get_revid_service(request: Request):
    try:
        api_key = await validate_provider_api_key(request, "brave")
        client = RevidAIClient(api_key)
        apply_error_handler_to_client(client)
        service = RevidAIService(client)
        apply_error_handler_to_service(service)
        return service
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Revid AI service initialization failed: {str(e)}")

@router.post("/create_video", response_model=ApiResponse)
@schema(
    input_schema_class=CreateVideoInput,
    output_schema_class=CreateVideoOutput,
    examples=examples["/revid/create_video"]
)
async def web_search(
    params: Dict[str, Any] = Body(...),
    service: AmazonService = Depends(get_amazon_service),
):
    validated_params = AmazonSearchParam(**params)
    return service.search_items(validated_params)
