from fastapi import APIRouter, Body, Depends, HTTPException, Request as FastAPIRequest
from typing import Dict, Any, Optional
from pydantic import ValidationError

from integrations.common.auth import get_user_from_request
from integrations.common.utils import format_validation_error
from integrations.common.examples_handler import ExamplesLoader
from integrations.common.input_schema_decorator import schema
from .schema import (
    SaveMemoryParams, GetMemoriesParams, UpdateMemoryParams, DeleteMemoryParams,
    SaveMemoryResponse, GetMemoriesResponse, UpdateMemoryResponse, DeleteMemoryResponse,
    ApiResponse
)
from .client import VeryraxMemoryClient
from .services import VeryraxMemoryService

router = APIRouter(prefix="/veyrax", tags=["veyrax"])

examples = ExamplesLoader()

async def get_veryrax_memory_service(request: FastAPIRequest):
    try:
        user_id = await get_user_from_request(request)
        client = VeryraxMemoryClient(user_id)
        return VeryraxMemoryService(client)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize service: {str(e)}")

@router.post("/save_memory", response_model=ApiResponse)
@schema(input_schema_class=SaveMemoryParams, output_schema_class=SaveMemoryResponse, examples=examples["/veyrax/save_memory"])
async def save_memory(
    params: Dict[str, Any] = Body(...),
    service: VeryraxMemoryService = Depends(get_veryrax_memory_service)
):
    try:
        print("SAVE_MEMORY RECEIVED PARAMS:", params)
        print("PARAMS TYPE:", type(params))
        print("PARAMS KEYS:", list(params.keys()))
        
        validated_params = SaveMemoryParams(**params)
        print("VALIDATED PARAMS:", validated_params.dict())
        
        return service.save_memory(
            memory=validated_params.memory,
            tool=validated_params.tool
        )
    except ValidationError as e:
        print("VALIDATION ERROR:", e)
        print("ERROR JSON:", e.json())
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'SaveMemoryParams'))
    except Exception as e:
        print("GENERAL ERROR:", str(e))
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_memory", response_model=ApiResponse)
@schema(input_schema_class=GetMemoriesParams, output_schema_class=GetMemoriesResponse, examples=examples["/veyrax/get_memory"])
async def get_memory(
    params: Dict[str, Any] = Body(...),
    service: VeryraxMemoryService = Depends(get_veryrax_memory_service)
):
    try:
        validated_params = GetMemoriesParams(**params)
        return service.get_memories(
            tool=validated_params.tool,
            limit=validated_params.limit,
            offset=validated_params.offset
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetMemoriesParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update_memory", response_model=ApiResponse)
@schema(input_schema_class=UpdateMemoryParams, output_schema_class=UpdateMemoryResponse, examples=examples["/veyrax/update_memory"])
async def update_memory(
    params: Dict[str, Any] = Body(...),
    service: VeryraxMemoryService = Depends(get_veryrax_memory_service)
):
    try:
        validated_params = UpdateMemoryParams(**params)
        return service.update_memory(
            id=validated_params.id,
            memory=validated_params.memory,
            tool=validated_params.tool
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'UpdateMemoryParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/delete_memory", response_model=ApiResponse)
@schema(input_schema_class=DeleteMemoryParams, output_schema_class=DeleteMemoryResponse, examples=examples["/veyrax/delete_memory"])
async def delete_memory(
    params: Dict[str, Any] = Body(...),
    service: VeryraxMemoryService = Depends(get_veryrax_memory_service)
):
    try:
        validated_params = DeleteMemoryParams(**params)
        return service.delete_memory(id=validated_params.id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'DeleteMemoryParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
