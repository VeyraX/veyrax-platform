from fastapi import APIRouter, Depends, HTTPException, Request as FastAPIRequest, Body
from typing import Dict, Any
from .schema import (
    ApiResponse,
    GetTasksParams, GetTaskParams, CreateTaskParams, UpdateTaskParams, DeleteTaskParams,
    GetSubtasksParams, CreateSubtaskParams, GetWorkspacesParams, GetProjectsParams,
    GetTasksResponse, GetTaskResponse, CreateTaskResponse, UpdateTaskResponse, DeleteTaskResponse,
    GetSubtasksResponse, CreateSubtaskResponse, GetWorkspacesResponse, GetProjectsResponse,
    GetGoalsParams, GetGoalParams, CreateGoalParams, UpdateGoalParams, CreateGoalResponse,
    UpdateGoalResponse, GetGoalsResponse, GetGoalResponse,
    GetProjectParams, GetProjectResponse, GetTagsParams, GetTagsResponse, GetTagParams, GetTagResponse,
    GetTeamsParams, GetTeamsResponse, GetTeamParams, GetTeamResponse, GetUsersParams, GetUsersResponse,
    GetUserParams, GetUserResponse, GetWorkspaceParams, GetWorkspaceResponse,
    GetSectionsParams, GetSectionParams, GetSectionTasksParams, GetSectionsResponse, GetSectionResponse,
    GetSectionTasksResponse, GetTimePeriodsParams, GetTimePeriodsResponse
)

from .service import AsanaService
from .client import AsanaClient
from ..common.auth import TokenService, AsanaTokenRefresher
from ..common.input_schema_decorator import schema
from ..common.utils import format_validation_error, apply_error_handler_to_service, apply_error_handler_to_router, apply_error_handler_to_client
from ..common.examples_handler import ExamplesLoader

router = APIRouter(prefix="/asana", tags=["asana"])

examples = ExamplesLoader() 

async def get_asana_service(request: FastAPIRequest) -> AsanaService:
    try:
        token_data = await TokenService.get_user_token(request, 'asana')
        
        if TokenService.is_token_expired(token_data):
            try:
                token_data = await AsanaTokenRefresher.refresh(request, token_data)
            except Exception as e:
                raise HTTPException(status_code=401, detail="Failed to refresh token")
        
        access_token = token_data['access_token']
        client = AsanaClient(access_token)
        service = AsanaService(client)
        
        apply_error_handler_to_client(client)
        apply_error_handler_to_service(service)
        
        
        return service
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Failed to initialize Asana service: {str(e)}"
        )

@router.post("/get_tasks", response_model=ApiResponse)
@schema(input_schema_class=GetTasksParams, output_schema_class=GetTasksResponse, examples=examples["/asana/get_tasks"])
async def get_tasks(
    params: Dict[str, Any] = Body(...),
    service: AsanaService = Depends(get_asana_service)
):
    validated_params = GetTasksParams(**params)
    return service.get_tasks(
        workspace_id=validated_params.workspace_id,
        project_id=validated_params.project_id,
        assignee=validated_params.assignee,
        completed_since=validated_params.completed_since,
        limit=validated_params.limit,
        offset=validated_params.offset
    )

@router.post("/get_task", response_model=ApiResponse)
@schema(input_schema_class=GetTaskParams, output_schema_class=GetTaskResponse, examples=examples["/asana/get_task"])
async def get_task(
    params: Dict[str, Any] = Body(...),
    service: AsanaService = Depends(get_asana_service)
):
    validated_params = GetTaskParams(**params)
    return service.get_task(validated_params.task_id)

@router.post("/create_task", response_model=ApiResponse)
@schema(input_schema_class=CreateTaskParams, output_schema_class=CreateTaskResponse, examples=examples["/asana/create_task"])
async def create_task(
    params: Dict[str, Any] = Body(...),
    service: AsanaService = Depends(get_asana_service)
):
    validated_params = CreateTaskParams(**params)
    return service.create_task(validated_params.task)

@router.post("/update_task", response_model=ApiResponse)
@schema(input_schema_class=UpdateTaskParams, output_schema_class=UpdateTaskResponse, examples=examples["/asana/update_task"])
async def update_task(
    params: Dict[str, Any] = Body(...),
    service: AsanaService = Depends(get_asana_service)
):
    validated_params = UpdateTaskParams(**params)
    return service.update_task(
        validated_params.task_id,
        validated_params.task_update
    )

@router.post("/delete_task", response_model=ApiResponse)
@schema(input_schema_class=DeleteTaskParams, output_schema_class=DeleteTaskResponse, examples=examples["/asana/delete_task"])
async def delete_task(
    params: Dict[str, Any] = Body(...),
    service: AsanaService = Depends(get_asana_service)
):
    validated_params = DeleteTaskParams(**params)
    return service.delete_task(validated_params.task_id)

