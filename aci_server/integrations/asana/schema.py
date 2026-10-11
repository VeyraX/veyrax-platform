from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from pydantic import validator

# Base models
class User(BaseModel):
    gid: str
    name: str
    email: Optional[str] = None
    photo: Optional[Dict[str, Any]] = None

class Workspace(BaseModel):
    gid: str
    name: str
    is_organization: Optional[bool] = None

class Team(BaseModel):
    gid: str
    name: str
    description: Optional[str] = None

class Project(BaseModel):
    gid: str
    name: str
    notes: Optional[str] = None
    archived: Optional[bool] = False
    color: Optional[str] = None
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
    due_date: Optional[str] = None
    owner: Optional[User] = None
    team: Optional[Team] = None
    workspace: Optional[Workspace] = None

class Tag(BaseModel):
    gid: str
    name: str
    color: Optional[str] = None
    workspace: Optional[Workspace] = None

class Task(BaseModel):
    gid: str
    name: str
    completed: bool = False
    due_on: Optional[str] = None
    notes: Optional[str] = None
    assignee: Optional[User] = None
    workspace: Optional[Workspace] = None
    projects: Optional[List[Project]] = None
    parent: Optional[str] = None
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None

class TaskList(BaseModel):
    items: List[Task]
    offset: Optional[str] = None

# Input schemas
class GetTasksParams(BaseModel):
    workspace_id: str
    project_id: Optional[str] = Field(
        None, 
        description="Project ID. Either project_id or assignee must be provided"
    )
    assignee: Optional[str] = Field(
        None, 
        description="Assignee ID. Either project_id or assignee must be provided"
    )
    completed_since: Optional[str] = None
    limit: Optional[int] = 20
    offset: Optional[str] = None

class GetTaskParams(BaseModel):
    task_id: str

class CreateTaskParams(BaseModel):
    task: Dict[str, Any]

class UpdateTaskParams(BaseModel):
    task_id: str
    task_update: Dict[str, Any]

class DeleteTaskParams(BaseModel):
    task_id: str

class GetSubtasksParams(BaseModel):
    task_id: str

class CreateSubtaskParams(BaseModel):
    parent_task_id: str
    subtask: Dict[str, Any]

class GetWorkspacesParams(BaseModel):
    limit: Optional[int] = 20
    offset: Optional[str] = None

class GetWorkspaceParams(BaseModel):
    workspace_id: str

class GetProjectsParams(BaseModel):
    workspace_id: Optional[str] = None
    team_id: Optional[str] = None
    archived: Optional[bool] = None
    limit: Optional[int] = 20
    offset: Optional[str] = None

class GetProjectParams(BaseModel):
    project_id: str

class GetTagsParams(BaseModel):
    workspace_id: Optional[str] = None
    limit: Optional[int] = 20
    offset: Optional[str] = None

class GetTagParams(BaseModel):
    tag_id: str

class GetTeamsParams(BaseModel):
    workspace_id: str
    limit: Optional[int] = 20
    offset: Optional[str] = None

class GetTeamParams(BaseModel):
    team_id: str

class GetUsersParams(BaseModel):
    workspace_id: Optional[str] = None
    team_id: Optional[str] = None
    limit: Optional[int] = 20
    offset: Optional[str] = None

class GetUserParams(BaseModel):
    user_id: str

# Output schemas
class GetTasksResponse(BaseModel):
    data: TaskList
    message: Optional[str] = None

class GetTaskResponse(BaseModel):
    data: Task
    message: Optional[str] = None

class CreateTaskResponse(BaseModel):
    data: Task
    message: Optional[str] = None

class UpdateTaskResponse(BaseModel):
    data: Task
    message: Optional[str] = None

class DeleteTaskResponse(BaseModel):
    data: Dict[str, Any]
    message: Optional[str] = None

class GetSubtasksResponse(BaseModel):
    data: TaskList
    message: Optional[str] = None

class CreateSubtaskResponse(BaseModel):
    data: Task
    message: Optional[str] = None

class GetWorkspacesResponse(BaseModel):
    data: List[Workspace]
    message: Optional[str] = None

class GetWorkspaceResponse(BaseModel):
    data: Workspace
    message: Optional[str] = None

class GetProjectsResponse(BaseModel):
    data: List[Project]
    message: Optional[str] = None

class GetProjectResponse(BaseModel):
    data: Project
    message: Optional[str] = None

