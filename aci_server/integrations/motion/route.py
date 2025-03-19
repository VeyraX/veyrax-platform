from fastapi import APIRouter, Depends, Body, HTTPException, Path, Query
from typing import Dict, Any, Optional, List
from .schema import (
    CreateCommentParams,
    GetCommentsParams,
    CreateProjectParams,
    GetProjectParams,
    ListProjectsParams,
    CreateRecurringTaskParams,
    DeleteRecurringTaskParams,
    ListRecurringTasksParams,
    ApiResponse,
    GetSchedulesParams,
    GetStatusesParams,
    ListUsersParams,
    ListWorkspacesParams,
    CreateTaskParams,
    DeleteTaskParams,
    GetTaskParams,
    ListTasksParams,
    MoveTaskParams,
    UnassignTaskParams,
    UpdateTaskParams,
    Comment,
    GetCommentsResponse,
    Project,
    ListProjectsResponse,
    RecurringTask,
    SchedulesListResponse,
    StatusesListResponse,
    ListUsersResponse,
    ListWorkspacesResponse,
    Task,
    ListTasksResponse,
    User,
    ListRecurringTasksResponse,
    EmptyRequestBody,
    SuccessResponse,
)
from .service import MotionService
from .client import MotionClient
from ..common.auth import validate_provider_api_key
from ..common.input_schema_decorator import schema
from ..common.utils import apply_error_handler_to_service, apply_error_handler_to_router, apply_error_handler_to_client
from ..common.examples_handler import ExamplesLoader
from fastapi import Request

router = APIRouter(prefix="/motion", tags=["motion"])
examples = ExamplesLoader()

async def get_motion_service(request: Request):
    try:
        api_key = await validate_provider_api_key(request, "motion")
        client = MotionClient(api_key)
        apply_error_handler_to_client(client)

        service = MotionService(client)
        apply_error_handler_to_service(service)
        return service
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Motion service initialization failed: {str(e)}")

@router.post("/create_comment", response_model=ApiResponse)
@schema(
    input_schema_class=CreateCommentParams,
    output_schema_class=Comment,
    examples=examples["/motion/create_comment"]
)
async def create_comment(
    params: Dict[str, Any] = Body(...),
    service: MotionService = Depends(get_motion_service)
):
    validated_params = CreateCommentParams(**params)
    return service.create_comment(validated_params)

@router.post("/get_comments", response_model=ApiResponse)
@schema(
    input_schema_class=GetCommentsParams,
    output_schema_class=GetCommentsResponse,
    examples=examples["/motion/get_comments"]
)
async def get_comments(
    params: Dict[str, Any] = Body(...),
    service: MotionService = Depends(get_motion_service)
):
    validated_params = GetCommentsParams(**params)
    return service.get_comments(validated_params)

@router.post("/create_project", response_model=ApiResponse)
@schema(
    input_schema_class=CreateProjectParams,
    output_schema_class=Project,
    examples=examples["/motion/create_project"]
)
async def create_project(
    params: Dict[str, Any] = Body(...),
    service: MotionService = Depends(get_motion_service)
):
    validated_params = CreateProjectParams(**params)
    return service.create_project(validated_params)

@router.post("/get_project", response_model=ApiResponse)
@schema(
    input_schema_class=GetProjectParams,
    output_schema_class=Project,
    examples=examples["/motion/get_project"]
)
async def get_project(
    params: Dict[str, Any] = Body(...),
    service: MotionService = Depends(get_motion_service)
):
    validated_params = GetProjectParams(**params)
    return service.get_project(validated_params.id)

@router.post("/list_projects", response_model=ApiResponse)
@schema(
    input_schema_class=ListProjectsParams,
    output_schema_class=ListProjectsResponse,
    examples=examples["/motion/list_projects"]
)
async def list_projects(
    params: Dict[str, Any] = Body(...),
    service: MotionService = Depends(get_motion_service)
):
    validated_params = ListProjectsParams(**params)
    return service.list_projects(validated_params)

@router.post("/create_recurring_task", response_model=ApiResponse)
@schema(
    input_schema_class=CreateRecurringTaskParams,
    output_schema_class=RecurringTask,
    examples=examples["/motion/create_recurring_task"]
)
async def create_recurring_task(
    params: Dict[str, Any] = Body(...),
    service: MotionService = Depends(get_motion_service)
):
    validated_params = CreateRecurringTaskParams(**params)
    return service.create_recurring_task(validated_params)

@router.post("/delete_recurring_task", response_model=ApiResponse)
@schema(
    input_schema_class=DeleteRecurringTaskParams,
    output_schema_class=SuccessResponse,
    examples=examples["/motion/delete_recurring_task"]
)
async def delete_recurring_task(
    params: Dict[str, Any] = Body(...),
    service: MotionService = Depends(get_motion_service)
):
    validated_params = DeleteRecurringTaskParams(**params)
    return service.delete_recurring_task(validated_params.id)

@router.post("/list_recurring_tasks", response_model=ApiResponse)
@schema(
    input_schema_class=ListRecurringTasksParams,
    output_schema_class=ListRecurringTasksResponse,
    examples=examples["/motion/list_recurring_tasks"]
)
async def list_recurring_tasks(
    params: Dict[str, Any] = Body(...),
    service: MotionService = Depends(get_motion_service)
):
    validated_params = ListRecurringTasksParams(**params)
    return service.list_recurring_tasks(validated_params)

