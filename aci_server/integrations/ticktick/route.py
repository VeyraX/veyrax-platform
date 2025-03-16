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
from ..common.utils import format_validation_error, apply_error_handler_to_service, apply_error_handler_to_router
from pydantic import ValidationError
from ..common.examples_handler import ExamplesLoader

router = APIRouter(prefix="/ticktick", tags=["ticktick"])
examples = ExamplesLoader()

async def get_ticktick_service(request: FastAPIRequest) -> TickTickService:
    try:
        token_data = await TokenService.get_user_token(request, 'ticktick')
        if not token_data or not token_data.get('access_token'):
            raise HTTPException(
                status_code=401,
                detail="No TickTick token data found"
            )
            
        client = TickTickClient(token_data['access_token'])
        service = TickTickService(client)
        apply_error_handler_to_service(service)
        return service
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Failed to initialize TickTick service: {str(e)}"
        )

@router.post("/tasks-get", response_model=ApiResponse)
@schema(input_schema_class=GetTaskParams, output_schema_class=ApiResponse, examples=examples["/ticktick/tasks-get"])
async def get_task(
    params: Dict[str, Any] = Body(...),
    service: TickTickService = Depends(get_ticktick_service)
):
    validated = GetTaskParams(**params)
    return service.get_task(validated.project_id, validated.task_id)

@router.post("/tasks-create", response_model=ApiResponse)
@schema(input_schema_class=TaskCreate, output_schema_class=ApiResponse, examples=examples["/ticktick/tasks-create"])
async def create_task(
    params: Dict[str, Any] = Body(...),
    service: TickTickService = Depends(get_ticktick_service)
):
    print("Creating task with params: ", params)
    validated = TaskCreate(**params)
    print("Validated task: ", validated)
    return service.create_task(validated)

@router.post("/tasks-update", response_model=ApiResponse)
@schema(input_schema_class=TaskUpdate, output_schema_class=ApiResponse, examples=examples["/ticktick/tasks-update"])
async def update_task(
    params: Dict[str, Any] = Body(...),
    service: TickTickService = Depends(get_ticktick_service)
):
    validated = TaskUpdate(**params)
    return service.update_task(validated.id, validated)

@router.post("/tasks-complete", response_model=ApiResponse)
@schema(input_schema_class=TaskOperationParams, output_schema_class=ApiResponse)
async def complete_task(
    params: Dict[str, Any] = Body(...),
    service: TickTickService = Depends(get_ticktick_service)
):
    validated = TaskOperationParams(**params)
    return service.complete_task(validated.project_id, validated.task_id)

@router.post("/projects-list", response_model=ApiResponse)
@schema(output_schema_class=ApiResponse, examples=examples["/ticktick/projects-list"])
async def list_projects(service: TickTickService = Depends(get_ticktick_service)):
    return service.get_projects()

@router.post("/projects-get", response_model=ApiResponse)
@schema(input_schema_class=ProjectOperationParams, output_schema_class=ApiResponse, examples=examples["/ticktick/projects-get"])
async def get_project(
    params: Dict[str, Any] = Body(...),
    service: TickTickService = Depends(get_ticktick_service)
):
    validated = ProjectOperationParams(**params)
    return service.get_project(validated.project_id)

@router.post("/projects-create", response_model=ApiResponse)
@schema(input_schema_class=ProjectCreate, output_schema_class=ApiResponse, examples=examples["/ticktick/projects-create"])
async def create_project(
    params: Dict[str, Any] = Body(...),
    service: TickTickService = Depends(get_ticktick_service)
):
    validated = ProjectCreate(**params)
    return service.create_project(validated)

@router.post("/projects-update", response_model=ApiResponse)
@schema(input_schema_class=ProjectUpdate, output_schema_class=ApiResponse, examples=examples["/ticktick/projects-update"])
async def update_project(
    params: Dict[str, Any] = Body(...),
    service: TickTickService = Depends(get_ticktick_service)
):
    validated = ProjectUpdate(**params)
    return service.update_project(validated.id, validated)

@router.post("/tasks-list", response_model=ApiResponse)
@schema(input_schema_class=ProjectOperationParams, output_schema_class=ApiResponse)
async def list_tasks(
    params: Dict[str, Any] = Body(...),
    service: TickTickService = Depends(get_ticktick_service)
):
    validated = ProjectOperationParams(**params)
    return service.get_project_tasks(validated.project_id)

apply_error_handler_to_router(router) 