class GetTagsResponse(BaseModel):
    data: List[Tag]
    message: Optional[str] = None

class GetTagResponse(BaseModel):
    data: Tag
    message: Optional[str] = None

class GetTeamsResponse(BaseModel):
    data: List[Team]
    message: Optional[str] = None

class GetTeamResponse(BaseModel):
    data: Team
    message: Optional[str] = None

class GetUsersResponse(BaseModel):
    data: List[User]
    message: Optional[str] = None

class GetUserResponse(BaseModel):
    data: User
    message: Optional[str] = None

# Add new base models for goals
class TimePeriod(BaseModel):
    gid: str
    name: str
    start_on: Optional[str] = None
    end_on: Optional[str] = None

class GoalMetric(BaseModel):
    gid: str
    name: str
    progress_value: Optional[float] = None
    target_number_value: Optional[float] = None
    current_number_value: Optional[float] = None
    unit: Optional[str] = None
    precision: Optional[int] = None

class Goal(BaseModel):
    gid: str
    name: str
    due_on: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = Field(
        None, 
        description="Goal status. Must be one of: achieved, dropped, green, missed, partial, red, yellow. Note: Goal metric must be set before setting status"
    )
    owner: Optional[User] = None
    workspace: Optional[Workspace] = None
    time_period: Optional[TimePeriod] = None
    metric: Optional[GoalMetric] = None
    is_workspace_level: Optional[bool] = False
    liked: Optional[bool] = False
    
class GoalList(BaseModel):
    items: List[Goal]
    offset: Optional[str] = None

# Add input schemas for goal operations
class GetGoalsParams(BaseModel):
    workspace_id: str
    time_period_id: Optional[str] = None
    owner_id: Optional[str] = None
    is_workspace_level: Optional[bool] = None
    limit: Optional[int] = 20
    offset: Optional[str] = None

class GetGoalParams(BaseModel):
    goal_id: str

class CreateGoalParams(BaseModel):
    goal: Dict[str, Any]

class UpdateGoalParams(BaseModel):
    goal_id: str
    goal_update: Dict[str, Any]

# Add output schemas for goal operations
class GetGoalsResponse(BaseModel):
    data: GoalList
    message: Optional[str] = None

class GetGoalResponse(BaseModel):
    data: Goal
    message: Optional[str] = None

class CreateGoalResponse(BaseModel):
    data: Goal
    message: Optional[str] = None

class UpdateGoalResponse(BaseModel):
    data: Goal
    message: Optional[str] = None

class UserList(BaseModel):
    items: List[User]
    offset: Optional[str] = None

class WorkspaceList(BaseModel):
    items: List[Workspace]
    offset: Optional[str] = None


# Add to the base models section
class Section(BaseModel):
    gid: str
    name: str
    project: Optional[Project] = None
    created_at: Optional[datetime] = None

class SectionList(BaseModel):
    items: List[Section]
    offset: Optional[str] = None

# Add to the input schemas section
class GetSectionsParams(BaseModel):
    project_id: str

class GetSectionParams(BaseModel):
    section_id: str

class GetSectionTasksParams(BaseModel):
    section_id: str
    limit: Optional[int] = 20
    offset: Optional[str] = None

# Add to the output schemas section
class GetSectionsResponse(BaseModel):
    data: SectionList
    message: Optional[str] = None

class GetSectionResponse(BaseModel):
    data: Section
    message: Optional[str] = None

class GetSectionTasksResponse(BaseModel):
    data: TaskList
    message: Optional[str] = None

# Add to the input schemas section
class GetTimePeriodsParams(BaseModel):
    workspace_id: str
    limit: Optional[int] = 20
    offset: Optional[str] = None

# Add to the output schemas section
class TimePeriodList(BaseModel):
    items: List[TimePeriod]
    offset: Optional[str] = None

class GetTimePeriodsResponse(BaseModel):
    data: TimePeriodList
    message: Optional[str] = None

# Update ApiResponse to include TimePeriodList
class ApiResponse(BaseModel):
    data: Union[
        Task, TaskList, 
        Project, List[Project], 
        Tag, List[Tag], 
        Team, List[Team], 
        User, List[User], UserList,
        Workspace, List[Workspace], WorkspaceList,
        Goal, GoalList, 
        GoalMetric,
        Section, SectionList,
        TimePeriodList,
        Dict[str, Any]
    ]
    component: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None