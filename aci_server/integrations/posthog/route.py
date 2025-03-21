from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query
from starlette.requests import Request as FastAPIRequest
from typing import Dict, Any, Optional, List
from .schema import (
    # Input schema classes
    QueryParams, 
    GetQueryParams,
    DeleteQueryParams,
    InsightParams,
    ListInsightsParams,
    GetInsightParams,
    UpdateInsightParams,
    ValidateKeyParams,
    
    # Output schema classes
    QueryResultResponse,
    QueryStatusResponse,
    InsightResponse,
    InsightsListResponse,
    SuccessResponse,
    ValidateKeyResponse,
    
    # Base model definitions
    ApiResponse,
    Dashboard,
    DashboardsList,
    DashboardParams,
    GetDashboardParams,
    UpdateDashboardParams,
    ListDashboardsParams,
    DashboardResponse,
    DashboardsListResponse,
    Event,
    EventsList,
    ListEventsParams,
    GetEventParams,
    EventResponse,
    EventsListResponse,
    Project,
    ProjectsList,
    ListProjectsParams,
    GetProjectParams,
    ProjectResponse,
    ProjectsListResponse,
    Organization,
    OrganizationsList,
    ListOrganizationsParams,
    GetOrganizationParams,
    OrganizationResponse,
    OrganizationsListResponse,
    OrganizationMember,
    OrganizationMembersList,
    ListOrganizationMembersParams,
    OrganizationMembersListResponse,
    Person,
    PersonsList,
    ListPersonsParams,
    GetPersonParams,
    UpdatePersonParams,
    DeletePersonParams,
    BulkDeletePersonsParams,
    PersonResponse,
    PersonsListResponse,
    ActionStep,
    Action,
    ActionsList,
    ListActionsParams,
    GetActionParams,
    ActionParams,
    UpdateActionParams,
    DeleteActionParams,
    ActionResponse,
    ActionsListResponse,
    FeatureFlagFilters,
    FeatureFlag,
    FeatureFlagsList,
    ListFeatureFlagsParams,
    GetFeatureFlagParams,
    FeatureFlagParams,
    UpdateFeatureFlagParams,
    DeleteFeatureFlagParams,
    FeatureFlagResponse,
    FeatureFlagsListResponse,
)
from .service import PosthogService
from .client import PosthogClient
from ..common.auth import validate_provider_api_key, get_custom_base_url
from ..common.input_schema_decorator import schema
from ..common.utils import apply_error_handler_to_service, apply_error_handler_to_router, apply_error_handler_to_client
from ..common.examples_handler import ExamplesLoader

router = APIRouter(prefix="/posthog", tags=["posthog"])
examples = ExamplesLoader()

async def get_posthog_service(request: FastAPIRequest):
    try:
        api_key = await validate_provider_api_key(request, "posthog")
        base_url = await get_custom_base_url(request, "posthog")
        if not base_url:
            base_url = "https://us.posthog.com"
        
        if not api_key:
            raise HTTPException(status_code=401, detail="PostHog API key is required")
        
        client = PosthogClient(api_key=api_key, base_url=base_url)
        apply_error_handler_to_client(client)
        service = PosthogService(client)
        apply_error_handler_to_service(service)
        return service
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize Posthog service: {str(e)}")

@router.post("/execute_query", response_model=ApiResponse)
@schema(
    input_schema_class=QueryParams,
    output_schema_class=QueryResultResponse,
    examples=examples["/posthog/execute_query"]
)
async def execute_query(
    params: Dict[str, Any] = Body(...),
    service: PosthogService = Depends(get_posthog_service)
):
    validated_params = QueryParams(**params)
    return service.execute_query(validated_params)

@router.post("/get_query", response_model=ApiResponse)
@schema(
    input_schema_class=GetQueryParams,
    output_schema_class=QueryStatusResponse,
    examples=examples["/posthog/get_query"]
)
async def get_query(
    params: Dict[str, Any] = Body(...),
    service: PosthogService = Depends(get_posthog_service)
):
    validated_params = GetQueryParams(**params)
    return service.get_query(validated_params)

@router.post("/delete_query", response_model=SuccessResponse)
@schema(
    input_schema_class=DeleteQueryParams,
    output_schema_class=SuccessResponse
)
async def delete_query(
    params: Dict[str, Any] = Body(...),
    service: PosthogService = Depends(get_posthog_service)
):
    validated_params = DeleteQueryParams(**params)
    service.delete_query(validated_params)
    return SuccessResponse(success=True)

