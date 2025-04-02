from fastapi import APIRouter, Body, Depends, HTTPException
from starlette.requests import Request as FastAPIRequest
from typing import Dict, Any
from .schema import (
    ModelsParams,
    SearchModelParams,
    SchemaModelParams,
    GenerateParams,
    ResultParams,
    StatusParams,
    CancelParams,
    UploadParams,
    ApiResponse,
    ModelsResponse,
    SchemaResponse,
    GenerateResponse,
    ResultResponse,
    StatusResponse,
    CancelResponse,
    UploadResponse
)
from .service import FalAIService
from .client import FalAIClient
from ..common.auth import validate_provider_api_key
from ..common.input_schema_decorator import schema, input_schema, output_schema
from ..common.utils import apply_error_handler_to_service, apply_error_handler_to_router, format_validation_error, apply_error_handler_to_client
from ..common.examples_handler import ExamplesLoader

router = APIRouter(prefix="/falai", tags=["falai"])
examples = ExamplesLoader()

async def get_falai_service(request: FastAPIRequest):
    try:
        api_key = await validate_provider_api_key(request, "falai")
        client = FalAIClient(api_key)
        apply_error_handler_to_client(client)
        service = FalAIService(client)
        
        apply_error_handler_to_service(service)
        
        return service
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Failed to initialize FalAI service: {str(e)}"
        )

@router.post("/get_models", response_model=ApiResponse)
@schema(
    input_schema_class=ModelsParams,
    output_schema_class=ModelsResponse
)
async def get_models(
    params: Dict[str, Any] = Body(...),
    service: FalAIService = Depends(get_falai_service)
):
    validated_params = ModelsParams(**params)
    return await service.get_models(validated_params)

@router.post("/search_models", response_model=ApiResponse)
@schema(
    input_schema_class=SearchModelParams,
    output_schema_class=ModelsResponse
)
async def search_models(
    params: Dict[str, Any] = Body(...),
    service: FalAIService = Depends(get_falai_service)
):
    validated_params = SearchModelParams(**params)
    return await service.search_models(validated_params)

@router.post("/get_schema", response_model=ApiResponse)
@schema(
    input_schema_class=SchemaModelParams,
    output_schema_class=SchemaResponse
)
async def get_schema(
    params: Dict[str, Any] = Body(...),
    service: FalAIService = Depends(get_falai_service)
):
    validated_params = SchemaModelParams(**params)
    return await service.get_schema(validated_params)

@router.post("/generate", response_model=ApiResponse)
@schema(
    input_schema_class=GenerateParams,
    output_schema_class=GenerateResponse
)
async def generate(
    params: Dict[str, Any] = Body(...),
    service: FalAIService = Depends(get_falai_service)
):
    validated_params = GenerateParams(**params)
    return await service.generate(validated_params)

@router.post("/get_result", response_model=ApiResponse)
@schema(
    input_schema_class=ResultParams,
    output_schema_class=ResultResponse
)
async def get_result(
    params: Dict[str, Any] = Body(...),
    service: FalAIService = Depends(get_falai_service)
):
    validated_params = ResultParams(**params)
    return await service.get_result(validated_params)

@router.post("/get_status", response_model=ApiResponse)
@schema(
    input_schema_class=StatusParams,
    output_schema_class=StatusResponse
)
async def get_status(
    params: Dict[str, Any] = Body(...),
    service: FalAIService = Depends(get_falai_service)
):
    validated_params = StatusParams(**params)
    return await service.get_status(validated_params)

@router.post("/cancel", response_model=ApiResponse)
@schema(
    input_schema_class=CancelParams,
    output_schema_class=CancelResponse
)
async def cancel(
    params: Dict[str, Any] = Body(...),
    service: FalAIService = Depends(get_falai_service)
):
    validated_params = CancelParams(**params)
    return await service.cancel_request(validated_params)

@router.post("/upload", response_model=ApiResponse)
@schema(
    input_schema_class=UploadParams,
    output_schema_class=UploadResponse
)
async def upload(
    params: Dict[str, Any] = Body(...),
    service: FalAIService = Depends(get_falai_service)
):
    validated_params = UploadParams(**params)
    return await service.upload_file(validated_params)

@router.post("/validate_key")
async def validate_key(
    params: Dict[str, Any] = Body(...)
):
    try:
        api_key = params.get("api_key")
        if not api_key:
            return {"valid": False, "message": "API key is required"}
        
        client = FalAIClient(api_key=api_key)

        await client.get_models(page=1, total=1)
        
        return {"valid": True, "message": "API key is valid"}
    except Exception as e:
        return {"valid": False, "message": f"Invalid API key: {str(e)}"}

apply_error_handler_to_router(router)
