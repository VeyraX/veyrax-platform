from fastapi import APIRouter, Depends, Body, HTTPException, Request
from typing import Dict, Any
from .service import SentryService
from .schema import (
    TeamListResponse, TeamResponse, UserTeamsResponse,
    ProjectListResponse, ProjectResponse, IssueListResponse, IssueResponse,
    EventListResponse, ReleaseListResponse, ReleaseResponse, 
    AlertRuleListResponse, AlertRuleResponse, UserFeedbackListResponse,
    ServiceHookListResponse, ServiceHookResponse, ListTeamsParams, CreateTeamParams, ListUserTeamsParams,
    ListProjectsParams, CreateProjectParams, ListIssuesParams, GetIssueDetailsParams,
    ListIssueEventsParams, ListReleasesParams, CreateReleaseParams,
    ListAlertRulesParams, CreateAlertRuleParams, ListUserFeedbackParams,
    ListServiceHooksParams, CreateServiceHookParams,
    ApiResponse, DsnResponse, GetDsnParams
)
from ..common.auth import TokenService, TokenRefresherFactory
from ..common.utils import format_validation_error, apply_error_handler_to_service, apply_error_handler_to_router
from .client import SentryClient
from ..common.input_schema_decorator import schema
from pydantic import ValidationError
from ..common.examples_handler import ExamplesLoader

router = APIRouter(prefix="/sentry", tags=["sentry"])

examples = ExamplesLoader()

async def get_sentry_service(request: Request):
    try:
        token_data = await TokenService.get_user_token(request, 'sentry')
        if TokenService.is_token_expired(token_data):
            refresher = TokenRefresherFactory.get_refresher('sentry')
            token_data = await refresher.refresh(request, token_data)
            await TokenService.update_token(request, token_data)
        
        client = SentryClient(token_data['access_token'], token_data.get('raw_token_data',{}).get('org_slug', ""))
        service = SentryService(client)
        apply_error_handler_to_service(service)
        return service
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sentry service initialization failed: {str(e)}")

@router.post("/list_teams", response_model=ApiResponse)
@schema(
    input_schema_class=ListTeamsParams,
    output_schema_class=TeamListResponse,
    examples=examples["/sentry/list_teams"]
)
async def list_teams(
    params: Dict[str, Any] = Body(...),
    service: SentryService = Depends(get_sentry_service)
):
    validated_params = ListTeamsParams(**params)
    return service.list_teams(validated_params.cursor)

@router.post("/create_team", response_model=ApiResponse)
@schema(
    input_schema_class=CreateTeamParams,
    output_schema_class=TeamResponse,
    examples=examples["/sentry/create_team"]
)
async def create_team(
    params: Dict[str, Any] = Body(...),
    service: SentryService = Depends(get_sentry_service)
):
    validated_params = CreateTeamParams(**params)
    return service.create_team(validated_params.name, validated_params.slug)

@router.post("/list_user_teams", response_model=ApiResponse)
@schema(input_schema_class=ListUserTeamsParams, output_schema_class=UserTeamsResponse)
async def list_user_teams(
    params: Dict[str, Any] = Body(...),
    service: SentryService = Depends(get_sentry_service)
):
    validated_params = ListUserTeamsParams(**params)
    return service.list_user_teams(validated_params.cursor)

# Project Management
@router.post("/list_projects", response_model=ApiResponse)
@schema(input_schema_class=ListProjectsParams, output_schema_class=ProjectListResponse)
async def list_projects(
    params: Dict[str, Any] = Body(...),
    service: SentryService = Depends(get_sentry_service)
):
    validated_params = ListProjectsParams(**params)
    return service.list_projects(validated_params.cursor)

@router.post("/create_project", response_model=ApiResponse)
@schema(input_schema_class=CreateProjectParams, output_schema_class=ProjectResponse)
async def create_project(
    params: Dict[str, Any] = Body(...),
    service: SentryService = Depends(get_sentry_service)
):
    validated_params = CreateProjectParams(**params)
    return service.create_project(
        validated_params.team_slug,
        validated_params.name,
        validated_params.slug,
        validated_params.platform
    )

# Issues and Events Management
@router.post("/list_issues", response_model=ApiResponse)
@schema(input_schema_class=ListIssuesParams, output_schema_class=IssueListResponse)
async def list_issues(
    params: Dict[str, Any] = Body(...),
    service: SentryService = Depends(get_sentry_service)
):
    validated_params = ListIssuesParams(**params)
    return service.list_issues(
        validated_params.project_slug,
        validated_params.query,
        validated_params.status,
        validated_params.cursor
    )