@router.post("/list_insights", response_model=ApiResponse)
@schema(
    input_schema_class=ListInsightsParams,
    output_schema_class=InsightsListResponse,
    examples=examples["/posthog/list_insights"]
)
async def list_insights(
    params: Dict[str, Any] = Body(...),
    service: PosthogService = Depends(get_posthog_service)
):
    validated_params = ListInsightsParams(**params)
    return service.get_insights(validated_params)

@router.post("/create_insight", response_model=ApiResponse)
@schema(
    input_schema_class=InsightParams,
    output_schema_class=InsightResponse,
    examples=examples["/posthog/create_insight"]
)
async def create_insight(
    params: Dict[str, Any] = Body(...),
    service: PosthogService = Depends(get_posthog_service)
):
    validated_params = InsightParams(**params)
    return service.create_insight(validated_params)

@router.post("/get_insight", response_model=ApiResponse)
@schema(
    input_schema_class=GetInsightParams,
    output_schema_class=InsightResponse,
    examples=examples["/posthog/get_insight"]
)
async def get_insight(
    params: Dict[str, Any] = Body(...),
    service: PosthogService = Depends(get_posthog_service)
):
    validated_params = GetInsightParams(**params)
    return service.get_insight(validated_params)

@router.post("/update_insight", response_model=ApiResponse)
@schema(
    input_schema_class=UpdateInsightParams,
    output_schema_class=InsightResponse,
    examples=examples["/posthog/update_insight"]
)
async def update_insight(
    params: Dict[str, Any] = Body(...),
    service: PosthogService = Depends(get_posthog_service)
):
    validated_params = UpdateInsightParams(**params)
    return service.update_insight(validated_params)

@router.post("/list_dashboards", response_model=ApiResponse)
@schema(
    input_schema_class=ListDashboardsParams,
    output_schema_class=DashboardsListResponse,
    examples=examples["/posthog/list_dashboards"]
)
async def list_dashboards(
    params: Dict[str, Any] = Body(...),
    service: PosthogService = Depends(get_posthog_service)
):
    validated_params = ListDashboardsParams(**params)
    return service.get_dashboards(validated_params)

@router.post("/create_dashboard", response_model=ApiResponse)
@schema(
    input_schema_class=DashboardParams,
    output_schema_class=DashboardResponse,
    examples=examples["/posthog/create_dashboard"]
)
async def create_dashboard(
    params: Dict[str, Any] = Body(...),
    service: PosthogService = Depends(get_posthog_service)
):
    validated_params = DashboardParams(**params)
    return service.create_dashboard(validated_params)

@router.post("/get_dashboard", response_model=ApiResponse)
@schema(
    input_schema_class=GetDashboardParams,
    output_schema_class=DashboardResponse,
    examples=examples["/posthog/get_dashboard"]
)
async def get_dashboard(
    params: Dict[str, Any] = Body(...),
    service: PosthogService = Depends(get_posthog_service)
):
    validated_params = GetDashboardParams(**params)
    return service.get_dashboard(validated_params)

@router.post("/update_dashboard", response_model=ApiResponse)
@schema(
    input_schema_class=UpdateDashboardParams,
    output_schema_class=DashboardResponse,
    examples=examples["/posthog/update_dashboard"]
)
async def update_dashboard(
    params: Dict[str, Any] = Body(...),
    service: PosthogService = Depends(get_posthog_service)
):
    validated_params = UpdateDashboardParams(**params)
    return service.update_dashboard(validated_params)

@router.post("/list_events", response_model=ApiResponse)
@schema(
    input_schema_class=ListEventsParams,
    output_schema_class=EventsListResponse,
    examples=examples["/posthog/list_events"]
)
async def list_events(
    params: Dict[str, Any] = Body(...),
    service: PosthogService = Depends(get_posthog_service)
):
    validated_params = ListEventsParams(**params)
    return service.get_events(validated_params)

@router.post("/get_event", response_model=ApiResponse)
@schema(
    input_schema_class=GetEventParams,
    output_schema_class=EventResponse,
    examples=examples["/posthog/get_event"]
)
async def get_event(
    params: Dict[str, Any] = Body(...),
    service: PosthogService = Depends(get_posthog_service)
):
    validated_params = GetEventParams(**params)
    return service.get_event(validated_params)

@router.post("/list_projects", response_model=ApiResponse)
@schema(
    input_schema_class=ListProjectsParams,
    output_schema_class=ProjectsListResponse,
    examples=examples["/posthog/list_projects"]
)
async def list_projects(
    params: Dict[str, Any] = Body(...),
    service: PosthogService = Depends(get_posthog_service)
):
    validated_params = ListProjectsParams(**params)
    return service.get_projects(validated_params)

