from pydantic import BaseModel, Field, validator, root_validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime

class ChecklistItem(BaseModel):
    id: Optional[str] = None
    title: str
    status: int = Field(0, ge=0, le=1)
    completed_time: Optional[datetime] = Field(None, alias="completedTime")
    is_all_day: Optional[bool] = Field(None, alias="isAllDay")
    sort_order: Optional[int] = Field(None, alias="sortOrder")
    start_date: Optional[datetime] = Field(None, alias="startDate")
    time_zone: Optional[str] = Field(None, alias="timeZone")

class TaskBase(BaseModel):
    title: str
    project_id: str = Field(..., alias="projectId")
    content: Optional[str] = None
    desc: Optional[str] = None
    is_all_day: Optional[bool] = Field(None, alias="isAllDay")
    start_date: Optional[datetime] = Field(None, alias="startDate")
    due_date: Optional[datetime] = Field(None, alias="dueDate")
    time_zone: Optional[str] = Field(None, alias="timeZone")
    reminders: Optional[List[str]] = None
    repeat_flag: Optional[str] = Field(None, alias="repeatFlag")
    priority: int = Field(0, ge=0, le=5)
    sort_order: Optional[int] = Field(None, alias="sortOrder")
    items: Optional[List[ChecklistItem]] = None

    class Config:
        allow_population_by_field_name = True

class TaskCreate(TaskBase):
    @root_validator(pre=True)
    def validate_create_fields(cls, values):
        if not values.get('title'):
            raise ValueError("Title is required for task creation")
        if not values.get('project_id'):
            raise ValueError("Project ID is required for task creation")
        return values

class TaskUpdate(TaskBase):
    id: str
    @root_validator(pre=True)
    def validate_update_fields(cls, values):
        if not values.get('id'):
            raise ValueError("Task ID is required for update")
        return values

class TaskResponse(TaskBase):
    id: str
    status: int = Field(..., ge=0, le=2)
    completed_time: Optional[datetime] = Field(None, alias="completedTime")
    
    @validator('items', pre=True)
    def transform_items(cls, v):
        return [ChecklistItem(**item) for item in v] if v else []

class ProjectBase(BaseModel):
    name: str
    color: Optional[str] = None
    sort_order: Optional[int] = Field(None, pattern="sortOrder")
    view_mode: Optional[str] = Field(None, alias="viewMode", pattern="^(list|kanban|timeline)$")
    kind: Optional[str] = Field(None, pattern="^(TASK|NOTE)$")

class ProjectCreate(ProjectBase):
    @validator('name')
    def name_required(cls, v):
        if not v:
            raise ValueError("Project name is required")
        return v

class ProjectUpdate(ProjectBase):
    pass

class ProjectResponse(ProjectBase):
    id: str
    closed: bool
    group_id: Optional[str] = Field(None, alias="groupId")
    permission: Optional[str] = None

class ProjectDataResponse(BaseModel):
    project: ProjectResponse
    tasks: List[TaskResponse]
    columns: List[Dict[str, Any]]

class TaskListResponse(BaseModel):
    items: List[TaskResponse]
    cursor: Optional[str] = None

class ProjectListResponse(BaseModel):
    items: List[ProjectResponse]
    cursor: Optional[str] = None

class ApiResponse(BaseModel):
    data: Union[TaskResponse, ProjectResponse, TaskListResponse, ProjectListResponse, ProjectDataResponse, Dict]
    component: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None
    message: Optional[str] = None

# Parameter classes for routes
class GetTaskParams(BaseModel):
    project_id: str
    task_id: str

class TaskOperationParams(BaseModel):
    project_id: str
    task_id: str

class ListTasksParams(BaseModel):
    cursor: Optional[str] = None
    max_results: Optional[int] = 50

class ProjectOperationParams(BaseModel):
    project_id: str 