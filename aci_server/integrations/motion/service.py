from typing import Optional, Dict, Any, List
from .client import MotionClient
from .schema import (
    ApiResponse,
    CreateCommentParams,
    GetCommentsParams,
    CreateProjectParams,
    GetProjectParams,
    ListProjectsParams,
    Comment,
    GetCommentsResponse,
    Project,
    ListProjectsResponse,
    CreateRecurringTaskParams,
    DeleteRecurringTaskParams,
    ListRecurringTasksParams,
    RecurringTask,
    ListRecurringTasksResponse,
    GetSchedulesParams,
    GetStatusesParams,
    ListUsersParams,
    ListWorkspacesParams,
    Schedule,
    Status,
    User,
    ListUsersResponse,
    ListWorkspacesResponse,
    SchedulesListResponse,
    StatusesListResponse,
    CreateTaskParams,
    DeleteTaskParams,
    GetTaskParams,
    ListTasksParams,
    MoveTaskParams,
    UnassignTaskParams,
    UpdateTaskParams,
    Task,
    ListTasksResponse
)
import os
from ..common.component_handler import load_components, prepare_components_auto

class MotionService:
    def __init__(self, client: MotionClient):
        self.client = client
        self.components_data = self._load_components()

    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
        
    def prepare_response(self, data: Any, component_name: str = None) -> ApiResponse:
        tool_name = "motion"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)

    def create_comment(self, params: CreateCommentParams) -> ApiResponse:
        """Create a new comment on a task"""
        params_dict = params.model_dump(exclude_none=True)
        response = self.client.create_comment(params_dict)
        validated = Comment(**response)
        return self.prepare_response(validated, "MotionCommentCard")

    def get_comments(self, params: GetCommentsParams) -> ApiResponse:
        """Get all comments for a task"""
        task_id = params.taskId
        cursor = params.cursor
        response = self.client.get_comments(task_id, cursor)
        validated = GetCommentsResponse(**response)
        return self.prepare_response(validated, "MotionCommentsList")

    def create_project(self, params: CreateProjectParams) -> ApiResponse:
        """Create a new project"""
        params_dict = params.model_dump(exclude_none=True)
        
        response = self.client.create_project(params_dict)
        validated = Project(**response)
        return self.prepare_response(validated, "MotionProjectCard")

    def get_project(self, project_id: str) -> ApiResponse:
        """Get a single project by ID"""
        response = self.client.get_project(project_id)
        validated = Project(**response)
        return self.prepare_response(validated, "MotionProjectCard")

    def list_projects(self, params: ListProjectsParams) -> ApiResponse:
        """List all projects for a workspace"""
        workspace_id = params.workspaceId
        cursor = params.cursor
        response = self.client.list_projects(workspace_id, cursor)
        validated = ListProjectsResponse(**response)
        return self.prepare_response(validated, "MotionProjectsList")
        
    def create_recurring_task(self, params: CreateRecurringTaskParams) -> ApiResponse:
        """Create a new recurring task"""
        params_dict = params.model_dump(exclude_none=True)
        response = self.client.create_recurring_task(params_dict)
        validated = RecurringTask(**response)
        return self.prepare_response(validated, "MotionRecurringTaskCard")
        
    def delete_recurring_task(self, task_id: str) -> ApiResponse:
        """Delete a recurring task by ID"""
        response = self.client.delete_recurring_task(task_id)
        return self.prepare_response(response, None)
        
    def list_recurring_tasks(self, params: ListRecurringTasksParams) -> ApiResponse:
        """List all recurring tasks for a workspace"""
        workspace_id = params.workspaceId
        cursor = params.cursor
        response = self.client.list_recurring_tasks(workspace_id, cursor)
        validated = ListRecurringTasksResponse(**response)
        return self.prepare_response(validated, "MotionRecurringTasksList")

    def get_schedules(self) -> ApiResponse:
        """Get all schedules for the authenticated user"""
        response = self.client.get_schedules()
        validated_schedules = [Schedule(**schedule) for schedule in response]
        wrapped_response = SchedulesListResponse(schedules=validated_schedules)
        return self.prepare_response(wrapped_response, "MotionSchedulesList")
        
    def get_statuses(self, params: GetStatusesParams) -> ApiResponse:
        """Get a list of statuses for a workspace"""
        workspace_id = params.workspaceId
        response = self.client.get_statuses(workspace_id)
        validated_statuses = [Status(**status) for status in response]
        wrapped_response = StatusesListResponse(statuses=validated_statuses)
        return self.prepare_response(wrapped_response, "MotionStatusesList")
        
    def list_users(self, params: ListUsersParams) -> ApiResponse:
        """Get a list of users for a team or workspace"""
        team_id = params.teamId
        workspace_id = params.workspaceId
        cursor = params.cursor
        response = self.client.list_users(team_id, workspace_id, cursor)
        validated = ListUsersResponse(**response)
        return self.prepare_response(validated, "MotionUsersList")
        
    def get_my_user(self) -> ApiResponse:
        """Get information about the authenticated user"""
        response = self.client.get_my_user()
        validated = User(**response)
        return self.prepare_response(validated, "MotionUserCard")
        
    def list_workspaces(self, params: ListWorkspacesParams) -> ApiResponse:
        """Get a list of workspaces the user is part of"""
        ids = params.ids
        cursor = params.cursor
        response = self.client.list_workspaces(ids, cursor)
        validated = ListWorkspacesResponse(**response)
        return self.prepare_response(validated, "MotionWorkspacesList")

    def create_task(self, params: CreateTaskParams) -> ApiResponse:
        """Create a new task"""
        params_dict = params.model_dump(exclude_none=True)
        response = self.client.create_task(params_dict)
        validated = Task(**response)
        return self.prepare_response(validated, "MotionTaskCard")
    
    def delete_task(self, task_id: str) -> ApiResponse:
        """Delete a task by ID"""
        response = self.client.delete_task(task_id)
        return self.prepare_response(response, None)
    
    def get_task(self, task_id: str) -> ApiResponse:
        """Get a task by ID"""
        response = self.client.get_task(task_id)
        validated = Task(**response)
        return self.prepare_response(validated, "MotionTaskCard")
    
    def list_tasks(self, params: ListTasksParams) -> ApiResponse:
        """List tasks based on query parameters"""
        params_dict = params.model_dump(exclude_none=True)
        # List tasks handles params slightly differently
        assignee_id = params_dict.pop("assigneeId", None)
        cursor = params_dict.pop("cursor", None)
        include_all_statuses = params_dict.pop("includeAllStatuses", None)
        label = params_dict.pop("label", None)
        name = params_dict.pop("name", None)
        project_id = params_dict.pop("projectId", None)
        status = params_dict.pop("status", None)
        workspace_id = params_dict.pop("workspaceId", None)
        
        response = self.client.list_tasks(
            assignee_id=assignee_id,
            cursor=cursor,
            include_all_statuses=include_all_statuses,
            label=label,
            name=name,
            project_id=project_id,
            status=status,
            workspace_id=workspace_id
        )
        validated = ListTasksResponse(**response)
        return self.prepare_response(validated, "MotionTasksList")
    
    def move_task(self, task_id: str, workspace_id: str) -> ApiResponse:
        """Move a task to a different workspace"""
        data = {"workspaceId": workspace_id}
        response = self.client.move_task(task_id, data)
        validated = Task(**response)
        return self.prepare_response(validated, "MotionTaskCard")
    
    def unassign_task(self, task_id: str) -> ApiResponse:
        """Remove the assignee of a task"""
        response = self.client.unassign_task(task_id)
        return self.prepare_response(response, None)
    
    def update_task(self, task_id: str, params: UpdateTaskParams) -> ApiResponse:
        """Update a task"""
        params_dict = params.model_dump(exclude_none=True)
        # Remove ID as it's in the URL
        if "id" in params_dict:
            params_dict.pop("id")
            
        response = self.client.update_task(task_id, params_dict)
        validated = Task(**response)
        return self.prepare_response(validated, "MotionTaskCard")
