from typing import Dict, Any, List, Optional
import os
from .client import TodoistClient
from .schema import (
    TodoistProject,
    TodoistSection,
    TodoistCollaborator,
    TodoistTask,
    TodoistComment,
    ProjectList,
    SectionList,
    CollaboratorList,
    GetProjectsParams,
    CreateProjectParams,
    GetProjectParams,
    UpdateProjectParams,
    DeleteProjectParams,
    GetCollaboratorsParams,
    GetSectionsParams,
    ApiResponse,
    CreateSectionParams,
    UpdateSectionParams,
    DeleteSectionParams,
    GetTasksParams,
    GetCommentsParams,
    CreateCommentParams,
    UpdateCommentParams,
    TaskList,
    CommentList,
    TodoistPersonalLabel,
    PersonalLabelList,
    GetPersonalLabelsParams,
    CreatePersonalLabelParams,
    UpdatePersonalLabelParams,
    GetSharedLabelsParams,
    CreateTaskParams,
    UpdateTaskParams,
    CloseTaskParams,
    ReopenTaskParams,
    DeleteTaskParams
)
from ..common.component_handler import load_components, prepare_components_auto

class TodoistService:
    def __init__(self, client: TodoistClient):
        self.client = client
        self.components_data = self._load_components()
    
    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
    
    def prepare_response(self, data: Any, component_name: str = None) -> ApiResponse:
        tool_name = "todoist"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)
    
    def get_projects(self, params: GetProjectsParams) -> ApiResponse:
        response = self.client.get_projects()
        projects = [TodoistProject(**project) for project in response]
        project_list = ProjectList(items=projects)
        return self.prepare_response(project_list, "TodoistProjectList")
    
    def create_project(self, params: CreateProjectParams) -> ApiResponse:
        processed_params = params.model_dump(exclude_none=True)
        response = self.client.create_project(processed_params)
        project = TodoistProject(**response)
        return self.prepare_response(project, "TodoistProject")
    
    def get_project(self, project_id: str) -> ApiResponse:
        response = self.client.get_project(project_id)
        project = TodoistProject(**response)
        return self.prepare_response(project, "TodoistProject")
    
    def update_project(self, project_id: str, params: UpdateProjectParams) -> ApiResponse:
        processed_params = params.model_dump(exclude_none=True, exclude={"project_id"})
        response = self.client.update_project(project_id, processed_params)
        project = TodoistProject(**response)
        return self.prepare_response(project, "TodoistProject")
    
    def delete_project(self, project_id: str) -> ApiResponse:
        success = self.client.delete_project(project_id)
        return ApiResponse(data=success)
    
    def get_collaborators(self, project_id: str) -> ApiResponse:
        response = self.client.get_collaborators(project_id)
        collaborators = [TodoistCollaborator(**collab) for collab in response]
        collaborator_list = CollaboratorList(items=collaborators)
        return self.prepare_response(collaborator_list, "TodoistCollaboratorList")
    
    def get_sections(self, params: GetSectionsParams) -> ApiResponse:
        response = self.client.get_sections(params.project_id)
        sections = [TodoistSection(**section) for section in response]
        section_list = SectionList(items=sections)
        return self.prepare_response(section_list, "TodoistSectionList")

    def get_section(self, section_id: str) -> ApiResponse:
        response = self.client.get_section(section_id)
        section = TodoistSection(**response)
        return self.prepare_response(section, "TodoistSection")

    def create_section(self, params: CreateSectionParams) -> ApiResponse:
        processed_params = params.model_dump(exclude_none=True)
        response = self.client.create_section(processed_params)
        section = TodoistSection(**response)
        return self.prepare_response(section, "TodoistSection")

    def update_section(self, section_id: str, params: UpdateSectionParams) -> ApiResponse:
        processed_params = params.model_dump(exclude_none=True, exclude={"section_id"})
        response = self.client.update_section(section_id, processed_params)
        section = TodoistSection(**response)
        return self.prepare_response(section, "TodoistSection")

    def delete_section(self, section_id: str) -> ApiResponse:
        success = self.client.delete_section(section_id)
        return ApiResponse(data=success)

    def get_tasks(self, params: GetTasksParams) -> ApiResponse:
        response = self.client.get_tasks(
            project_id=params.project_id,
            section_id=params.section_id,
            label=params.label,
            filter_str=params.filter,
            lang=params.lang,
            ids=params.ids
        )
        tasks = [TodoistTask(**task) for task in response]
        task_list = TaskList(items=tasks)
        return self.prepare_response(task_list, "TodoistTaskList")

    def get_task(self, task_id: str) -> ApiResponse:
        response = self.client.get_task(task_id)
        task = TodoistTask(**response)
        return self.prepare_response(task, "TodoistTask")

    def create_task(self, params: CreateTaskParams) -> ApiResponse:
        processed_params = params.model_dump(exclude_none=True)
        response = self.client.create_task(processed_params)
        task = TodoistTask(**response)
        return self.prepare_response(task, "TodoistTask")

    def update_task(self, task_id: str, params: UpdateTaskParams) -> ApiResponse:
        processed_params = params.model_dump(exclude_none=True, exclude={"task_id"})
        response = self.client.update_task(task_id, processed_params)
        task = TodoistTask(**response)
        return self.prepare_response(task, "TodoistTask")

    def close_task(self, task_id: str) -> ApiResponse:
        success = self.client.close_task(task_id)
        return ApiResponse(data=success)

    def reopen_task(self, task_id: str) -> ApiResponse:
        success = self.client.reopen_task(task_id)
        return ApiResponse(data=success)

    def delete_task(self, task_id: str) -> ApiResponse:
        success = self.client.delete_task(task_id)
        return ApiResponse(data=success)

    def get_comments(self, params: GetCommentsParams) -> ApiResponse:
        task_id = params.task_id if hasattr(params, 'task_id') else None
        project_id = params.project_id if hasattr(params, 'project_id') else None
        
        if task_id and project_id:
            response = self.client.get_comments(task_id=task_id)
        elif task_id:
            response = self.client.get_comments(task_id=task_id)
        elif project_id:
            response = self.client.get_comments(project_id=project_id)
        else:
            raise ValueError("Either task_id or project_id must be provided")
        
        comments = [TodoistComment(**comment) for comment in response]
        comment_list = CommentList(items=comments)
        return self.prepare_response(comment_list, "TodoistCommentList")

    def get_comment(self, comment_id: str) -> ApiResponse:
        response = self.client.get_comment(comment_id)
        comment = TodoistComment(**response)
        return self.prepare_response(comment, "TodoistComment")

    def create_comment(self, params: CreateCommentParams) -> ApiResponse:
        processed_params = params.model_dump(exclude_none=True)
        response = self.client.create_comment(processed_params)
        comment = TodoistComment(**response)
        return self.prepare_response(comment, "TodoistComment")

    def update_comment(self, comment_id: str, params: UpdateCommentParams) -> ApiResponse:
        processed_params = params.model_dump(exclude_none=True, exclude={"comment_id"})
        response = self.client.update_comment(comment_id, processed_params)
        comment = TodoistComment(**response)
        return self.prepare_response(comment, "TodoistComment")

    def delete_comment(self, comment_id: str) -> ApiResponse:
        success = self.client.delete_comment(comment_id)
        return ApiResponse(data=success)

    def get_personal_labels(self, params: GetPersonalLabelsParams) -> ApiResponse:
        response = self.client.get_personal_labels()
        labels = [TodoistPersonalLabel(**label) for label in response]
        label_list = PersonalLabelList(items=labels)
        return self.prepare_response(label_list, "TodoistPersonalLabelList")

    def get_personal_label(self, label_id: str) -> ApiResponse:
        response = self.client.get_personal_label(label_id)
        label = TodoistPersonalLabel(**response)
        return self.prepare_response(label, "TodoistPersonalLabel")

    def create_personal_label(self, params: CreatePersonalLabelParams) -> ApiResponse:
        processed_params = params.model_dump(exclude_none=True)
        response = self.client.create_personal_label(processed_params)
        label = TodoistPersonalLabel(**response)
        return self.prepare_response(label, "TodoistPersonalLabel")

    def update_personal_label(self, label_id: str, params: UpdatePersonalLabelParams) -> ApiResponse:
        processed_params = params.model_dump(exclude_none=True, exclude={"label_id"})
        response = self.client.update_personal_label(label_id, processed_params)
        label = TodoistPersonalLabel(**response)
        return self.prepare_response(label, "TodoistPersonalLabel")

    def delete_personal_label(self, label_id: str) -> ApiResponse:
        success = self.client.delete_personal_label(label_id)
        return ApiResponse(data=success)

    def get_shared_labels(self, params: GetSharedLabelsParams) -> ApiResponse:
        response = self.client.get_shared_labels(params.omit_personal)
        return self.prepare_response(response, "TodoistSharedLabelList")

    def rename_shared_label(self, name: str, new_name: str) -> ApiResponse:
        success = self.client.rename_shared_label(name, new_name)
        return ApiResponse(data=success)

    def remove_shared_label(self, name: str) -> ApiResponse:
        success = self.client.remove_shared_label(name)
        return ApiResponse(data=success)
