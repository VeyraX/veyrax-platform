from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union, Literal
from datetime import datetime

class HogQLQuery(BaseModel):
    kind: Literal["HogQLQuery"] = "HogQLQuery"
    query: str = Field(..., description="HogQL SQL query string")

class QueryParams(BaseModel):
    project_id: str = Field(..., description="Project ID to query")
    query: HogQLQuery = Field(..., description="The query to execute")
    async_query: Optional[bool] = Field(False, description="Whether to run the query asynchronously")
    client_query_id: Optional[str] = Field(None, description="Client provided query ID")
    refresh: Optional[Literal["blocking", "async", "lazy_async", "force_blocking", "force_async", "force_cache"]] = Field(
        "blocking", 
        description="How results should be calculated and how much to rely on cache"
    )
    filters_override: Optional[Dict[str, Any]] = Field(None, description="Override filters for the query")
    variables_override: Optional[Dict[str, Any]] = Field(None, description="Override variables for the query")

class GetQueryParams(BaseModel):
    project_id: str = Field(..., description="Project ID")
    query_id: str = Field(..., description="ID of the query to retrieve")

class DeleteQueryParams(BaseModel):
    project_id: str = Field(..., description="Project ID")
    query_id: str = Field(..., description="ID of the query to delete")

# Классы для статуса и результатов запроса не изменяются
class QueryStatus(BaseModel):
    complete: bool
    dashboard_id: Optional[str] = None
    end_time: Optional[str] = None
    error: bool
    error_message: Optional[str] = None
    expiration_time: Optional[str] = None
    id: str
    insight_id: Optional[str] = None
    labels: Optional[List[str]] = None
    pickup_time: Optional[str] = None
    query_async: bool
    query_progress: Optional[float] = None
    results: Optional[Dict[str, Any]] = None
    start_time: Optional[str] = None
    task_id: Optional[str] = None
    team_id: int

class QueryResult(BaseModel):
    results: Union[List[Any], Dict[str, Any]] = Field(default_factory=list)
    columns: List[str] = Field(default_factory=list)
    types: Optional[Union[List[Any], str]] = None
    hogql: Optional[str] = None
    query_status: Optional[QueryStatus] = None
    
    cache_key: Optional[str] = None
    last_refresh: Optional[str] = None
    is_cached: Optional[bool] = None
    next_allowed_client_refresh: Optional[str] = None

class User(BaseModel):
    id: int
    uuid: str
    distinct_id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    is_email_verified: Optional[bool] = None
    hedgehog_config: Optional[Dict[str, Any]] = None
    role_at_organization: Optional[str] = None

class DashboardTile(BaseModel):
    id: Optional[int] = None
    dashboard_id: Optional[int] = None
    insight_id: Optional[int] = None
    text: Optional[str] = None
    color: Optional[str] = None
    deleted: Optional[bool] = None
    layouts: Optional[Dict[str, Any]] = None
    filters: Optional[Dict[str, Any]] = None