@router.post("/get_issue_details", response_model=ApiResponse)
@schema(input_schema_class=GetIssueDetailsParams, output_schema_class=IssueResponse)
async def get_issue_details(
    params: Dict[str, Any] = Body(...),
    service: SentryService = Depends(get_sentry_service)
):
    validated_params = GetIssueDetailsParams(**params)
    return service.get_issue_details(validated_params.issue_id)

@router.post("/list_issue_events", response_model=ApiResponse)
@schema(input_schema_class=ListIssueEventsParams, output_schema_class=EventListResponse)
async def list_issue_events(
    params: Dict[str, Any] = Body(...),
    service: SentryService = Depends(get_sentry_service)
):
    validated_params = ListIssueEventsParams(**params)
    return service.list_issue_events(validated_params.issue_id, validated_params.cursor)

# Releases Management
@router.post("/list_releases", response_model=ApiResponse)
@schema(input_schema_class=ListReleasesParams, output_schema_class=ReleaseListResponse)
async def list_releases(
    params: Dict[str, Any] = Body(...),
    service: SentryService = Depends(get_sentry_service)
):
    validated_params = ListReleasesParams(**params)
    return service.list_releases(validated_params.query, validated_params.cursor)

@router.post("/create_release", response_model=ApiResponse)
@schema(input_schema_class=CreateReleaseParams, output_schema_class=ReleaseResponse)
async def create_release(
    params: Dict[str, Any] = Body(...),
    service: SentryService = Depends(get_sentry_service)
):
    validated_params = CreateReleaseParams(**params)
    return service.create_release(
        validated_params.version,
        validated_params.projects,
        validated_params.ref,
        validated_params.url,
        validated_params.dateReleased
    )

# Alert Rules Management
@router.post("/list_alert_rules", response_model=ApiResponse)
@schema(input_schema_class=ListAlertRulesParams, output_schema_class=AlertRuleListResponse)
async def list_alert_rules(
    params: Dict[str, Any] = Body(...),
    service: SentryService = Depends(get_sentry_service)
):
    validated_params = ListAlertRulesParams(**params)
    return service.list_alert_rules(validated_params.project_slug)

@router.post("/create_alert_rule", response_model=ApiResponse)
@schema(input_schema_class=CreateAlertRuleParams, output_schema_class=AlertRuleResponse)
async def create_alert_rule(
    params: Dict[str, Any] = Body(...),
    service: SentryService = Depends(get_sentry_service)
):
    validated_params = CreateAlertRuleParams(**params)
    return service.create_alert_rule(
        validated_params.project_slug,
        validated_params.name,
        validated_params.conditions,
        validated_params.actions,
        validated_params.actionMatch,
        validated_params.frequency,
        validated_params.environment
    )

# User Feedback Management
@router.post("/list_user_feedback", response_model=ApiResponse)
@schema(input_schema_class=ListUserFeedbackParams, output_schema_class=UserFeedbackListResponse)
async def list_user_feedback(
    params: Dict[str, Any] = Body(...),
    service: SentryService = Depends(get_sentry_service)
):
    validated_params = ListUserFeedbackParams(**params)
    return service.list_user_feedback(validated_params.project_slug, validated_params.cursor)

# Service Hooks Management
@router.post("/list_service_hooks", response_model=ApiResponse)
@schema(
    input_schema_class=ListServiceHooksParams,
    output_schema_class=ServiceHookListResponse,
    examples=examples["/sentry/list_service_hooks"]
)
async def list_service_hooks(
    params: Dict[str, Any] = Body(...),
    service: SentryService = Depends(get_sentry_service)
):
    validated_params = ListServiceHooksParams(**params)
    return service.list_service_hooks(validated_params.project_slug)

@router.post("/create_service_hook", response_model=ApiResponse)
@schema(
    input_schema_class=CreateServiceHookParams,
    output_schema_class=ServiceHookResponse,
    examples=examples["/sentry/create_service_hook"]
)
async def create_service_hook(
    params: Dict[str, Any] = Body(...),
    service: SentryService = Depends(get_sentry_service)
):
    validated_params = CreateServiceHookParams(**params)
    return service.create_service_hook(
        validated_params.project_slug,
        validated_params.url,
        validated_params.events
    )

@router.post("/get_dsn", response_model=ApiResponse)
@schema(
    input_schema_class=GetDsnParams,
    output_schema_class=DsnResponse,
    examples=examples["/sentry/get_dsn"]
)
async def get_dsn(
    params: Dict[str, Any] = Body(...),
    service: SentryService = Depends(get_sentry_service)
):
    validated_params = GetDsnParams(**params)
    return service.get_project_dsn(validated_params.project_slug)

apply_error_handler_to_router(router)

