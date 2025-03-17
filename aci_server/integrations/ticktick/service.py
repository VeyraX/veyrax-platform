from typing import Optional, Dict, Any, List
from .client import TickTickClient
from .schema import (
    TaskCreate, TaskUpdate, TaskResponse, ProjectCreate, ProjectUpdate, ProjectResponse,
    ProjectDataResponse, TaskListResponse, ProjectListResponse, ApiResponse
)
from ..common.component_handler import prepare_components_auto, load_components
import os

class TickTickService:
    def __init__(self, client: TickTickClient):
        self.client = client
        self.components_data = self._load_components()

    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)

    def prepare_response(self, data: Any, component_name: str = None) -> ApiResponse:
        tool_name = "ticktick"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)

    def get_task(self, project_id: str, task_id: str) -> ApiResponse:
        response = self.client.get_task(project_id, task_id)
        return self.prepare_response(TaskResponse(**response), "TickTickTaskCard")

    def create_task(self, task_data: TaskCreate) -> ApiResponse:
        clean_data = task_data.dict(by_alias=True, exclude_none=True)
        created_task = self.client.create_task(clean_data)
        return self.prepare_response(TaskResponse(**created_task), "TickTickTaskCard")

    def update_task(self, task_id: str, task_data: TaskUpdate) -> ApiResponse:
        update_data = task_data.dict(by_alias=True, exclude_none=True)
        updated_task = self.client.update_task(task_id, update_data)
        return self.prepare_response(TaskResponse(**updated_task), "TickTickTaskCard")

    def complete_task(self, project_id: str, task_id: str) -> ApiResponse:
        self.client.complete_task(project_id, task_id)
        return self.prepare_response({"status": "completed", "task_id": task_id})

    def delete_task(self, project_id: str, task_id: str) -> ApiResponse:
        self.client.delete_task(project_id, task_id)
        return self.prepare_response({"status": "deleted", "task_id": task_id})

    def get_projects(self) -> ApiResponse:
        response = self.client.get_projects()
        print("Get Projects Response: ", response)
        projects = [ProjectResponse(**p) for p in response]
        print("Projects: ", projects)
        return self.prepare_response(ProjectListResponse(items=projects), "TickTickProjectCard")

    def get_project(self, project_id: str) -> ApiResponse:
        response = self.client.get_project(project_id)
        return self.prepare_response(ProjectResponse(**response), "TickTickProjectCard")

    def get_project_data(self, project_id: str) -> ApiResponse:
        response = self.client.get_project_data(project_id)
        project_data = ProjectDataResponse(
            project=ProjectResponse(**response['project']),
            tasks=[TaskResponse(**task) for task in response.get('tasks', [])],
            columns=response.get('columns', [])
        )
        return self.prepare_response(project_data, "ProjectDataCard")

    def create_project(self, project_data: ProjectCreate) -> ApiResponse:
        created_project = self.client.create_project(project_data.dict(by_alias=True, exclude_none=True))
        return self.prepare_response(ProjectResponse(**created_project), "TickTickProjectCard")

    def update_project(self, project_id: str, project_data: ProjectUpdate) -> ApiResponse:
        update_data = project_data.dict(by_alias=True, exclude_none=True)
        updated_project = self.client.update_project(project_id, update_data)
        return self.prepare_response(ProjectResponse(**updated_project), "TickTickProjectCard")

    def delete_project(self, project_id: str) -> ApiResponse:
        self.client.delete_project(project_id)
        return self.prepare_response({"status": "deleted", "project_id": project_id})

    def get_project_tasks(self, project_id: str) -> ApiResponse:
        response = self.client.get_project_data(project_id)
        tasks = [TaskResponse(**task) for task in response.get('tasks', [])]
        return self.prepare_response(
            TaskListResponse(items=tasks), 
            "TickTickTaskCard"
        ) 