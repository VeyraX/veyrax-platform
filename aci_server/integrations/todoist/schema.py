from pydantic import BaseModel, Field, model_validator
from typing import List, Optional, Dict, Any, Union, Literal

# Base Todoist models
class TodoistProject(BaseModel):
    id: str
    name: str
    comment_count: int
    order: int
    color: str
    is_shared: bool
    is_favorite: bool
    parent_id: Optional[str] = None
    is_inbox_project: bool
    is_team_inbox: bool
    view_style: str
    url: str

class TodoistSection(BaseModel):
    id: str
    project_id: str
    order: int
    name: str

class TodoistCollaborator(BaseModel):
    id: str
    name: str
    email: str

class TodoistDue(BaseModel):
    string: str
    date: str
    is_recurring: bool
    datetime: Optional[str] = None
    timezone: Optional[str] = None
    lang: Optional[str] = None

class TodoistDeadline(BaseModel):
    date: str
    lang: Optional[str] = None

class TodoistDuration(BaseModel):
    amount: int
    unit: Literal["minute", "day"]

class TodoistTask(BaseModel):
    id: str
    project_id: str
    section_id: Optional[str] = None
    content: str
    description: str = ""
    is_completed: bool
    labels: List[str] = []
    parent_id: Optional[str] = None
    order: int
    priority: int
    due: Optional[TodoistDue] = None
    deadline: Optional[TodoistDeadline] = None
    url: str
    comment_count: int
    created_at: str
    creator_id: str
    assignee_id: Optional[str] = None
    assigner_id: Optional[str] = None
    duration: Optional[TodoistDuration] = None

class TodoistAttachment(BaseModel):
    file_name: str
    file_type: str
    file_url: str
    resource_type: str

class TodoistComment(BaseModel):
    id: str
    task_id: Optional[str] = None
    project_id: Optional[str] = None
    posted_at: str
    content: str
    attachment: Optional[TodoistAttachment] = None

class TodoistPersonalLabel(BaseModel):
    id: str
    name: str
    color: str
    order: int
    is_favorite: bool

# List container models
class ProjectList(BaseModel):
    items: List[TodoistProject]

class SectionList(BaseModel):
    items: List[TodoistSection]

class CollaboratorList(BaseModel):
    items: List[TodoistCollaborator]

class TaskList(BaseModel):
    items: List[TodoistTask]

# List container model for comments
class CommentList(BaseModel):
    items: List[TodoistComment]

# List container model for personal labels
class PersonalLabelList(BaseModel):
    items: List[TodoistPersonalLabel]

# Input schema classes
class GetProjectsParams(BaseModel):
    pass

class CreateProjectParams(BaseModel):
    name: str
    parent_id: Optional[str] = None
    color: Optional[str] = None
    is_favorite: Optional[bool] = None
    view_style: Optional[Literal["list", "board"]] = "list"

class GetProjectParams(BaseModel):
    project_id: str

class UpdateProjectParams(BaseModel):
    project_id: str
    name: Optional[str] = None
    color: Optional[str] = None
    is_favorite: Optional[bool] = None
    view_style: Optional[Literal["list", "board"]] = None

class DeleteProjectParams(BaseModel):
    project_id: str

class GetCollaboratorsParams(BaseModel):
    project_id: str

class GetSectionsParams(BaseModel):
    project_id: Optional[str] = None

# Input schema classes for Sections
class GetSectionParams(BaseModel):
    section_id: str

class CreateSectionParams(BaseModel):
    name: str
    project_id: str
    order: Optional[int] = None

class UpdateSectionParams(BaseModel):
    section_id: str
    name: str

class DeleteSectionParams(BaseModel):
    section_id: str

# Input schema classes for Tasks
class GetTasksParams(BaseModel):
    project_id: Optional[str] = None
    section_id: Optional[str] = None
    label: Optional[str] = None
    filter: Optional[str] = None
    lang: Optional[str] = None
    ids: Optional[List[str]] = None

class GetTaskParams(BaseModel):
    task_id: str

class CreateTaskParams(BaseModel):
    content: str
    description: Optional[str] = None
    project_id: Optional[str] = None
    section_id: Optional[str] = None
    parent_id: Optional[str] = None
    order: Optional[int] = None
    labels: Optional[List[str]] = None
    priority: Optional[int] = None
    due_string: Optional[str] = None
    due_date: Optional[str] = None
    due_datetime: Optional[str] = None
    due_lang: Optional[str] = None
    assignee_id: Optional[str] = None
    duration: Optional[int] = None
    duration_unit: Optional[Literal["minute", "day"]] = None
    deadline_date: Optional[str] = None
    deadline_lang: Optional[str] = None

class UpdateTaskParams(BaseModel):
    task_id: str
    content: Optional[str] = None
    description: Optional[str] = None
    labels: Optional[List[str]] = None
    priority: Optional[int] = None
    due_string: Optional[str] = None
    due_date: Optional[str] = None
    due_datetime: Optional[str] = None
    due_lang: Optional[str] = None
    assignee_id: Optional[str] = None
    duration: Optional[int] = None
    duration_unit: Optional[Literal["minute", "day"]] = None
    deadline_date: Optional[str] = None
    deadline_lang: Optional[str] = None

class CloseTaskParams(BaseModel):
    task_id: str

class ReopenTaskParams(BaseModel):
    task_id: str

class DeleteTaskParams(BaseModel):
    task_id: str

