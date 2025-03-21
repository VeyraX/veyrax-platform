from fastapi import APIRouter, Depends, Body, HTTPException
from typing import Dict, Any, List
from .schema import (
    ApiResponse,
    CreateVideoInput,
    CreateVideoOutput,
    VideoStatusInput,
    VideoStatusOutput,
    ProjectsListInput,
    ProjectListOutput,
    QueueInput,
    QueueOutput,
    PublishInput,
    PublishOutput
)
from .service import RevidAIService
from .client import RevidAIClient
from ..common.auth import validate_provider_api_key
from ..common.input_schema_decorator import schema
from ..common.utils import format_validation_error, apply_error_handler_to_service, apply_error_handler_to_router, apply_error_handler_to_client
from ..common.examples_handler import ExamplesLoader
from fastapi import Request


router = APIRouter(prefix="/revid", tags=["revid"])
examples = ExamplesLoader()

async def get_revid_service(request: Request):
    try:
        api_key = await validate_provider_api_key(request, "revid")
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
async def create_video(
    params: Dict[str, Any] = Body(...),
    service: RevidAIService = Depends(get_revid_service),
):
    validated_params = CreateVideoInput(**params)
    return service.create_tiktok_video(validated_params)

@router.post("/video_status", response_model=ApiResponse)
@schema(
    input_schema_class=VideoStatusInput,
    output_schema_class=VideoStatusOutput,
    examples=examples["/revid/video_status"]
)
async def video_status(
    params: Dict[str, Any] = Body(...),
    service: RevidAIService = Depends(get_revid_service),
):
    validated_params = VideoStatusInput(**params)
    return service.get_video_status(validated_params)

@router.post("/projects_list", response_model=ApiResponse)
@schema(
    input_schema_class=ProjectsListInput,
    output_schema_class=ProjectListOutput,
    examples=examples["/revid/projects_list"]
)
async def projects_list(
    params: Dict[str, Any] = Body(...),
    service: RevidAIService = Depends(get_revid_service),
):
    validated_params = ProjectsListInput(**params)
    return service.get_projects_list(validated_params)

@router.post("/add_to_queue", response_model=ApiResponse)
@schema(
    input_schema_class=QueueInput,
    output_schema_class=QueueOutput,
    examples=examples["/revid/add_to_queue"]
)
async def add_to_queue(
    params: Dict[str, Any] = Body(...),
    service: RevidAIService = Depends(get_revid_service),
):
    validated_params = QueueInput(**params)
    return service.add_to_queue(validated_params)

@router.post("/publish_now", response_model=ApiResponse)
@schema(
    input_schema_class=PublishInput,
    output_schema_class=PublishOutput,
    examples=examples["/revid/publish_now"]
)
async def publish_now(
    params: Dict[str, Any] = Body(...),
    service: RevidAIService = Depends(get_revid_service),
):
    validated_params = PublishInput(**params)
    return service.publish_video(validated_params)

@router.post("/validate_key")
async def validate_key(
    params: Dict[str, Any] = Body(...),
):
    try:
        api_key = params.get("api_key")
        if not api_key:
            return {"valid": False, "message": "API key is required"}
        
        client = RevidAIClient(api_key=api_key)
        # Test the API connection with a simple request
        test_response = client.get_projects(limit=1)
        if test_response.status_code == 200:
            return {"valid": True, "message": "API key is valid"}
        return {"valid": False, "message": "Invalid API key"}
    except Exception as e:
        return {"valid": False, "message": f"Invalid API key: {str(e)}"}

apply_error_handler_to_router(router)
