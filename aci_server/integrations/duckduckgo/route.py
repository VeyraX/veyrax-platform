from fastapi import APIRouter, Body, Depends, HTTPException
from starlette.requests import Request as FastAPIRequest
from typing import Dict, Any
from .schema import (
    SearchParams,
    ContentParams,
    SearchResponse,
    ContentResponse,
    ApiResponse
)
from .service import DuckDuckGoService
from .client import DuckDuckGoClient
from ..common.input_schema_decorator import schema
from ..common.utils import apply_error_handler_to_service, apply_error_handler_to_router
from ..common.examples_handler import ExamplesLoader

router = APIRouter(prefix="/duckduckgo", tags=["duckduckgo"])
examples = ExamplesLoader()

async def get_duckduckgo_service(request: FastAPIRequest):
    client = DuckDuckGoClient()
    service = DuckDuckGoService(client)
    apply_error_handler_to_service(service)
    return service

@router.post("/search", response_model=ApiResponse)
@schema(
    input_schema_class=SearchParams,
    output_schema_class=SearchResponse,
    examples=examples["/duckduckgo/search"]
)
async def search(
    params: Dict[str, Any] = Body(...),
    service: DuckDuckGoService = Depends(get_duckduckgo_service)
):
    validated_params = SearchParams(**params)
    return service.search(validated_params)

@router.post("/fetch_content", response_model=ApiResponse)
@schema(
    input_schema_class=ContentParams,
    output_schema_class=ContentResponse,
    examples=examples["/duckduckgo/fetch_content"]
)
async def fetch_content(
    params: Dict[str, Any] = Body(...),
    service: DuckDuckGoService = Depends(get_duckduckgo_service)
):
    validated_params = ContentParams(**params)
    return service.fetch_content(validated_params)

apply_error_handler_to_router(router)
