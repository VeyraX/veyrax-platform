from fastapi import APIRouter, Depends, Body, HTTPException
from typing import Dict, Any, List
from .schema import (
    WebSearchParams, 
    ImageSearchParams,
    VideoSearchParams, 
    NewsSearchParams,
    ApiResponse
)
from .service import BraveService
from .client import BraveClient
from ..common.auth import validate_provider_api_key
from ..common.input_schema_decorator import schema
from pydantic import ValidationError
from ..common.utils import format_validation_error
from ..common.examples_handler import ExamplesLoader
from fastapi import Request


router = APIRouter(prefix="/brave", tags=["brave"])
examples = ExamplesLoader()

async def get_brave_service(request: Request):
    try:
        api_key = await validate_provider_api_key(request, "brave")
        return BraveService(BraveClient(api_key))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Brave service initialization failed: {str(e)}")

@router.post("/web_search", response_model=ApiResponse)
@schema(
    input_schema_class=WebSearchParams,
    output_schema_class=ApiResponse,
    examples=examples["web_search"]
)
async def web_search(
    params: Dict[str, Any] = Body(...),
    service: BraveService = Depends(get_brave_service)
):
    try:
        print("web_search params", params)
        validated_params = WebSearchParams(**params)
        print("web_search validated_params", validated_params)
        return service.web_search(validated_params)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'WebSearchParams'))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/images_search", response_model=ApiResponse)
@schema(
    input_schema_class=ImageSearchParams,
    output_schema_class=ApiResponse,
    examples=examples["images_search"]
)
async def image_search(
    params: Dict[str, Any] = Body(...),
    service: BraveService = Depends(get_brave_service)
):
    try:
        print("image_search params", params)
        validated_params = ImageSearchParams(**params)
        print("image_search validated_params", validated_params)
        return service.image_search(validated_params)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'ImageSearchParams'))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/videos_search", response_model=ApiResponse)
@schema(input_schema_class=VideoSearchParams, output_schema_class=ApiResponse, examples=examples["/brave/videos_search"])
async def video_search(
    params: Dict[str, Any] = Body(...),
    service: BraveService = Depends(get_brave_service)
):
    try:
        validated_params = VideoSearchParams(**params)
        return service.video_search(validated_params)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'VideoSearchParams'))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/news_search", response_model=ApiResponse)
@schema(input_schema_class=NewsSearchParams, output_schema_class=ApiResponse, examples=examples["/brave/news_search"])
async def news_search(
    params: Dict[str, Any] = Body(...),
    service: BraveService = Depends(get_brave_service)
):
    try:
        validated_params = NewsSearchParams(**params)
        return service.news_search(validated_params)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'NewsSearchParams'))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 