@router.post("/get_subtasks", response_model=ApiResponse)
@schema(input_schema_class=GetSubtasksParams, output_schema_class=GetSubtasksResponse, examples=examples["/asana/get_subtasks"])
async def get_subtasks(
    params: Dict[str, Any] = Body(...),
    service: AsanaService = Depends(get_asana_service)
):
    validated_params = GetSubtasksParams(**params)
    return service.get_subtasks(validated_params.task_id)

@router.post("/create_subtask", response_model=ApiResponse)
@schema(input_schema_class=CreateSubtaskParams, output_schema_class=CreateSubtaskResponse, examples=examples["/asana/create_subtask"])
async def create_subtask(
    params: Dict[str, Any] = Body(...),
    service: AsanaService = Depends(get_asana_service)
):
    validated_params = CreateSubtaskParams(**params)
    return service.create_subtask(
        validated_params.parent_task_id,
        validated_params.subtask
    )

@router.post("/get_workspaces", response_model=ApiResponse)
@schema(input_schema_class=GetWorkspacesParams, output_schema_class=GetWorkspacesResponse, examples=examples["/asana/get_workspaces"])
async def get_workspaces(
    params: Dict[str, Any] = Body(...),
    service: AsanaService = Depends(get_asana_service)
):
    validated_params = GetWorkspacesParams(**params)
    return service.get_workspaces(
        limit=validated_params.limit,
        offset=validated_params.offset
    )

@router.post("/get_projects", response_model=ApiResponse)
@schema(input_schema_class=GetProjectsParams, output_schema_class=GetProjectsResponse, examples=examples["/asana/get_projects"])
async def get_projects(
    params: Dict[str, Any] = Body(...),
    service: AsanaService = Depends(get_asana_service)
):
    validated_params = GetProjectsParams(**params)
    return service.get_projects(
        workspace_id=validated_params.workspace_id,
        team_id=validated_params.team_id,
        archived=validated_params.archived,
        limit=validated_params.limit,
        offset=validated_params.offset
    )

@router.post("/get_project", response_model=ApiResponse)
@schema(input_schema_class=GetProjectParams, output_schema_class=GetProjectResponse, examples=examples["/asana/get_project"])
async def get_project(
    params: Dict[str, Any] = Body(...),
    service: AsanaService = Depends(get_asana_service)
):
    validated_params = GetProjectParams(**params)
    return service.get_project(validated_params.project_id)

@router.post("/get_tags", response_model=ApiResponse)
@schema(input_schema_class=GetTagsParams, output_schema_class=GetTagsResponse, examples=examples["/asana/get_tags"])
async def get_tags(
    params: Dict[str, Any] = Body(...),
    service: AsanaService = Depends(get_asana_service)
):
    validated_params = GetTagsParams(**params)
    return service.get_tags(
        workspace_id=validated_params.workspace_id,
        limit=validated_params.limit,
        offset=validated_params.offset
    )

@router.post("/get_tag", response_model=ApiResponse)
@schema(input_schema_class=GetTagParams, output_schema_class=GetTagResponse, examples=examples["/asana/get_tag"])
async def get_tag(
    params: Dict[str, Any] = Body(...),
    service: AsanaService = Depends(get_asana_service)
):
    validated_params = GetTagParams(**params)
    return service.get_tag(validated_params.tag_id)

@router.post("/get_teams", response_model=ApiResponse)
@schema(input_schema_class=GetTeamsParams, output_schema_class=GetTeamsResponse, examples=examples["/asana/get_teams"])
async def get_teams(
    params: Dict[str, Any] = Body(...),
    service: AsanaService = Depends(get_asana_service)
):
    validated_params = GetTeamsParams(**params)
    return service.get_teams(
        workspace_id=validated_params.workspace_id,
        limit=validated_params.limit,
        offset=validated_params.offset
    )

@router.post("/get_team", response_model=ApiResponse)
@schema(input_schema_class=GetTeamParams, output_schema_class=GetTeamResponse, examples=examples["/asana/get_team"])
async def get_team(
    params: Dict[str, Any] = Body(...),
    service: AsanaService = Depends(get_asana_service)
):
    validated_params = GetTeamParams(**params)
    return service.get_team(validated_params.team_id)

@router.post("/get_users", response_model=ApiResponse)
@schema(input_schema_class=GetUsersParams, output_schema_class=GetUsersResponse, examples=examples["/asana/get_users"])
async def get_users(
    params: Dict[str, Any] = Body(...),
    service: AsanaService = Depends(get_asana_service)
):
    validated_params = GetUsersParams(**params)
    return service.get_users(
        workspace_id=validated_params.workspace_id,
        team_id=validated_params.team_id,
        limit=validated_params.limit,
        offset=validated_params.offset
    )