@router.post("/get_project", response_model=ApiResponse)
@schema(
    input_schema_class=GetProjectParams,
    output_schema_class=ProjectResponse,
    examples=examples["/posthog/get_project"]
)
async def get_project(
    params: Dict[str, Any] = Body(...),
    service: PosthogService = Depends(get_posthog_service)
):
    validated_params = GetProjectParams(**params)
    return service.get_project(validated_params)

@router.post("/list_organizations", response_model=ApiResponse)
@schema(
    input_schema_class=ListOrganizationsParams,
    output_schema_class=OrganizationsListResponse,
    examples=examples["/posthog/list_organizations"]
)
async def list_organizations(
    params: Dict[str, Any] = Body(...),
    service: PosthogService = Depends(get_posthog_service)
):
    validated_params = ListOrganizationsParams(**params)
    return service.get_organizations(validated_params)

@router.post("/get_organization", response_model=ApiResponse)
@schema(
    input_schema_class=GetOrganizationParams,
    output_schema_class=OrganizationResponse,
    examples=examples["/posthog/get_organization"]
)
async def get_organization(
    params: Dict[str, Any] = Body(...),
    service: PosthogService = Depends(get_posthog_service)
):
    validated_params = GetOrganizationParams(**params)
    return service.get_organization(validated_params)

@router.post("/list_organization_members", response_model=ApiResponse)
@schema(
    input_schema_class=ListOrganizationMembersParams,
    output_schema_class=OrganizationMembersListResponse,
    examples=examples["/posthog/list_organization_members"]
)
async def list_organization_members(
    params: Dict[str, Any] = Body(...),
    service: PosthogService = Depends(get_posthog_service)
):
    validated_params = ListOrganizationMembersParams(**params)
    return service.get_organization_members(validated_params)

@router.post("/list_persons", response_model=ApiResponse)
@schema(
    input_schema_class=ListPersonsParams,
    output_schema_class=PersonsListResponse,
    examples=examples["/posthog/list_persons"]
)
async def list_persons(
    params: Dict[str, Any] = Body(...),
    service: PosthogService = Depends(get_posthog_service)
):
    validated_params = ListPersonsParams(**params)
    return service.get_persons(validated_params)

@router.post("/get_person", response_model=ApiResponse)
@schema(
    input_schema_class=GetPersonParams,
    output_schema_class=PersonResponse,
    examples=examples["/posthog/get_person"]
)
async def get_person(
    params: Dict[str, Any] = Body(...),
    service: PosthogService = Depends(get_posthog_service)
):
    validated_params = GetPersonParams(**params)
    return service.get_person(validated_params)

@router.post("/update_person", response_model=ApiResponse)
@schema(
    input_schema_class=UpdatePersonParams,
    output_schema_class=PersonResponse,
    examples=examples["/posthog/update_person"]
)
async def update_person(
    params: Dict[str, Any] = Body(...),
    service: PosthogService = Depends(get_posthog_service)
):
    validated_params = UpdatePersonParams(**params)
    return service.update_person(validated_params)

@router.post("/delete_person", response_model=SuccessResponse)
@schema(
    input_schema_class=DeletePersonParams,
    output_schema_class=SuccessResponse,
    examples=examples["/posthog/delete_person"]
)
async def delete_person(
    params: Dict[str, Any] = Body(...),
    service: PosthogService = Depends(get_posthog_service)
):
    validated_params = DeletePersonParams(**params)
    return service.delete_person(validated_params)

@router.post("/bulk_delete_persons", response_model=SuccessResponse)
@schema(
    input_schema_class=BulkDeletePersonsParams,
    output_schema_class=SuccessResponse,
    examples=examples["/posthog/bulk_delete_persons"]
)
async def bulk_delete_persons(
    params: Dict[str, Any] = Body(...),
    service: PosthogService = Depends(get_posthog_service)
):
    validated_params = BulkDeletePersonsParams(**params)
    return service.bulk_delete_persons(validated_params)

@router.post("/list_actions", response_model=ApiResponse)
@schema(
    input_schema_class=ListActionsParams,
    output_schema_class=ActionsListResponse,
    examples=examples["/posthog/list_actions"]
)
async def list_actions(
    params: Dict[str, Any] = Body(...),
    service: PosthogService = Depends(get_posthog_service)
):
    validated_params = ListActionsParams(**params)
    return service.get_actions(validated_params)

@router.post("/create_action", response_model=ApiResponse)
@schema(
    input_schema_class=ActionParams,
    output_schema_class=ActionResponse,
    examples=examples["/posthog/create_action"]
)
async def create_action(
    params: Dict[str, Any] = Body(...),
    service: PosthogService = Depends(get_posthog_service)
):
    validated_params = ActionParams(**params)
    return service.create_action(validated_params)

