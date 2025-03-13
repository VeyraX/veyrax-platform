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
from ..common.utils import format_validation_error
from ..common.examples_handler import ExamplesLoader

router = APIRouter(prefix="/tavily", tags=["tavily"])
examples = ExamplesLoader()

async def get_tavily_service(request: Request):
    try:
        api_key = await validate_provider_api_key(request, "tavily")
        return TavilyService(TavilyClient(api_key))
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
    try:
        validated_params = SearchParams(**params)
        return service.search(validated_params)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'SearchParams'))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
    try:
        validated_params = ExtractParams(**params)
        return service.extract(validated_params)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'ExtractParams'))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 