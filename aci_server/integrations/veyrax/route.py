from fastapi import APIRouter, Body, Depends, HTTPException, Request as FastAPIRequest
from typing import Dict, Any, Optional
from pydantic import ValidationError

from integrations.common.auth import get_user_from_request
from integrations.common.utils import format_validation_error, apply_error_handler_to_service, apply_error_handler_to_router, apply_error_handler_to_client
from integrations.common.examples_handler import ExamplesLoader
from integrations.common.input_schema_decorator import schema
from integrations.veyrax.schema import (
    SaveMemoryParams, GetMemoriesParams, UpdateMemoryParams, DeleteMemoryParams,
    SaveMemoryResponse, GetMemoriesResponse, UpdateMemoryResponse, DeleteMemoryResponse,
    ApiResponse
)
from integrations.veyrax.client import VeyraxMemoryClient
from integrations.veyrax.services import VeyraxMemoryService

router = APIRouter(prefix="/veyrax", tags=["veyrax"])

examples = ExamplesLoader()

async def get_veyrax_memory_service(request: FastAPIRequest):
    try:
        user_id = await get_user_from_request(request)
        client = VeyraxMemoryClient(user_id)
        apply_error_handler_to_client(client)
        service = VeyraxMemoryService(client)
        apply_error_handler_to_service(service)
        return service
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize service: {str(e)}")

@router.post("/save_memory", response_model=ApiResponse)
@schema(input_schema_class=SaveMemoryParams, output_schema_class=SaveMemoryResponse, examples=examples["/veyrax/save_memory"])
async def save_memory(
    params: Dict[str, Any] = Body(...),
    service: VeyraxMemoryService = Depends(get_veyrax_memory_service)
):
    validated_params = SaveMemoryParams(**params)
    
    return service.save_memory(
        memory=validated_params.memory,
        tool=validated_params.tool
    )

@router.post("/get_memory", response_model=ApiResponse)
@schema(input_schema_class=GetMemoriesParams, output_schema_class=GetMemoriesResponse, examples=examples["/veyrax/get_memory"])
async def get_memory(
    params: Dict[str, Any] = Body(...),
    service: VeyraxMemoryService = Depends(get_veyrax_memory_service)
):
    validated_params = GetMemoriesParams(**params)
    return service.get_memories(
        tool=validated_params.tool,
        limit=validated_params.limit,
        offset=validated_params.offset
    )

@router.post("/update_memory", response_model=ApiResponse)
@schema(input_schema_class=UpdateMemoryParams, output_schema_class=UpdateMemoryResponse, examples=examples["/veyrax/update_memory"])
async def update_memory(
    params: Dict[str, Any] = Body(...),
    service: VeyraxMemoryService = Depends(get_veyrax_memory_service)
):
    validated_params = UpdateMemoryParams(**params)
    return service.update_memory(
        id=validated_params.id,
        memory=validated_params.memory,
        tool=validated_params.tool
    )

@router.post("/delete_memory", response_model=ApiResponse)
@schema(input_schema_class=DeleteMemoryParams, output_schema_class=DeleteMemoryResponse, examples=examples["/veyrax/delete_memory"])
async def delete_memory(
    params: Dict[str, Any] = Body(...),
    service: VeyraxMemoryService = Depends(get_veyrax_memory_service)
):
    validated_params = DeleteMemoryParams(**params)
    return service.delete_memory(id=validated_params.id)

apply_error_handler_to_router(router)