@router.post("/get_action", response_model=ApiResponse)
@schema(
    input_schema_class=GetActionParams,
    output_schema_class=ActionResponse,
    examples=examples["/posthog/get_action"]
)
async def get_action(
    params: Dict[str, Any] = Body(...),
    service: PosthogService = Depends(get_posthog_service)
):
    validated_params = GetActionParams(**params)
    return service.get_action(validated_params)

@router.post("/update_action", response_model=ApiResponse)
@schema(
    input_schema_class=UpdateActionParams,
    output_schema_class=ActionResponse,
    examples=examples["/posthog/update_action"]
)
async def update_action(
    params: Dict[str, Any] = Body(...),
    service: PosthogService = Depends(get_posthog_service)
):
    validated_params = UpdateActionParams(**params)
    return service.update_action(validated_params)

@router.post("/delete_action", response_model=SuccessResponse)
@schema(
    input_schema_class=DeleteActionParams,
    output_schema_class=SuccessResponse,
    examples=examples["/posthog/delete_action"]
)
async def delete_action(
    params: Dict[str, Any] = Body(...),
    service: PosthogService = Depends(get_posthog_service)
):
    validated_params = DeleteActionParams(**params)
    return service.delete_action(validated_params)

@router.post("/list_feature_flags", response_model=ApiResponse)
@schema(
    input_schema_class=ListFeatureFlagsParams,
    output_schema_class=FeatureFlagsListResponse,
    examples=examples["/posthog/list_feature_flags"]
)
async def list_feature_flags(
    params: Dict[str, Any] = Body(...),
    service: PosthogService = Depends(get_posthog_service)
):
    validated_params = ListFeatureFlagsParams(**params)
    return service.get_feature_flags(validated_params)

@router.post("/create_feature_flag", response_model=ApiResponse)
@schema(
    input_schema_class=FeatureFlagParams,
    output_schema_class=FeatureFlagResponse,
    examples=examples["/posthog/create_feature_flag"]
)
async def create_feature_flag(
    params: Dict[str, Any] = Body(...),
    service: PosthogService = Depends(get_posthog_service)
):
    validated_params = FeatureFlagParams(**params)
    return service.create_feature_flag(validated_params)

@router.post("/get_feature_flag", response_model=ApiResponse)
@schema(
    input_schema_class=GetFeatureFlagParams,
    output_schema_class=FeatureFlagResponse,
    examples=examples["/posthog/get_feature_flag"]
)
async def get_feature_flag(
    params: Dict[str, Any] = Body(...),
    service: PosthogService = Depends(get_posthog_service)
):
    validated_params = GetFeatureFlagParams(**params)
    return service.get_feature_flag(validated_params)

@router.post("/update_feature_flag", response_model=ApiResponse)
@schema(
    input_schema_class=UpdateFeatureFlagParams,
    output_schema_class=FeatureFlagResponse,
    examples=examples["/posthog/update_feature_flag"]
)
async def update_feature_flag(
    params: Dict[str, Any] = Body(...),
    service: PosthogService = Depends(get_posthog_service)
):
    validated_params = UpdateFeatureFlagParams(**params)
    return service.update_feature_flag(validated_params)

@router.post("/delete_feature_flag", response_model=SuccessResponse)
@schema(
    input_schema_class=DeleteFeatureFlagParams,
    output_schema_class=SuccessResponse,
    examples=examples["/posthog/delete_feature_flag"]
)
async def delete_feature_flag(
    params: Dict[str, Any] = Body(...),
    service: PosthogService = Depends(get_posthog_service)
):
    validated_params = DeleteFeatureFlagParams(**params)
    return service.delete_feature_flag(validated_params)

@router.post("/validate_key")
async def validate_key(
    params: Dict[str, Any] = Body(...),
):
    try:
        api_key = params.get("api_key")
        base_url = params.get("base_url", "https://us.posthog.com")
        
        if not api_key:
            return ValidateKeyResponse(valid=False, message="API key is required")
        
        client = PosthogClient(api_key=api_key, base_url=base_url)
        
        try:
            client.get_organizations()
            return ValidateKeyResponse(valid=True, message="API key is valid")
        except Exception as e:
            return ValidateKeyResponse(valid=False, message=f"Invalid API key: {str(e)}")
    except Exception as e:
        return ValidateKeyResponse(valid=False, message=f"Error validating API key: {str(e)}")

apply_error_handler_to_router(router)