@router.post("/get_schedules", response_model=ApiResponse)
@schema(
    input_schema_class=GetSchedulesParams,
    output_schema_class=SchedulesListResponse,
    examples=examples["/motion/get_schedules"]
)
async def get_schedules(
    service: MotionService = Depends(get_motion_service)
):
    return service.get_schedules()

@router.post("/get_statuses", response_model=ApiResponse)
@schema(
    input_schema_class=GetStatusesParams,
    output_schema_class=StatusesListResponse,
    examples=examples["/motion/get_statuses"]
)
async def get_statuses(
    params: Dict[str, Any] = Body(...),
    service: MotionService = Depends(get_motion_service)
):
    validated_params = GetStatusesParams(**params)
    return service.get_statuses(validated_params)

@router.post("/list_users", response_model=ApiResponse)
@schema(
    input_schema_class=ListUsersParams,
    output_schema_class=ListUsersResponse,
    examples=examples["/motion/list_users"]
)
async def list_users(
    params: Dict[str, Any] = Body(...),
    service: MotionService = Depends(get_motion_service)
):
    validated_params = ListUsersParams(**params)
    return service.list_users(validated_params)

@router.post("/get_my_user", response_model=ApiResponse)
@schema(
    input_schema_class=EmptyRequestBody,
    output_schema_class=User,
    examples=examples["/motion/get_my_user"]
)
async def get_my_user(
    service: MotionService = Depends(get_motion_service)
):
    return service.get_my_user()

@router.post("/list_workspaces", response_model=ApiResponse)
@schema(
    input_schema_class=ListWorkspacesParams,
    output_schema_class=ListWorkspacesResponse,
    examples=examples["/motion/list_workspaces"]
)
async def list_workspaces(
    params: Dict[str, Any] = Body(...),
    service: MotionService = Depends(get_motion_service)
):
    validated_params = ListWorkspacesParams(**params)
    return service.list_workspaces(validated_params)

@router.post("/create_task", response_model=ApiResponse)
@schema(
    input_schema_class=CreateTaskParams,
    output_schema_class=Task,
    examples=examples["/motion/create_task"]
)
async def create_task(
    params: Dict[str, Any] = Body(...),
    service: MotionService = Depends(get_motion_service)
):
    validated_params = CreateTaskParams(**params)
    return service.create_task(validated_params)

@router.post("/delete_task", response_model=ApiResponse)
@schema(
    input_schema_class=DeleteTaskParams,
    output_schema_class=SuccessResponse,
    examples=examples["/motion/delete_task"]
)
async def delete_task(
    params: Dict[str, Any] = Body(...),
    service: MotionService = Depends(get_motion_service)
):
    validated_params = DeleteTaskParams(**params)
    return service.delete_task(validated_params.id)

@router.post("/get_task", response_model=ApiResponse)
@schema(
    input_schema_class=GetTaskParams,
    output_schema_class=Task,
    examples=examples["/motion/get_task"]
)
async def get_task(
    params: Dict[str, Any] = Body(...),
    service: MotionService = Depends(get_motion_service)
):
    validated_params = GetTaskParams(**params)
    return service.get_task(validated_params.id)

@router.post("/list_tasks", response_model=ApiResponse)
@schema(
    input_schema_class=ListTasksParams,
    output_schema_class=ListTasksResponse,
    examples=examples["/motion/list_tasks"]
)
async def list_tasks(
    params: Dict[str, Any] = Body(...),
    service: MotionService = Depends(get_motion_service)
):
    validated_params = ListTasksParams(**params)
    return service.list_tasks(validated_params)

@router.post("/move_task", response_model=ApiResponse)
@schema(
    input_schema_class=MoveTaskParams,
    output_schema_class=Task,
    examples=examples["/motion/move_task"]
)
async def move_task(
    params: Dict[str, Any] = Body(...),
    service: MotionService = Depends(get_motion_service)
):
    validated_params = MoveTaskParams(**params)
    return service.move_task(validated_params.id, validated_params.workspaceId)

@router.post("/unassign_task", response_model=ApiResponse)
@schema(
    input_schema_class=UnassignTaskParams,
    output_schema_class=SuccessResponse,
    examples=examples["/motion/unassign_task"]
)
async def unassign_task(
    params: Dict[str, Any] = Body(...),
    service: MotionService = Depends(get_motion_service)
):
    validated_params = UnassignTaskParams(**params)
    return service.unassign_task(validated_params.id)

@router.post("/update_task", response_model=ApiResponse)
@schema(
    input_schema_class=UpdateTaskParams,
    output_schema_class=Task,
    examples=examples["/motion/update_task"]
)
async def update_task(
    params: Dict[str, Any] = Body(...),
    service: MotionService = Depends(get_motion_service)
):
    validated_params = UpdateTaskParams(**params)
    return service.update_task(validated_params.id, validated_params)

@router.post("/validate_key")
async def validate_key(
    params: Dict[str, Any] = Body(...),
):
    try:
        api_key = params.get("api_key", "")
        if not api_key:
            return {"valid": False, "message": "API key is required"}
        
        client = MotionClient(api_key)
        # Test the API key with a simple operation like listing projects with a small limit
        client.get_my_user()
        
        return {"valid": True, "message": "API key is valid"}
    except Exception as e:
        return {"valid": False, "message": f"Invalid API key"}


apply_error_handler_to_router(router)
