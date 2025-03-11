from fastapi import APIRouter, Depends, HTTPException, Body, Request as FastAPIRequest
from typing import Dict, Any
from .service import TickTickService
from .client import TickTickClient
from .schema import (
    ApiResponse, GetTaskParams, TaskCreate, TaskUpdate,
    ProjectOperationParams, ProjectCreate, ProjectUpdate,
    ListTasksParams, TaskOperationParams
)
from ..common.auth import TokenService, TokenRefresherFactory
from ..common.input_schema_decorator import schema, input_schema, output_schema
from ..common.utils import format_validation_error
from pydantic import ValidationError
from ..common.examples_handler import ExamplesLoader

router = APIRouter(prefix="/ticktick", tags=["ticktick"])
examples = ExamplesLoader()

async def get_ticktick_service(request: FastAPIRequest) -> TickTickService:
    try:
        token_data = await TokenService.get_user_token(request, 'ticktick')
        if TokenService.is_token_expired(token_data):
            refresher = TokenRefresherFactory.get_refresher('ticktick')
            token_data = await refresher.refresh(request, token_data)
        client = TickTickClient(token_data['access_token'])
        return TickTickService(client)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Service initialization failed: {str(e)}")

@router.post("/tasks-get", response_model=ApiResponse)
@schema(input_schema_class=GetTaskParams, output_schema_class=ApiResponse, examples=examples["/ticktick/tasks-get"])
async def get_task(
    params: Dict[str, Any] = Body(...),
    service: TickTickService = Depends(get_ticktick_service)
):
    try:
        validated = GetTaskParams(**params)
        return service.get_task(validated.project_id, validated.task_id)
    except ValidationError as e:
        raise HTTPException(400, detail=format_validation_error(e, 'GetTaskParams'))
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@router.post("/tasks-create", response_model=ApiResponse)
@schema(input_schema_class=TaskCreate, output_schema_class=ApiResponse, examples=examples["/ticktick/tasks-create"])
async def create_task(
    params: Dict[str, Any] = Body(...),
    service: TickTickService = Depends(get_ticktick_service)
):
    try:
        print("Creating task with params: ", params)
        validated = TaskCreate(**params)
        print("Validated task: ", validated)
        return service.create_task(validated)
    except ValidationError as e:
        error_msg = format_validation_error(e, 'TaskCreate')
        return ApiResponse(
            data={"validation_errors": error_msg},
            message="Invalid task data",
            status_code=400
        )
    except Exception as e:
        return ApiResponse(
            data={"error": str(e)},
            message="Server error",
            status_code=500
        )

@router.post("/tasks-update", response_model=ApiResponse)
@schema(input_schema_class=TaskUpdate, output_schema_class=ApiResponse, examples=examples["/ticktick/tasks-update"])
async def update_task(
    params: Dict[str, Any] = Body(...),
    service: TickTickService = Depends(get_ticktick_service)
):
    try:
        validated = TaskUpdate(**params)
        return service.update_task(validated.id, validated)
    except ValidationError as e:
        raise HTTPException(400, detail=format_validation_error(e, 'TaskUpdate'))
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@router.post("/tasks-complete", response_model=ApiResponse)
@schema(input_schema_class=TaskOperationParams, output_schema_class=ApiResponse)
async def complete_task(
    params: Dict[str, Any] = Body(...),
    service: TickTickService = Depends(get_ticktick_service)
):
    try:
        validated = TaskOperationParams(**params)
        return service.complete_task(validated.project_id, validated.task_id)
    except ValidationError as e:
        raise HTTPException(400, detail=format_validation_error(e, 'TaskOperationParams'))
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@router.post("/projects-list", response_model=ApiResponse)
@schema(output_schema_class=ApiResponse, examples=examples["/ticktick/projects-list"])
async def list_projects(service: TickTickService = Depends(get_ticktick_service)):
    try:
        return service.get_projects()
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@router.post("/projects-get", response_model=ApiResponse)
@schema(input_schema_class=ProjectOperationParams, output_schema_class=ApiResponse, examples=examples["/ticktick/projects-get"])
async def get_project(
    params: Dict[str, Any] = Body(...),
    service: TickTickService = Depends(get_ticktick_service)
):
    try:
        validated = ProjectOperationParams(**params)
        return service.get_project(validated.project_id)
    except ValidationError as e:
        raise HTTPException(400, detail=format_validation_error(e, 'ProjectOperationParams'))
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@router.post("/projects-create", response_model=ApiResponse)
@schema(input_schema_class=ProjectCreate, output_schema_class=ApiResponse, examples=examples["/ticktick/projects-create"])
async def create_project(
    params: Dict[str, Any] = Body(...),
    service: TickTickService = Depends(get_ticktick_service)
):
    try:
        validated = ProjectCreate(**params)
        return service.create_project(validated)
    except ValidationError as e:
        raise HTTPException(400, detail=format_validation_error(e, 'ProjectCreate'))
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@router.post("/projects-update", response_model=ApiResponse)
@schema(input_schema_class=ProjectUpdate, output_schema_class=ApiResponse, examples=examples["/ticktick/projects-update"])
async def update_project(
    params: Dict[str, Any] = Body(...),
    service: TickTickService = Depends(get_ticktick_service)
):
    try:
        validated = ProjectUpdate(**params)
        return service.update_project(validated.id, validated)
    except ValidationError as e:
        raise HTTPException(400, detail=format_validation_error(e, 'ProjectUpdate'))
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@router.post("/tasks-list", response_model=ApiResponse)
@schema(input_schema_class=ProjectOperationParams, output_schema_class=ApiResponse)
async def list_tasks(
    params: Dict[str, Any] = Body(...),
    service: TickTickService = Depends(get_ticktick_service)
):
    try:
        validated = ProjectOperationParams(**params)
        return service.get_project_tasks(validated.project_id)
    except ValidationError as e:
        raise HTTPException(400, detail=format_validation_error(e, 'ProjectOperationParams'))
    except Exception as e:
        raise HTTPException(500, detail=str(e)) 