from fastapi import APIRouter, Depends, HTTPException, Request as FastAPIRequest, Body
from typing import Dict, Any, List
from .schema import (
    RunTaskParams, TaskIdParams, ApiResponse,
    RunTaskResponse, StopTaskResponse, PauseTaskResponse, ResumeTaskResponse,
    GetTaskResponse, GetTaskStatusResponse, GetTaskMediaResponse, ListTasksResponse,
    CheckBalanceResponse, MeResponse, PingResponse
)
from .service import BrowserUseService
from .client import BrowserUseClient
import os
from ..common.auth import validate_provider_api_key
from ..common.input_schema_decorator import schema
from pydantic import ValidationError
from ..common.utils import format_validation_error
from ..common.examples_handler import ExamplesLoader

router = APIRouter(prefix="/browser-use", tags=["browser-use"])

examples = ExamplesLoader()

async def get_browser_use_service(request: FastAPIRequest):
    try:
        api_key = await validate_provider_api_key(request, "browser-use")
        client = BrowserUseClient(api_key)
        return BrowserUseService(client)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to initialize service: {str(e)}")

@router.post("/run_task", response_model=ApiResponse)
@schema(input_schema_class=RunTaskParams, output_schema_class=RunTaskResponse, examples=examples["/browser-use/run_task"])
async def run_task(
    params: Dict[str, Any] = Body(...),
    service: BrowserUseService = Depends(get_browser_use_service)
):
    try:
        validated_params = RunTaskParams(**params)
        return service.run_task(validated_params)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'RunTaskParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop_task", response_model=ApiResponse)
@schema(input_schema_class=TaskIdParams, output_schema_class=StopTaskResponse, examples=examples["/browser-use/stop_task"])
async def stop_task(
    params: Dict[str, Any] = Body(...),
    service: BrowserUseService = Depends(get_browser_use_service)
):
    try:
        validated_params = TaskIdParams(**params)
        return service.stop_task(validated_params.task_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'TaskIdParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/pause_task", response_model=ApiResponse)
@schema(input_schema_class=TaskIdParams, output_schema_class=PauseTaskResponse, examples=examples["/browser-use/pause_task"])
async def pause_task(
    params: Dict[str, Any] = Body(...),
    service: BrowserUseService = Depends(get_browser_use_service)
):
    try:
        validated_params = TaskIdParams(**params)
        return service.pause_task(validated_params.task_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'TaskIdParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/resume_task", response_model=ApiResponse)
@schema(input_schema_class=TaskIdParams, output_schema_class=ResumeTaskResponse, examples=examples["/browser-use/resume_task"])
async def resume_task(
    params: Dict[str, Any] = Body(...),
    service: BrowserUseService = Depends(get_browser_use_service)
):
    try:
        validated_params = TaskIdParams(**params)
        return service.resume_task(validated_params.task_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'TaskIdParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_task", response_model=ApiResponse)
@schema(input_schema_class=TaskIdParams, output_schema_class=GetTaskResponse, examples=examples["/browser-use/get_task"])
async def get_task(
    params: Dict[str, Any] = Body(...),
    service: BrowserUseService = Depends(get_browser_use_service)
):
    try:
        validated_params = TaskIdParams(**params)
        return service.get_task(validated_params.task_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'TaskIdParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_task_status", response_model=ApiResponse)
@schema(input_schema_class=TaskIdParams, output_schema_class=GetTaskStatusResponse, examples=examples["/browser-use/get_task_status"])
async def get_task_status(
    params: Dict[str, Any] = Body(...),
    service: BrowserUseService = Depends(get_browser_use_service)
):
    try:
        validated_params = TaskIdParams(**params)
        return service.get_task_status(validated_params.task_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'TaskIdParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_task_media", response_model=ApiResponse)
@schema(input_schema_class=TaskIdParams, output_schema_class=GetTaskMediaResponse, examples=examples["/browser-use/get_task_media"])
async def get_task_media(
    params: Dict[str, Any] = Body(...),
    service: BrowserUseService = Depends(get_browser_use_service)
):
    try:
        validated_params = TaskIdParams(**params)
        return service.get_task_media(validated_params.task_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'TaskIdParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/list_tasks", response_model=ApiResponse)
@schema(input_schema_class=None, output_schema_class=ListTasksResponse, examples=examples["/browser-use/list_tasks"])
async def list_tasks(
    service: BrowserUseService = Depends(get_browser_use_service)
):
    try:
        return service.list_tasks()
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/check_balance", response_model=ApiResponse)
@schema(input_schema_class=None, output_schema_class=CheckBalanceResponse, examples=examples["/browser-use/check_balance"])
async def check_balance(
    service: BrowserUseService = Depends(get_browser_use_service)
):
    try:
        return service.check_balance()
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/me", response_model=ApiResponse)
@schema(input_schema_class=None, output_schema_class=MeResponse, examples=examples["/browser-use/me"])
async def me(
    service: BrowserUseService = Depends(get_browser_use_service)
):
    try:
        return service.me()
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ping", response_model=ApiResponse)
@schema(input_schema_class=None, output_schema_class=PingResponse, examples=examples["/browser-use/ping"])
async def ping(
    service: BrowserUseService = Depends(get_browser_use_service)
):
    try:
        return service.ping()
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/validate_key")
async def validate_key(
    params: Dict[str, Any] = Body(...),
):
    try:
        api_key = params.get("api_key", "")
        if not api_key:
            return {"valid": False, "message": "API key is required"}
        
        client = BrowserUseClient(api_key)
        response = client.me()
        
        return {"valid": True, "message": "API key is valid"}
    except Exception as e:
        return {"valid": False, "message": f"Invalid API key"}