@router.post("/get_user", response_model=ApiResponse)
@schema(input_schema_class=GetUserParams, output_schema_class=GetUserResponse, examples=examples["/asana/get_user"])
async def get_user(
    params: Dict[str, Any] = Body(...),
    service: AsanaService = Depends(get_asana_service)
):
    validated_params = GetUserParams(**params)
    return service.get_user(validated_params.user_id)

@router.post("/get_workspace", response_model=ApiResponse)
@schema(input_schema_class=GetWorkspaceParams, output_schema_class=GetWorkspaceResponse, examples=examples["/asana/get_workspace"])
async def get_workspace(
    params: Dict[str, Any] = Body(...),
    service: AsanaService = Depends(get_asana_service)
):
    validated_params = GetWorkspaceParams(**params)
    return service.get_workspace(validated_params.workspace_id)

@router.post("/get_goals", response_model=ApiResponse)
@schema(input_schema_class=GetGoalsParams, output_schema_class=GetGoalsResponse, examples=examples["/asana/get_goals"])
async def get_goals(
    params: Dict[str, Any] = Body(...),
    service: AsanaService = Depends(get_asana_service)
):
    validated_params = GetGoalsParams(**params)
    return service.get_goals(
        workspace_id=validated_params.workspace_id,
        time_period_id=validated_params.time_period_id,
        owner_id=validated_params.owner_id,
        is_workspace_level=validated_params.is_workspace_level,
        limit=validated_params.limit,
        offset=validated_params.offset
    )

@router.post("/get_goal", response_model=ApiResponse)
@schema(input_schema_class=GetGoalParams, output_schema_class=GetGoalResponse, examples=examples["/asana/get_goal"])
async def get_goal(
    params: Dict[str, Any] = Body(...),
    service: AsanaService = Depends(get_asana_service)
):
    validated_params = GetGoalParams(**params)
    return service.get_goal(validated_params.goal_id)

@router.post("/create_goal", response_model=ApiResponse)
@schema(input_schema_class=CreateGoalParams, output_schema_class=CreateGoalResponse, examples=examples["/asana/create_goal"])
async def create_goal(
    params: Dict[str, Any] = Body(...),
    service: AsanaService = Depends(get_asana_service)
):
    validated_params = CreateGoalParams(**params)
    return service.create_goal(validated_params.goal)

@router.post("/update_goal", response_model=ApiResponse)
@schema(input_schema_class=UpdateGoalParams, output_schema_class=UpdateGoalResponse, examples=examples["/asana/update_goal"])
async def update_goal(
    params: Dict[str, Any] = Body(...),
    service: AsanaService = Depends(get_asana_service)
):
    validated_params = UpdateGoalParams(**params)
    return service.update_goal(
        validated_params.goal_id,
        validated_params.goal_update
    )

@router.post("/get_sections", response_model=ApiResponse)
@schema(input_schema_class=GetSectionsParams, output_schema_class=GetSectionsResponse, examples=examples["/asana/get_sections"])
async def get_sections(
    params: Dict[str, Any] = Body(...),
    service: AsanaService = Depends(get_asana_service)
):
    validated_params = GetSectionsParams(**params)
    return service.get_sections(validated_params.project_id)

@router.post("/get_section", response_model=ApiResponse)
@schema(input_schema_class=GetSectionParams, output_schema_class=GetSectionResponse, examples=examples["/asana/get_section"])
async def get_section(
    params: Dict[str, Any] = Body(...),
    service: AsanaService = Depends(get_asana_service)
):
    validated_params = GetSectionParams(**params)
    return service.get_section(validated_params.section_id)

@router.post("/get_section_tasks", response_model=ApiResponse)
@schema(input_schema_class=GetSectionTasksParams, output_schema_class=GetSectionTasksResponse, examples=examples["/asana/get_section_tasks"])
async def get_section_tasks(
    params: Dict[str, Any] = Body(...),
    service: AsanaService = Depends(get_asana_service)
):
    validated_params = GetSectionTasksParams(**params)
    return service.get_section_tasks(
        validated_params.section_id,
        validated_params.limit,
        validated_params.offset
    )

@router.post("/get_time_periods", response_model=ApiResponse)
@schema(input_schema_class=GetTimePeriodsParams, output_schema_class=GetTimePeriodsResponse, examples=examples["/asana/get_time_periods"])
async def get_time_periods(
    params: Dict[str, Any] = Body(...),
    service: AsanaService = Depends(get_asana_service)
):
    validated_params = GetTimePeriodsParams(**params)
    return service.get_time_periods(
        workspace_id=validated_params.workspace_id,
        limit=validated_params.limit,
        offset=validated_params.offset
    )

apply_error_handler_to_router(router)
