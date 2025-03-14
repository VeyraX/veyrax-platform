from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union

# Base Models
class Avatar(BaseModel):
    avatarType: str
    avatarUuid: Optional[str] = None

class Organization(BaseModel):
    id: str
    slug: str
    name: str
    dateCreated: str
    status: Optional[Dict[str, Any]] = None
    avatar: Optional[Avatar] = None

class Team(BaseModel):
    id: str
    slug: str
    name: str
    dateCreated: str
    isMember: bool
    teamRole: Optional[str] = None
    access: List[str] = []
    memberCount: int
    avatar: Optional[Avatar] = None

class Project(BaseModel):
    id: str
    slug: str
    name: str
    platform: Optional[str] = None
    dateCreated: str
    isBookmarked: Optional[bool] = False
    isMember: Optional[bool] = False
    features: List[str] = []
    firstEvent: Optional[str] = None
    access: List[str] = []
    hasAccess: bool
    status: str
    avatar: Optional[Avatar] = None
    color: Optional[str] = None

class Issue(BaseModel):
    id: str
    shortId: str
    title: str
    culprit: str
    level: str
    status: str
    statusDetails: Optional[Dict[str, Any]] = None
    isSubscribed: bool
    isBookmarked: bool
    project: Project
    type: str
    metadata: Dict[str, Any]
    numComments: int
    assignedTo: Optional[Dict[str, Any]] = None
    count: str
    userCount: int
    firstSeen: str
    lastSeen: str

class Event(BaseModel):
    id: str
    eventID: str
    groupID: str
    title: str
    message: Optional[str] = None
    dateCreated: str
    user: Optional[Dict[str, Any]] = None
    tags: List[Dict[str, Any]] = []
    entries: List[Dict[str, Any]] = []
    metadata: Dict[str, Any]

class Release(BaseModel):
    id: str
    version: str
    dateCreated: str
    dateReleased: Optional[str] = None
    projects: List[Dict[str, Any]] = []
    url: Optional[str] = None
    newGroups: int
    commits: Optional[List[Dict[str, Any]]] = None

class AlertRule(BaseModel):
    id: str
    name: str
    conditions: List[Dict[str, Any]]
    actions: List[Dict[str, Any]]
    actionMatch: str
    dateCreated: str
    environment: Optional[str] = None
    frequency: int
    dateModified: str

class UserFeedback(BaseModel):
    id: str
    name: str
    email: str
    comments: str
    dateCreated: str
    issueId: str
    eventId: str
    event: Optional[Dict[str, Any]] = None

class ServiceHook(BaseModel):
    id: str
    url: str
    events: List[str]
    dateCreated: str
    status: str

# Collection Models
class OrganizationList(BaseModel):
    organizations: List[Organization]

class TeamList(BaseModel):
    teams: List[Team]

class ProjectList(BaseModel):
    projects: List[Project]

class IssueList(BaseModel):
    issues: List[Issue]
    cursor: Optional[str] = None

class EventList(BaseModel):
    events: List[Event]
    cursor: Optional[str] = None

class ReleaseList(BaseModel):
    releases: List[Release]
    cursor: Optional[str] = None

class AlertRuleList(BaseModel):
    rules: List[AlertRule]

class UserFeedbackList(BaseModel):
    feedback: List[UserFeedback]
    cursor: Optional[str] = None

class ServiceHookList(BaseModel):
    hooks: List[ServiceHook]

# Parameter Models
class ListOrganizationsParams(BaseModel):
    cursor: Optional[str] = None

class ListTeamsParams(BaseModel):
    cursor: Optional[str] = None