# Input schema classes for Comments
class GetCommentsParams(BaseModel):
    task_id: Optional[str] = None
    project_id: Optional[str] = None

    @model_validator(mode='after')
    def validate_task_or_project(self):
        if not self.task_id and not self.project_id:
            raise ValueError('Either task_id or project_id must be provided')
        return self

class GetCommentParams(BaseModel):
    comment_id: str

class CreateCommentParams(BaseModel):
    task_id: Optional[str] = None
    project_id: Optional[str] = None
    content: str
    attachment: Optional[Dict[str, str]] = None
    
    @model_validator(mode='after')
    def validate_task_or_project(self):
        if not self.task_id and not self.project_id:
            raise ValueError('Either task_id or project_id must be provided')
        return self

class UpdateCommentParams(BaseModel):
    comment_id: str
    content: str

class DeleteCommentParams(BaseModel):
    comment_id: str

# Input schema classes for Labels
class GetPersonalLabelsParams(BaseModel):
    pass

class GetPersonalLabelParams(BaseModel):
    label_id: str

class CreatePersonalLabelParams(BaseModel):
    name: str
    order: Optional[int] = None
    color: Optional[str] = None
    is_favorite: Optional[bool] = None

class UpdatePersonalLabelParams(BaseModel):
    label_id: str
    name: Optional[str] = None
    order: Optional[int] = None
    color: Optional[str] = None
    is_favorite: Optional[bool] = None

class DeletePersonalLabelParams(BaseModel):
    label_id: str

class GetSharedLabelsParams(BaseModel):
    omit_personal: Optional[bool] = False

class RenameSharedLabelParams(BaseModel):
    name: str
    new_name: str

class RemoveSharedLabelParams(BaseModel):
    name: str

# Response schema classes
class GetProjectsResponse(BaseModel):
    data: ProjectList

class CreateProjectResponse(BaseModel):
    data: TodoistProject

class GetProjectResponse(BaseModel):
    data: TodoistProject

class UpdateProjectResponse(BaseModel):
    data: TodoistProject

class DeleteProjectResponse(BaseModel):
    success: bool

class GetCollaboratorsResponse(BaseModel):
    data: CollaboratorList

class GetSectionsResponse(BaseModel):
    data: SectionList

# Response schema classes for new endpoints
class GetSectionResponse(BaseModel):
    data: TodoistSection

class CreateSectionResponse(BaseModel):
    data: TodoistSection

class UpdateSectionResponse(BaseModel):
    data: TodoistSection

class DeleteSectionResponse(BaseModel):
    data: bool

class GetTasksResponse(BaseModel):
    data: TaskList

class GetTaskResponse(BaseModel):
    data: TodoistTask

class CreateTaskResponse(BaseModel):
    data: TodoistTask

class UpdateTaskResponse(BaseModel):
    data: TodoistTask

class CloseTaskResponse(BaseModel):
    data: bool

class ReopenTaskResponse(BaseModel):
    data: bool

class DeleteTaskResponse(BaseModel):
    data: bool

# Response schema classes for Comments
class GetCommentsResponse(BaseModel):
    data: CommentList

class GetCommentResponse(BaseModel):
    data: TodoistComment

class CreateCommentResponse(BaseModel):
    data: TodoistComment

class UpdateCommentResponse(BaseModel):
    data: TodoistComment

class DeleteCommentResponse(BaseModel):
    data: bool

# Response schema classes for Labels
class GetPersonalLabelsResponse(BaseModel):
    data: PersonalLabelList

class GetPersonalLabelResponse(BaseModel):
    data: TodoistPersonalLabel

class CreatePersonalLabelResponse(BaseModel):
    data: TodoistPersonalLabel

class UpdatePersonalLabelResponse(BaseModel):
    data: TodoistPersonalLabel

class DeletePersonalLabelResponse(BaseModel):
    data: bool

class GetSharedLabelsResponse(BaseModel):
    data: List[str]

class RenameSharedLabelResponse(BaseModel):
    data: bool

class RemoveSharedLabelResponse(BaseModel):
    data: bool

# API Response
class ApiResponse(BaseModel):
    data: Union[
        ProjectList, TodoistProject, CollaboratorList, SectionList, TodoistSection, 
        TaskList, TodoistTask, CommentList, TodoistComment, PersonalLabelList, TodoistPersonalLabel,
        List[str], bool, GetSectionResponse, CreateSectionResponse, UpdateSectionResponse, DeleteSectionResponse, GetTasksResponse, GetTaskResponse, CreateTaskResponse, UpdateTaskResponse, CloseTaskResponse, ReopenTaskResponse, DeleteTaskResponse, GetProjectsResponse, CreateProjectResponse, GetProjectResponse, UpdateProjectResponse, DeleteProjectResponse, GetCollaboratorsResponse, GetSectionsResponse, GetTaskResponse, CreateTaskResponse, UpdateTaskResponse, CloseTaskResponse, ReopenTaskResponse, DeleteTaskResponse, GetSectionResponse, CreateSectionResponse, UpdateSectionResponse, DeleteSectionResponse, GetTasksResponse, GetTaskResponse, CreateTaskResponse, UpdateTaskResponse, CloseTaskResponse, ReopenTaskResponse, DeleteTaskResponse, GetCommentsResponse, GetCommentResponse, CreateCommentResponse, UpdateCommentResponse, DeleteCommentResponse, Dict[str, Any]
    ]
    component: Optional[Dict[str, Any]] = None
