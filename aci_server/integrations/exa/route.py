from fastapi import APIRouter, Depends, Body, HTTPException, Request
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
from ..common.input_schema_decorator import schema
from pydantic import ValidationError
from ..common.utils import format_validation_error
from ..common.examples_handler import ExamplesLoader

router = APIRouter(prefix="/exa", tags=["exa"])
examples = ExamplesLoader()

async def get_exa_service(request: Request):
    try:
        api_key = await validate_provider_api_key(request, "exa")
        return ExaService(ExaClient(api_key))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Exa service initialization failed: {str(e)}")

@router.post("/search", response_model=ApiResponse)
@schema(
    input_schema_class=SearchParams,
    output_schema_class=ApiResponse,
    examples=examples["search"]
)
async def search(
    params: Dict[str, Any] = Body(...),
    service: ExaService = Depends(get_exa_service)
):
    try:
        validated_params = SearchParams(**params)
        return service.search(validated_params)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'SearchParams'))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/contents", response_model=ApiResponse)
@schema(
    input_schema_class=ContentsParams,
    output_schema_class=ApiResponse,
    examples=examples["contents"]
)
async def get_contents(
    params: Dict[str, Any] = Body(...),
    service: ExaService = Depends(get_exa_service)
):
    try:
        validated_params = ContentsParams(**params)
        return service.get_contents(validated_params)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'ContentsParams'))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/find_similar", response_model=ApiResponse)
@schema(
    input_schema_class=FindSimilarParams,
    output_schema_class=ApiResponse,
    examples=examples["find_similar"]
)
async def find_similar(
    params: Dict[str, Any] = Body(...),
    service: ExaService = Depends(get_exa_service)
):
    try:
        validated_params = FindSimilarParams(**params)
        return service.find_similar(validated_params)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'FindSimilarParams'))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))