class Dashboard(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    pinned: Optional[bool] = None
    created_at: Optional[datetime] = None
    created_by: Optional[User] = None
    is_shared: Optional[bool] = None
    deleted: Optional[bool] = None
    creation_mode: Optional[str] = None
    tags: Optional[List[Any]] = None
    restriction_level: Optional[int] = None
    effective_restriction_level: Optional[int] = None
    effective_privilege_level: Optional[int] = None
    user_access_level: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None
    variables: Optional[Dict[str, Any]] = None
    tiles: Optional[List[DashboardTile]] = None

class DashboardsList(BaseModel):
    count: int
    next: Optional[str] = None
    previous: Optional[str] = None
    results: List[Dashboard]

class Insight(BaseModel):
    id: int
    short_id: str
    name: Optional[str] = None
    derived_name: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None
    query: Optional[Dict[str, Any]] = None
    order: Optional[int] = None
    deleted: Optional[bool] = None
    dashboards: Optional[List[int]] = None
    dashboard_tiles: Optional[List[DashboardTile]] = None
    last_refresh: Optional[str] = None
    cache_target_age: Optional[str] = None
    next_allowed_client_refresh: Optional[str] = None
    result: Optional[Any] = None
    hasMore: Optional[Union[str, bool]] = None
    columns: Optional[Any] = None
    created_at: Optional[datetime] = None
    created_by: Optional[User] = None
    description: Optional[str] = None
    updated_at: Optional[datetime] = None
    tags: Optional[List[Any]] = None
    favorited: Optional[bool] = None
    saved: Optional[bool] = None
    last_modified_at: Optional[datetime] = None
    last_modified_by: Optional[User] = None
    is_sample: Optional[bool] = None
    effective_restriction_level: Optional[int] = None
    effective_privilege_level: Optional[int] = None
    user_access_level: Optional[str] = None
    timezone: Optional[str] = None
    is_cached: Optional[Union[str, bool]] = None
    query_status: Optional[str] = None
    hogql: Optional[str] = None
    types: Optional[Union[str, List[Any]]] = None

class InsightsList(BaseModel):
    count: int
    next: Optional[str] = None
    previous: Optional[str] = None
    results: List[Insight]

class SuccessResponse(BaseModel):
    success: bool

class QueryResultResponse(BaseModel):
    data: QueryResult
    component: Optional[Dict[str, Any]] = None

class QueryStatusResponse(BaseModel):
    data: QueryStatus
    component: Optional[Dict[str, Any]] = None

class InsightResponse(BaseModel):
    data: Insight
    component: Optional[Dict[str, Any]] = None

class InsightsListResponse(BaseModel):
    data: InsightsList
    component: Optional[Dict[str, Any]] = None

class DashboardResponse(BaseModel):
    data: Dashboard
    component: Optional[Dict[str, Any]] = None

class DashboardsListResponse(BaseModel):
    data: DashboardsList
    component: Optional[Dict[str, Any]] = None

class ValidateKeyResponse(BaseModel):
    valid: bool
    message: str

class Event(BaseModel):
    id: str
    distinct_id: str
    properties: Dict[str, Any]
    event: str
    timestamp: str
    person: Optional[Dict[str, Any]] = None
    elements: Optional[List[Dict[str, Any]]] = None
    elements_chain: Optional[str] = None

class EventsList(BaseModel):
    next: Optional[str] = None
    previous: Optional[str] = None
    results: List[Event]

# Добавляем project_id для схем, связанных с проектом
class ListEventsParams(BaseModel):
    project_id: str = Field(..., description="Project ID")
    after: Optional[str] = Field(None, description="Only return events with a timestamp after this time")
    before: Optional[str] = Field(None, description="Only return events with a timestamp before this time")
    distinct_id: Optional[str] = Field(None, description="Filter list by distinct id")
    event: Optional[str] = Field(None, description="Filter list by event (e.g. user sign up or $pageview)")
    format: Optional[Literal["csv", "json"]] = Field(None, description="Response format (csv or json)")
    limit: Optional[int] = Field(100, ge=1, le=1000, description="The maximum number of results to return")
    offset: Optional[int] = Field(0, ge=0, description="The initial index from which to return the results")
    person_id: Optional[int] = Field(None, description="Filter list by person id")
    properties: Optional[List[Dict[str, Any]]] = Field(None, description="Filter events by properties")
    select: Optional[List[str]] = Field(None, description="(Experimental) JSON-serialized array of HogQL expressions to return")
    where: Optional[List[str]] = Field(None, description="(Experimental) JSON-serialized array of HogQL expressions that must pass")

class GetEventParams(BaseModel):
    project_id: str = Field(..., description="Project ID")
    event_id: str = Field(..., description="ID of the event to retrieve")
    format: Optional[Literal["csv", "json"]] = Field(None, description="Response format (csv or json)")

class EventResponse(BaseModel):
    data: Event
    component: Optional[Dict[str, Any]] = None

class EventsListResponse(BaseModel):
    data: EventsList
    component: Optional[Dict[str, Any]] = None

class DashboardTitle(BaseModel):
    id: int
    dashboard_id: int
    deleted: Optional[bool] = None

class InsightParams(BaseModel):
    project_id: str = Field(..., description="Project ID")
    name: Optional[str] = None
    derived_name: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None
    query: Optional[Dict[str, Any]] = None
    order: Optional[int] = None
    deleted: Optional[bool] = None
    dashboards: Optional[List[int]] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    favorited: Optional[bool] = None
    saved: Optional[bool] = None

class ListInsightsParams(BaseModel):
    project_id: str = Field(..., description="Project ID")
    created_by: Optional[int] = None
    limit: Optional[int] = Field(100, ge=1, le=1000, description="Number of results to return per page")
    offset: Optional[int] = Field(0, ge=0, description="The initial index from which to return the results")
    refresh: Optional[Literal["async", "async_except_on_cache_miss", "blocking", "force_async", "force_blocking", "force_cache", "lazy_async"]] = Field(
        "force_cache",
        description="Whether to refresh insights, how aggressively, and if sync or async"
    )
    short_id: Optional[str] = None

class GetInsightParams(BaseModel):
    project_id: str = Field(..., description="Project ID")
    insight_id: int = Field(..., description="ID of the insight to retrieve")
    from_dashboard: Optional[int] = Field(None, description="ID of the dashboard from which the insight is being loaded")
    refresh: Optional[str] = Field("force_cache", description="How to refresh the data")

class UpdateInsightParams(BaseModel):
    project_id: str = Field(..., description="Project ID")
    insight_id: int = Field(..., description="ID of the insight to update")
    name: Optional[str] = None
    derived_name: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None
    query: Optional[Dict[str, Any]] = None
    order: Optional[int] = None
    deleted: Optional[bool] = None
    dashboards: Optional[List[int]] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    favorited: Optional[bool] = None
    saved: Optional[bool] = None

class ValidateKeyParams(BaseModel):
    api_key: str = Field(..., description="PostHog API key")
    base_url: Optional[str] = Field("https://us.posthog.com", description="PostHog API base URL")

class DashboardParams(BaseModel):
    project_id: str = Field(..., description="Project ID")
    name: str = Field(..., description="Dashboard name")
    description: Optional[str] = Field(None, description="Dashboard description")
    pinned: Optional[bool] = Field(None, description="Pin dashboard to the top")
    tags: Optional[List[str]] = Field(None, description="Tags for the dashboard")
    filters: Optional[Dict[str, Any]] = Field(None, description="Dashboard filters")

class GetDashboardParams(BaseModel):
    project_id: str = Field(..., description="Project ID")
    dashboard_id: int = Field(..., description="ID of the dashboard to retrieve")

class UpdateDashboardParams(BaseModel):
    project_id: str = Field(..., description="Project ID")
    dashboard_id: int = Field(..., description="ID of the dashboard to update")
    name: Optional[str] = None
    description: Optional[str] = None
    pinned: Optional[bool] = None
    deleted: Optional[bool] = None
    tags: Optional[List[str]] = None
    filters: Optional[Dict[str, Any]] = None
    variables: Optional[Dict[str, Any]] = None

class ListDashboardsParams(BaseModel):
    project_id: str = Field(..., description="Project ID")
    limit: Optional[int] = Field(100, ge=1, le=1000, description="Number of results to return per page")
    offset: Optional[int] = Field(0, ge=0, description="The initial index from which to return the results")

class Project(BaseModel):
    id: int
    uuid: str
    organization: str
    api_token: str
    name: str
    completed_snippet_onboarding: Optional[bool] = None
    has_completed_onboarding_for: Optional[Any] = None
    ingested_event: Optional[bool] = None
    is_demo: Optional[bool] = None
    timezone: Optional[str] = None
    access_control: Optional[bool] = None

class ProjectsList(BaseModel):
    count: int
    next: Optional[str] = None
    previous: Optional[str] = None
    results: List[Project]

class ListProjectsParams(BaseModel):
    organization_id: str = Field(..., description="Organization ID")
    limit: Optional[int] = Field(100, ge=1, le=1000, description="Number of results to return per page")
    offset: Optional[int] = Field(0, ge=0, description="The initial index from which to return the results")

class GetProjectParams(BaseModel):
    project_id: int = Field(..., description="ID of the project to retrieve")
    organization_id: str = Field(..., description="ID of the organization the project belongs to")

class ProjectResponse(BaseModel):
    data: Project
    component: Optional[Dict[str, Any]] = None

class ProjectsListResponse(BaseModel):
    data: ProjectsList
    component: Optional[Dict[str, Any]] = None

class Organization(BaseModel):
    id: str
    name: str
    slug: Optional[str] = None
    logo_media_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    membership_level: Optional[int] = None
    plugins_access_level: Optional[int] = None
    teams: Optional[List[Dict[str, Any]]] = None
    projects: Optional[List[Dict[str, Any]]] = None
    available_product_features: Optional[List[Any]] = None
    is_member_join_email_enabled: Optional[bool] = None
    metadata: Optional[Union[str, Dict[str, Any]]] = None
    customer_id: Optional[str] = None
    enforce_2fa: Optional[bool] = None
    member_count: Optional[Union[str, int]] = None
    is_ai_data_processing_approved: Optional[bool] = None

class OrganizationsList(BaseModel):
    count: int
    next: Optional[str] = None
    previous: Optional[str] = None
    results: List[Organization]

class ListOrganizationsParams(BaseModel):
    limit: Optional[int] = Field(100, ge=1, le=1000, description="Number of results to return per page")
    offset: Optional[int] = Field(0, ge=0, description="The initial index from which to return the results")

class GetOrganizationParams(BaseModel):
    organization_id: str = Field(..., description="ID of the organization to retrieve")

class OrganizationResponse(BaseModel):
    data: Organization
    component: Optional[Dict[str, Any]] = None

class OrganizationsListResponse(BaseModel):
    data: OrganizationsList
    component: Optional[Dict[str, Any]] = None

class OrganizationUser(BaseModel):
    id: int
    uuid: str
    distinct_id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    is_email_verified: Optional[bool] = None
    hedgehog_config: Optional[Dict[str, Any]] = None
    role_at_organization: Optional[str] = None

class OrganizationMember(BaseModel):
    id: str
    user: OrganizationUser
    level: int
    joined_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_2fa_enabled: Optional[bool] = None
    has_social_auth: Optional[bool] = None
    last_login: Optional[datetime] = None

class OrganizationMembersList(BaseModel):
    count: int
    next: Optional[str] = None
    previous: Optional[str] = None
    results: List[OrganizationMember]

class ListOrganizationMembersParams(BaseModel):
    organization_id: str = Field(..., description="ID of the organization to get members from")
    limit: Optional[int] = Field(100, ge=1, le=1000, description="Number of results to return per page")
    offset: Optional[int] = Field(0, ge=0, description="The initial index from which to return the results")

class OrganizationMembersListResponse(BaseModel):
    data: OrganizationMembersList
    component: Optional[Dict[str, Any]] = None

class Person(BaseModel):
    id: Union[int, str]
    name: Optional[str] = None
    distinct_ids: List[str]
    properties: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    uuid: Optional[str] = None

class PersonsList(BaseModel):
    count: Optional[int] = None
    next: Optional[str] = None
    previous: Optional[str] = None
    results: List[Person]

class ListPersonsParams(BaseModel):
    project_id: str = Field(..., description="Project ID")
    distinct_id: Optional[str] = Field(None, description="Filter list by distinct id")
    email: Optional[str] = Field(None, description="Filter persons by email (exact match)")
    search: Optional[str] = Field(None, description="Search persons by email or distinct_id")
    properties: Optional[List[Dict[str, Any]]] = Field(None, description="Filter Persons by person properties")
    format: Optional[Literal["csv", "json"]] = Field(None, description="Response format")
    limit: Optional[int] = Field(100, ge=1, le=1000, description="Number of results to return per page")
    offset: Optional[int] = Field(0, ge=0, description="The initial index from which to return the results")

class GetPersonParams(BaseModel):
    project_id: str = Field(..., description="Project ID")
    person_id: Union[int, str] = Field(..., description="ID of the person to retrieve")
    format: Optional[Literal["csv", "json"]] = Field(None, description="Response format")

class UpdatePersonParams(BaseModel):
    project_id: str = Field(..., description="Project ID")
    person_id: Union[int, str] = Field(..., description="ID of the person to update")
    properties: Dict[str, Any] = Field(..., description="Person properties to update")

class DeletePersonParams(BaseModel):
    project_id: str = Field(..., description="Project ID")
    person_id: Union[int, str] = Field(..., description="ID of the person to delete")
    delete_events: Optional[bool] = Field(False, description="If true, delete all events associated with this person")

class BulkDeletePersonsParams(BaseModel):
    project_id: str = Field(..., description="Project ID")
    ids: Optional[List[Union[int, str]]] = Field(None, description="A list of PostHog person IDs to delete")
    distinct_ids: Optional[List[str]] = Field(None, description="A list of distinct IDs to delete")
    delete_events: Optional[bool] = Field(False, description="If true, delete all events associated with these persons")

class PersonResponse(BaseModel):
    data: Person
    component: Optional[Dict[str, Any]] = None

class PersonsListResponse(BaseModel):
    data: PersonsList
    component: Optional[Dict[str, Any]] = None

class ActionStep(BaseModel):
    event: Optional[str] = None
    properties: Optional[List[Dict[str, Any]]] = None
    selector: Optional[str] = None
    tag_name: Optional[str] = None
    text: Optional[str] = None
    text_matching: Optional[Literal["contains", "exact", "regex"]] = "contains"
    href: Optional[str] = None
    href_matching: Optional[Literal["contains", "exact", "regex"]] = "contains"
    url: Optional[str] = None
    url_matching: Optional[Literal["contains", "exact", "regex"]] = "contains"

class Action(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    tags: Optional[List[Any]] = None
    post_to_slack: Optional[bool] = None
    slack_message_format: Optional[str] = None
    steps: Optional[List[ActionStep]] = None
    created_at: Optional[datetime] = None
    created_by: Optional[User] = None
    deleted: Optional[bool] = None
    is_calculating: Optional[bool] = None
    last_calculated_at: Optional[datetime] = None
    team_id: Optional[int] = None
    is_action: Optional[bool] = None
    bytecode_error: Optional[str] = None
    pinned_at: Optional[datetime] = None
    creation_context: Optional[str] = None

class ActionsList(BaseModel):
    count: Optional[int] = 0
    next: Optional[str] = None
    previous: Optional[str] = None
    results: List[Action]

class ListActionsParams(BaseModel):
    project_id: str = Field(..., description="Project ID")
    format: Optional[Literal["csv", "json"]] = Field(None, description="Response format")
    limit: Optional[int] = Field(100, ge=1, le=1000, description="Number of results to return per page")
    offset: Optional[int] = Field(0, ge=0, description="The initial index from which to return the results")

class GetActionParams(BaseModel):
    project_id: str = Field(..., description="Project ID")
    action_id: int = Field(..., description="ID of the action to retrieve")
    format: Optional[Literal["csv", "json"]] = Field(None, description="Response format")

class ActionParams(BaseModel):
    project_id: str = Field(..., description="Project ID")
    name: str = Field(..., description="Action name")
    description: Optional[str] = Field(None, description="Action description")
    tags: Optional[List[str]] = Field(None, description="Tags for the action")
    post_to_slack: Optional[bool] = Field(None, description="Whether to post to Slack when this action is triggered")
    slack_message_format: Optional[str] = Field(None, description="Format of the Slack message")
    steps: Optional[List[ActionStep]] = Field(None, description="Steps to define when this action is triggered")
    deleted: Optional[bool] = Field(None, description="Whether this action is deleted")
    pinned_at: Optional[datetime] = Field(None, description="When this action was pinned")

class UpdateActionParams(BaseModel):
    project_id: str = Field(..., description="Project ID")
    action_id: int = Field(..., description="ID of the action to update")
    name: Optional[str] = Field(None, description="Action name")
    description: Optional[str] = Field(None, description="Action description")
    tags: Optional[List[str]] = Field(None, description="Tags for the action")
    post_to_slack: Optional[bool] = Field(None, description="Whether to post to Slack when this action is triggered")
    slack_message_format: Optional[str] = Field(None, description="Format of the Slack message")
    steps: Optional[List[ActionStep]] = Field(None, description="Steps to define when this action is triggered")
    deleted: Optional[bool] = Field(None, description="Whether this action is deleted")
    pinned_at: Optional[datetime] = Field(None, description="When this action was pinned")

class DeleteActionParams(BaseModel):
    project_id: str = Field(..., description="Project ID")
    action_id: int = Field(..., description="ID of the action to delete")

class ActionResponse(BaseModel):
    data: Action
    component: Optional[Dict[str, Any]] = None

class ActionsListResponse(BaseModel):
    data: ActionsList
    component: Optional[Dict[str, Any]] = None

class FeatureFlagFilters(BaseModel):
    groups: Optional[List[Dict[str, Any]]] = None
    multivariate: Optional[Dict[str, Any]] = None
    aggregation_group_type_index: Optional[int] = None
    super_groups: Optional[List[Dict[str, Any]]] = None
    payloads: Optional[Dict[str, Any]] = None

class FeatureFlag(BaseModel):
    id: int
    key: str
    name: Optional[str] = None
    filters: Optional[FeatureFlagFilters] = None
    deleted: Optional[bool] = None
    active: Optional[bool] = None
    created_at: Optional[datetime] = None
    created_by: Optional[User] = None
    is_simple_flag: Optional[bool] = None
    rollout_percentage: Optional[int] = None
    ensure_experience_continuity: Optional[bool] = None
    experiment_set: Optional[List[Any]] = None
    features: Optional[List[Any]] = None
    rollback_conditions: Optional[List[Any]] = None
    performed_rollback: Optional[bool] = None
    can_edit: Optional[bool] = None
    tags: Optional[List[str]] = None

class FeatureFlagsList(BaseModel):
    count: int
    next: Optional[str] = None
    previous: Optional[str] = None
    results: List[FeatureFlag]

class ListFeatureFlagsParams(BaseModel):
    project_id: str = Field(..., description="Project ID")
    limit: Optional[int] = Field(100, ge=1, le=1000, description="Number of results to return per page")
    offset: Optional[int] = Field(0, ge=0, description="The initial index from which to return the results")

class GetFeatureFlagParams(BaseModel):
    project_id: str = Field(..., description="Project ID")
    flag_id: int = Field(..., description="ID of the feature flag to retrieve")

class FeatureFlagParams(BaseModel):
    project_id: str = Field(..., description="Project ID")
    key: str = Field(..., description="Feature flag key (must be unique)")
    name: Optional[str] = Field(None, description="A human-friendly name for the feature flag")
    filters: Optional[Dict[str, Any]] = Field(None, description="Filters defining who sees the flag")
    active: Optional[bool] = Field(True, description="Whether the flag is active")
    rollout_percentage: Optional[int] = Field(None, description="Percentage of users who see the flag (0-100)")
    ensure_experience_continuity: Optional[bool] = Field(None, description="Ensure users keep the same experience")
    tags: Optional[List[str]] = Field(None, description="Tags for the feature flag")

class UpdateFeatureFlagParams(BaseModel):
    project_id: str = Field(..., description="Project ID")
    flag_id: int = Field(..., description="ID of the feature flag to update")
    key: Optional[str] = Field(None, description="Feature flag key (must be unique)")
    name: Optional[str] = Field(None, description="A human-friendly name for the feature flag")
    filters: Optional[Dict[str, Any]] = Field(None, description="Filters defining who sees the flag")
    active: Optional[bool] = Field(None, description="Whether the flag is active")
    rollout_percentage: Optional[int] = Field(None, description="Percentage of users who see the flag (0-100)")
    ensure_experience_continuity: Optional[bool] = Field(None, description="Ensure users keep the same experience")
    tags: Optional[List[str]] = Field(None, description="Tags for the feature flag")

class DeleteFeatureFlagParams(BaseModel):
    project_id: str = Field(..., description="Project ID")
    flag_id: int = Field(..., description="ID of the feature flag to delete")

class FeatureFlagResponse(BaseModel):
    data: FeatureFlag
    component: Optional[Dict[str, Any]] = None

class FeatureFlagsListResponse(BaseModel):
    data: FeatureFlagsList
    component: Optional[Dict[str, Any]] = None

class ApiResponse(BaseModel):
    data: Union[
        QueryResult, 
        QueryStatus, 
        Insight, 
        InsightsList, 
        SuccessResponse, 
        QueryResultResponse, 
        QueryStatusResponse, 
        InsightResponse, 
        InsightsListResponse,
        Dashboard,
        DashboardsList,
        DashboardResponse,
        DashboardsListResponse,
        ValidateKeyResponse,
        Event,
        EventsList,
        EventResponse,
        EventsListResponse,
        Project,
        ProjectsList,
        ProjectResponse,
        ProjectsListResponse,
        Organization,
        OrganizationsList,
        OrganizationResponse,
        OrganizationsListResponse,
        OrganizationMember,
        OrganizationMembersList,
        OrganizationMembersListResponse,
        Person,
        PersonsList,
        PersonResponse,
        PersonsListResponse,
        Action,
        ActionsList,
        ActionResponse,
        ActionsListResponse,
        FeatureFlag,
        FeatureFlagsList,
        FeatureFlagResponse,
        FeatureFlagsListResponse
    ]
    component: Optional[Dict[str, Any]] = None