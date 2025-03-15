from pydantic import BaseModel, Field, model_validator, UUID4
from typing import List, Optional, Dict, Any, Union
from datetime import datetime

class User(BaseModel):
    id: str
    name: str
    email: Optional[str] = None

class State(BaseModel):
    id: str
    name: str

class Team(BaseModel):
    id: str
    name: Optional[str] = None
    key: str
    description: Optional[str] = None

class Label(BaseModel):
    name: str

class LabelConnection(BaseModel):
    nodes: List[Label]

class Issue(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    state: Optional[Union[str, State]] = None
    priority: Optional[int] = None
    assignee: Optional[User] = None
    creator: Optional[User] = None
    createdAt: Optional[datetime] = Field(None, alias="created_at")
    updatedAt: Optional[datetime] = Field(None, alias="updated_at")
    labels: Optional[Union[List[str], LabelConnection]] = None
    project: Optional[Dict[str, Any]] = None
    team: Optional[Team] = None
    identifier: Optional[str] = None
    
    @model_validator(mode='after')
    def extract_nested_fields(self):
        if isinstance(self.state, dict) and 'name' in self.state:
            self.state = self.state['name']
            
        if isinstance(self.labels, dict) and 'nodes' in self.labels:
            self.labels = [label['name'] for label in self.labels['nodes']]
            
        self.project_id = self.project['id'] if self.project and 'id' in self.project else None
        
        if self.team:
            self.team_id = self.team.id
            self.team_key = self.team.key
        else:
            self.team_id = ""
            self.team_key = ""
            
        return self
    
    # Дополнительные поля для совместимости
    project_id: Optional[str] = None
    team_id: str = ""
    team_key: str = ""

class IssueList(BaseModel):
    items: List[Issue]
    cursor: Optional[str] = None

class Project(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    state: str
    createdAt: datetime = Field(alias="created_at")
    updatedAt: datetime = Field(alias="updated_at")
    lead: Optional[User] = None
    
    class Config:
        populate_by_name = True

class ProjectList(BaseModel):
    items: List[Project]
    cursor: Optional[str] = None

class IssueCreate(BaseModel):
    title: str
    team_id: str = Field(..., format="uuid")
    description: Optional[str] = None
    assignee_id: Optional[str] = None
    state_id: Optional[str] = None
    priority: Optional[int] = None
    project_id: Optional[str] = None
    labels: Optional[List[str]] = None

    class Config:
        extra = "forbid"

class IssueUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assignee_id: Optional[str] = None
    state_id: Optional[str] = None
    priority: Optional[int] = None
    project_id: Optional[str] = None
    labels: Optional[List[str]] = None

    class Config:
        extra = "forbid"

class CommentCreate(BaseModel):
    body: str

class IssueFilter(BaseModel):
    assignee_id: Optional[str] = None
    creator_id: Optional[str] = None
    project_id: Optional[str] = None
    state_id: Optional[str] = None
    priority: Optional[int] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None

    class Config:
        extra = "forbid"

class CommentResponse(BaseModel):
    id: str
    body: str
    created_at: datetime = Field(alias="createdAt")
    user: Optional[User] = None

    class Config:
        populate_by_name = True

class UserList(BaseModel):
    items: List[User]
    cursor: Optional[str] = None

class TeamList(BaseModel):
    items: List[Team]
    cursor: Optional[str] = None

class WorkflowState(BaseModel):
    id: str
    name: str
    color: str
    type: str
    position: int
    team: Optional[Team] = None
    
    @model_validator(mode='after')
    def extract_team_fields(self):
        if self.team:
            self.team_id = self.team.id
            self.team_key = self.team.key
            self.team_name = self.team.name or ""
        else:
            self.team_id = ""
            self.team_key = ""
            self.team_name = ""
        return self
    
    # Дополнительные поля для совместимости
    team_id: str = ""
    team_key: str = ""
    team_name: str = ""

class WorkflowStateList(BaseModel):
    items: List[WorkflowState]
    cursor: Optional[str] = None

class ApiResponse(BaseModel):
    data: Union[Issue, IssueList, Project, ProjectList, Team, TeamList, WorkflowState, WorkflowStateList, CommentResponse, UserList]
    component: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None

# New parameter classes for routes
class ListIssuesParams(BaseModel):
    cursor: Optional[str] = None
    max_results: Optional[int] = 50

class SearchIssuesParams(BaseModel):
    query: str
    cursor: Optional[str] = None
    max_results: Optional[int] = 50

class FilterIssuesParams(BaseModel):
    filters: IssueFilter
    cursor: Optional[str] = None
    max_results: Optional[int] = 50

class CreateIssueParams(BaseModel):
    issue: IssueCreate

class UpdateIssueParams(BaseModel):
    issue_id: str
    issue_update: IssueUpdate

class CommentIssueParams(BaseModel):
    issue_id: str
    comment: CommentCreate

class ListProjectsParams(BaseModel):
    cursor: Optional[str] = None
    max_results: Optional[int] = 50

class GetProjectParams(BaseModel):
    project_id: str = Field(..., format="uuid")

class ListUsersParams(BaseModel):
    cursor: Optional[str] = None
    max_results: Optional[int] = 50

class ListTeamsParams(BaseModel):
    cursor: Optional[str] = None
    max_results: Optional[int] = 50

class GetTeamParams(BaseModel):
    team_id: str = Field(..., format="uuid")

class ListWorkflowStatesParams(BaseModel):
    cursor: Optional[str] = None
    max_results: Optional[int] = 50


# Response schema classes
class ListIssuesResponse(BaseModel):
    data: IssueList
    message: Optional[str] = None

class SearchIssuesResponse(BaseModel):
    data: IssueList
    message: Optional[str] = None

class FilterIssuesResponse(BaseModel):
    data: IssueList
    message: Optional[str] = None

class CreateIssueResponse(BaseModel):
    data: Issue
    message: Optional[str] = None

class UpdateIssueResponse(BaseModel):
    data: Issue
    message: Optional[str] = None

class CommentIssueResponse(BaseModel):
    data: CommentResponse
    message: Optional[str] = None

class ListProjectsResponse(BaseModel):
    data: ProjectList
    message: Optional[str] = None

class GetProjectResponse(BaseModel):
    data: Project
    message: Optional[str] = None

class ListUsersResponse(BaseModel):
    data: UserList
    message: Optional[str] = None

class ListTeamsResponse(BaseModel):
    data: TeamList
    message: Optional[str] = None

class GetTeamResponse(BaseModel):
    data: Team
    message: Optional[str] = None

class ListWorkflowStatesResponse(BaseModel):
    data: WorkflowStateList
    message: Optional[str] = None

class ProjectCreate(BaseModel):
    name: str
    team_id: str = Field(..., alias="teamId")
    description: Optional[str] = None
    state: Optional[str] = None
    lead_id: Optional[str] = Field(None, alias="leadId")
    start_date: Optional[datetime] = Field(None, alias="startDate")
    target_date: Optional[datetime] = Field(None, alias="targetDate")

    class Config:
        populate_by_name = True
        alias_generator = lambda x: ''.join(word.capitalize() if i else word for i, word in enumerate(x.split('_')))
        extra = "forbid"

# Add to parameter classes
class ListLabelsParams(BaseModel):
    cursor: Optional[str] = None
    max_results: Optional[int] = 50

# Add to response schema classes
class LabelListItem(BaseModel):
    id: str
    name: str
    color: Optional[str] = None

class LabelList(BaseModel):
    items: List[LabelListItem]
    cursor: Optional[str] = None

class ListLabelsResponse(BaseModel):
    data: LabelList
    message: Optional[str] = None

