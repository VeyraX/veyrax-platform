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
from ..common.utils import format_validation_error, apply_error_handler_to_service, apply_error_handler_to_router, apply_error_handler_to_client
from ..common.examples_handler import ExamplesLoader
from fastapi import Request


router = APIRouter(prefix="/brave", tags=["brave"])
examples = ExamplesLoader()

async def get_brave_service(request: Request):
    try:
        api_key = await validate_provider_api_key(request, "brave")
        service = BraveService(BraveClient(api_key))
        apply_error_handler_to_service(service)
        return service
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Brave service initialization failed: {str(e)}")

@router.post("/web_search", response_model=ApiResponse)
@schema(
    input_schema_class=WebSearchParams,
    output_schema_class=ApiResponse,
    examples=examples["/brave/web_search"]
)
async def web_search(
    params: Dict[str, Any] = Body(...),
    service: BraveService = Depends(get_brave_service),
):
    validated_params = WebSearchParams(**params)
    return service.web_search(validated_params)

@router.post("/images_search", response_model=ApiResponse)
@schema(
    input_schema_class=ImageSearchParams,
    output_schema_class=ApiResponse,
    examples=examples["/brave/images_search"]
)
async def image_search(
    params: Dict[str, Any] = Body(...),
    service: BraveService = Depends(get_brave_service)
):
    validated_params = ImageSearchParams(**params)
    return service.image_search(validated_params)

@router.post("/videos_search", response_model=ApiResponse)
@schema(input_schema_class=VideoSearchParams, output_schema_class=ApiResponse, examples=examples["/brave/videos_search"])
async def video_search(
    params: Dict[str, Any] = Body(...),
    service: BraveService = Depends(get_brave_service)
):
    validated_params = VideoSearchParams(**params)
    return service.video_search(validated_params)

@router.post("/news_search", response_model=ApiResponse)
@schema(input_schema_class=NewsSearchParams, output_schema_class=ApiResponse, examples=examples["/brave/news_search"])
async def news_search(
    params: Dict[str, Any] = Body(...),
    service: BraveService = Depends(get_brave_service)
):
    validated_params = NewsSearchParams(**params)
    return service.news_search(validated_params)

@router.post("/validate_key")
async def validate_key(
    params: Dict[str, Any] = Body(...),
):
    try:
        api_key = params.get("api_key", "")
        if not api_key:
            return {"valid": False, "message": "API key is required"}
        
        client = BraveClient(api_key)
        apply_error_handler_to_client(client)
        test_params = {"q": "test", "count": 1}
        client.web_search(test_params)
        
        return {"valid": True, "message": "API key is valid"}
    except Exception as e:
        return {"valid": False, "message": f"Invalid API key"}

apply_error_handler_to_router(router)