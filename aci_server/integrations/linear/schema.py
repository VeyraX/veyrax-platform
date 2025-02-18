from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class User(BaseModel):
    id: str
    name: str
    email: Optional[str]

class Comment(BaseModel):
    id: str
    body: str
    user: User
    created_at: datetime

class Issue(BaseModel):
    id: str
    title: str
    description: Optional[str]
    state: str
    priority: Optional[int]
    assignee: Optional[User]
    creator: User
    created_at: datetime
    updated_at: datetime
    labels: Optional[List[str]]
    project_id: Optional[str]
    team_id: str
    identifier: str
    team_key: str

class IssueList(BaseModel):
    issues: List[Issue]
    cursor: Optional[str]

class Project(BaseModel):
    id: str
    name: str
    description: Optional[str]
    state: str
    created_at: datetime
    updated_at: datetime
    lead: Optional[User]

class ProjectList(BaseModel):
    projects: List[Project]
    cursor: Optional[str]

class IssueCreate(BaseModel):
    title: str
    team_id: str
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
    created_at: datetime
    user: Optional[User]

class UserList(BaseModel):
    users: List[User]
    cursor: Optional[str]

class Team(BaseModel):
    id: str
    name: str
    key: str
    description: Optional[str]

class TeamList(BaseModel):
    teams: List[Team]
    cursor: Optional[str]

class WorkflowState(BaseModel):
    id: str
    name: str
    color: str
    type: str
    position: int
    team_id: str
    team_key: str
    team_name: str

class WorkflowStateList(BaseModel):
    states: List[WorkflowState]
    cursor: Optional[str]