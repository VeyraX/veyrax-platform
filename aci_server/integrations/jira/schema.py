from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class JiraServerInfo(BaseModel):
    cloud_id: str
    base_url: str
    version: str
    title: str

class JiraCredentials(BaseModel):
    access_token: str
    server_info: JiraServerInfo

class StatusSchema(BaseModel):
    name: str
    statusCategory: Optional[Dict[str, Any]] = None

class PrioritySchema(BaseModel):
    name: str
    id: Optional[str] = None
    iconUrl: Optional[str] = None

class IssueBase(BaseModel):
    key: str
    summary: str
    description: Optional[str]
    status: StatusSchema
    created: datetime
    updated: datetime
    assignee: Optional[Dict[str, Any]]
    reporter: Optional[str]
    priority: Optional[PrioritySchema]
    url: str

class Issue(IssueBase):
    comments: List[Dict[str, Any]] = []
    labels: List[str] = []
    components: List[str] = []
    created: datetime = Field(default_factory=datetime.now)
    updated: datetime = Field(default_factory=datetime.now)

class IssueCreate(BaseModel):
    project_id: str
    summary: str
    issue_type_id: str
    description: Optional[str] = None
    assignee_id: Optional[str] = None
    priority_id: Optional[str] = None
    parent_issue_key: Optional[str] = None
    status_id: Optional[str] = None
    labels: Optional[List[str]] = None
    components: Optional[List[str]] = None

class IssueUpdate(BaseModel):
    summary: Optional[str] = None
    description: Optional[str] = None
    assignee_id: Optional[str] = None
    priority_id: Optional[str] = None
    status_id: Optional[str] = None
    labels: Optional[List[str]] = None
    components: Optional[List[str]] = None

class IssueList(BaseModel):
    issues: List[IssueBase]
    total: int
    start_at: int

class IssueFilters(BaseModel):
    project_id: Optional[str] = None
    status_id: Optional[str] = None
    assignee: Optional[str] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    priority_id: Optional[str] = None
    max_results: Optional[int] = 50

    class Config:
        extra = "forbid"

class ProjectBase(BaseModel):
    id: str
    key: str
    name: str
    description: Optional[str]

class Project(ProjectBase):
    lead: Optional[str]
    url: str
    components: List[Dict[str, Any]]
    versions: List[Dict[str, Any]]

class StatusCategory(BaseModel):
    id: int
    key: str
    name: str
    colorName: str

class Status(BaseModel):
    id: str
    name: str
    description: Optional[str]
    category: StatusCategory

class Priority(BaseModel):
    id: str
    name: str
    description: Optional[str]
    iconUrl: str

class IssueType(BaseModel):
    id: str
    name: str
    description: Optional[str]
    iconUrl: str
    subtask: bool

class FieldSchema(BaseModel):
    type: str
    items: Optional[str] = None
    system: Optional[str] = None
    custom: Optional[str] = None

class Field(BaseModel):
    id: str
    name: str
    custom: bool
    orderable: bool
    navigable: bool
    searchable: bool
    clauseNames: Optional[List[str]] = None
    schema: Optional[FieldSchema] = None

class JiraUser(BaseModel):
    account_id: str
    email: Optional[str]
    display_name: str
    active: bool