class CreateTeamParams(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None

class ListUserTeamsParams(BaseModel):
    cursor: Optional[str] = None

class ListProjectsParams(BaseModel):
    cursor: Optional[str] = None

class CreateProjectParams(BaseModel):
    name: str
    team_slug: str
    slug: Optional[str] = None
    platform: Optional[str] = None

class ListIssuesParams(BaseModel):
    project_slug: str
    query: Optional[str] = None
    status: Optional[str] = None
    cursor: Optional[str] = None

class GetIssueDetailsParams(BaseModel):
    issue_id: str

class ListIssueEventsParams(BaseModel):
    issue_id: str
    cursor: Optional[str] = None

class ListReleasesParams(BaseModel):
    query: Optional[str] = None
    cursor: Optional[str] = None

class CreateReleaseParams(BaseModel):
    version: str = Field(..., min_length=1, example="v1.2.3")
    projects: List[str] = Field(
        ...,
        min_length=1,
        example=["web-app", "mobile-app"],
        description="List of project SLUGS (not IDs) associated with this release"
    )
    ref: Optional[str] = Field(
        None,
        example="master",
        description="Repository reference (e.g. git commit SHA)"
    )
    url: Optional[str] = Field(
        None,
        example="https://github.com/your/repo/releases/tag/v1.2.3",
        description="URL to the release in your VCS"
    )
    dateReleased: Optional[str] = Field(
        None,
        example="2023-09-01T12:00:00Z",
        description="ISO 8601 timestamp in UTC"
    )

class ListAlertRulesParams(BaseModel):
    project_slug: str

class CreateAlertRuleParams(BaseModel):
    """
    Parameters for creating a new alert rule in Sentry
    
    Required Permissions:
    - project:write
    - alerts:write
    """
    project_slug: str = Field(
        ...,
        example="web-app",
        description="Slug of the project this alert rule belongs to (not ID)"
    )
    name: str = Field(
        ...,
        min_length=3,
        max_length=50,
        example="High Error Rate Alert",
        description="Unique name for the alert rule (3-50 characters)"
    )
    conditions: List[Dict[str, Any]] = Field(
        ...,
        example=[
            {
                "id": "sentry.rules.conditions.high_priority_issue.HighPriorityIssueCondition",
                "value": 90
            }
        ],
        description="List of condition configurations that trigger the alert"
    )
    actions: List[Dict[str, Any]] = Field(
        ...,
        example=[
            {
                "id": "sentry.mail.actions.NotifyEmailAction",
                "targetType": "Team",
                "targetIdentifier": "4508923808055296"
            }
        ],
        description="List of actions to perform when conditions are met"
    )
    actionMatch: str = Field(
        "all",
        example="any",
        description="How to combine conditions: 'all' (AND) or 'any' (OR)"
    )
    frequency: int = Field(
        30,
        ge=1,
        le=1440,
        example=60,
        description="Check frequency in minutes (1-1440)"
    )
    environment: Optional[str] = Field(
        None,
        example="production",
        description="Optional environment filter (name or 'null' for no environment)"
    )

class ListUserFeedbackParams(BaseModel):
    project_slug: str
    cursor: Optional[str] = None

class ListServiceHooksParams(BaseModel):
    project_slug: str

class CreateServiceHookParams(BaseModel):
    project_slug: str
    url: str
    events: List[str]

# Response Models
class ApiResponse(BaseModel):
    data: Union[Organization, OrganizationList, Team, TeamList, Project, ProjectList, 
                Issue, IssueList, Event, EventList, Release, ReleaseList, 
                AlertRule, AlertRuleList, UserFeedback, UserFeedbackList, 
                ServiceHook, ServiceHookList]
    component: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None

class OrganizationListResponse(BaseModel):
    data: OrganizationList
    message: Optional[str] = None

class TeamListResponse(BaseModel):
    data: TeamList
    message: Optional[str] = None

class TeamResponse(BaseModel):
    data: Team
    message: Optional[str] = None

class UserTeamsResponse(BaseModel):
    data: TeamList
    message: Optional[str] = None

class ProjectListResponse(BaseModel):
    data: ProjectList
    message: Optional[str] = None

class ProjectResponse(BaseModel):
    data: Project
    message: Optional[str] = None

class IssueListResponse(BaseModel):
    data: IssueList
    message: Optional[str] = None

class IssueResponse(BaseModel):
    data: Issue
    message: Optional[str] = None

class EventListResponse(BaseModel):
    data: EventList
    message: Optional[str] = None

class ReleaseListResponse(BaseModel):
    data: ReleaseList
    message: Optional[str] = None

class ReleaseResponse(BaseModel):
    data: Release
    message: Optional[str] = None

class AlertRuleListResponse(BaseModel):
    data: AlertRuleList
    message: Optional[str] = None

class AlertRuleResponse(BaseModel):
    data: AlertRule
    message: Optional[str] = None

class UserFeedbackListResponse(BaseModel):
    data: UserFeedbackList
    message: Optional[str] = None

class ServiceHookListResponse(BaseModel):
    data: ServiceHookList
    message: Optional[str] = None

class ServiceHookResponse(BaseModel):
    data: ServiceHook
    message: Optional[str] = None
