import os
from typing import Dict, Any, Optional, List, Union
from .client import PosthogClient
from .schema import (
    QueryParams, 
    GetQueryParams, 
    DeleteQueryParams, 
    QueryResult, 
    QueryStatus,
    Insight,
    InsightsList,
    InsightParams,
    ListInsightsParams,
    GetInsightParams,
    UpdateInsightParams,
    ApiResponse,
    Dashboard,
    DashboardsList,
    DashboardParams,
    GetDashboardParams,
    ListDashboardsParams,
    UpdateDashboardParams,
    Event,
    EventsList,
    ListEventsParams,
    GetEventParams,
    Project,
    ProjectsList,
    ListProjectsParams,
    GetProjectParams,
    Organization,
    OrganizationsList,
    ListOrganizationsParams,
    GetOrganizationParams,
    OrganizationMember,
    OrganizationMembersList,
    ListOrganizationMembersParams,
    Person,
    PersonsList,
    ListPersonsParams,
    GetPersonParams,
    UpdatePersonParams,
    DeletePersonParams,
    BulkDeletePersonsParams,
    SuccessResponse,
    Action,
    ActionsList,
    ListActionsParams,
    GetActionParams,
    ActionParams,
    UpdateActionParams,
    DeleteActionParams,
    FeatureFlagFilters,
    FeatureFlag,
    FeatureFlagsList,
    ListFeatureFlagsParams,
    GetFeatureFlagParams,
    FeatureFlagParams,
    UpdateFeatureFlagParams,
    DeleteFeatureFlagParams,
    FeatureFlagResponse,
    FeatureFlagsListResponse
)
from ..common.component_handler import load_components, prepare_components_auto

class PosthogService:
    def __init__(self, client: PosthogClient):
        self.client = client
        self.components_data = self._load_components()
    
    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
    
    def prepare_response(self, data: Any, component_name: str = None) -> ApiResponse:
        tool_name = "posthog"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)
    
    def execute_query(self, params: QueryParams) -> ApiResponse:
        project_id = params.project_id
        
        query_payload = {
            "query": params.query.model_dump(),
        }
        
        if params.async_query:
            query_payload["async"] = params.async_query
        if params.client_query_id:
            query_payload["client_query_id"] = params.client_query_id
        if params.refresh:
            query_payload["refresh"] = params.refresh
        if params.filters_override:
            query_payload["filters_override"] = params.filters_override
        if params.variables_override:
            query_payload["variables_override"] = params.variables_override
        
        response = self.client.execute_query(project_id, query_payload)
        
        if response is None:
            return self.prepare_response({"error": "Failed to execute query. No response from PostHog API."}, "Error")
        
        if "query_status" in response and response.get("query_status") and response["query_status"].get("complete") is False:
            query_status = QueryStatus(**response["query_status"])
            return self.prepare_response(query_status, "QueryStatus")
        
        result = QueryResult(**response)
        return self.prepare_response(result, "QueryResult")
    
    def get_query(self, params: GetQueryParams) -> ApiResponse:
        response = self.client.get_query(params.project_id, params.query_id)
        query_status = QueryStatus(**response["query_status"])
        return self.prepare_response(query_status, "QueryStatus")
    
    def delete_query(self, params: DeleteQueryParams) -> None:
        return self.client.delete_query(params.project_id, params.query_id)
    
    def get_insights(self, params: ListInsightsParams) -> ApiResponse:
        project_id = params.project_id
        query_params = params.model_dump(exclude={"project_id"}, exclude_none=True)
        response = self.client.get_insights(project_id, query_params)
        insights_list = InsightsList(**response)
        return self.prepare_response(insights_list, "InsightsList")
    
    def create_insight(self, params: InsightParams) -> ApiResponse:
        project_id = params.project_id
        data = params.model_dump(exclude={"project_id"}, exclude_none=True)
        response = self.client.create_insight(project_id, data)
        insight = Insight(**response)
        return self.prepare_response(insight, "Insight")
    
    def get_insight(self, params: GetInsightParams) -> ApiResponse:
        project_id = params.project_id
        insight_id = params.insight_id
        query_params = {}
        if params.from_dashboard is not None:
            query_params["from_dashboard"] = params.from_dashboard
        if params.refresh:
            query_params["refresh"] = params.refresh
            
        response = self.client.get_insight(project_id, insight_id, query_params)
        insight = Insight(**response)
        return self.prepare_response(insight, "Insight")
    
    def update_insight(self, params: UpdateInsightParams) -> ApiResponse:
        project_id = params.project_id
        insight_id = params.insight_id
        data = params.model_dump(exclude={"project_id", "insight_id"}, exclude_none=True)
        response = self.client.update_insight(project_id, insight_id, data)
        insight = Insight(**response)
        return self.prepare_response(insight, "Insight")
    
    def get_dashboards(self, params: ListDashboardsParams) -> ApiResponse:
        project_id = params.project_id
        query_params = params.model_dump(exclude={"project_id"}, exclude_none=True)
        response = self.client.get_dashboards(project_id, query_params)
        dashboards_list = DashboardsList(**response)
        return self.prepare_response(dashboards_list, "DashboardsList")
    
    def create_dashboard(self, params: DashboardParams) -> ApiResponse:
        project_id = params.project_id
        data = params.model_dump(exclude={"project_id"}, exclude_none=True)
        response = self.client.create_dashboard(project_id, data)
        dashboard = Dashboard(**response)
        return self.prepare_response(dashboard, "Dashboard")
    
    def get_dashboard(self, params: GetDashboardParams) -> ApiResponse:
        project_id = params.project_id
        response = self.client.get_dashboard(project_id, params.dashboard_id)
        dashboard = Dashboard(**response)
        return self.prepare_response(dashboard, "Dashboard")
    
    def update_dashboard(self, params: UpdateDashboardParams) -> ApiResponse:
        project_id = params.project_id
        dashboard_id = params.dashboard_id
        data = params.model_dump(exclude={"project_id", "dashboard_id"}, exclude_none=True)
        response = self.client.update_dashboard(project_id, dashboard_id, data)
        dashboard = Dashboard(**response)
        return self.prepare_response(dashboard, "Dashboard")

    def get_events(self, params: ListEventsParams) -> ApiResponse:
        project_id = params.project_id
        query_params = params.model_dump(exclude={"project_id"}, exclude_none=True)
        response = self.client.get_events(project_id, query_params)
        events_list = EventsList(**response)
        return self.prepare_response(events_list, "EventsList")

    def get_event(self, params: GetEventParams) -> ApiResponse:
        project_id = params.project_id
        event_id = params.event_id
        query_params = {}
        if params.format:
            query_params["format"] = params.format
        
        response = self.client.get_event(project_id, event_id, query_params)
        event = Event(**response)
        return self.prepare_response(event, "Event")

    def get_projects(self, params: ListProjectsParams) -> ApiResponse:
        """Retrieve a list of projects in the specified organization"""
        organization_id = params.organization_id
        query_params = params.model_dump(exclude={"organization_id"}, exclude_none=True)
        response = self.client.get_projects(organization_id, query_params)
        projects_list = ProjectsList(**response)
        return self.prepare_response(projects_list, "ProjectsList")

    def get_project(self, params: GetProjectParams) -> ApiResponse:
        """Retrieve a specific project by ID"""
        response = self.client.get_project(params.organization_id, params.project_id)
        project = Project(**response)
        return self.prepare_response(project, "Project")

    def get_organizations(self, params: ListOrganizationsParams) -> ApiResponse:
        """Retrieve a list of organizations"""
        query_params = params.model_dump(exclude_none=True)
        response = self.client.get_organizations(query_params)
        organizations_list = OrganizationsList(**response)
        return self.prepare_response(organizations_list, "OrganizationsList")

    def get_organization(self, params: GetOrganizationParams) -> ApiResponse:
        """Retrieve a specific organization by ID"""
        response = self.client.get_organization(params.organization_id)
        organization = Organization(**response)
        return self.prepare_response(organization, "Organization")

    def get_organization_members(self, params: ListOrganizationMembersParams) -> ApiResponse:
        """Retrieve a list of members in the specified organization"""
        organization_id = params.organization_id
        query_params = params.model_dump(exclude={"organization_id"}, exclude_none=True)
        response = self.client.get_organization_members(organization_id, query_params)
        members_list = OrganizationMembersList(**response)
        return self.prepare_response(members_list, "OrganizationMembersList")

    def get_persons(self, params: ListPersonsParams) -> ApiResponse:
        """Retrieve a paginated list of persons"""
        project_id = params.project_id
        query_params = params.model_dump(exclude={"project_id"}, exclude_none=True)
        response = self.client.get_persons(project_id, query_params)
        persons_list = PersonsList(**response)
        return self.prepare_response(persons_list, "PersonsList")

    def get_person(self, params: GetPersonParams) -> ApiResponse:
        """Retrieve a specific person by ID"""
        project_id = params.project_id
        person_id = params.person_id
        query_params = {}
        if params.format:
            query_params["format"] = params.format
        
        response = self.client.get_person(project_id, person_id, query_params)
        person = Person(**response)
        return self.prepare_response(person, "Person")

    def update_person(self, params: UpdatePersonParams) -> ApiResponse:
        """Update a person's properties"""
        project_id = params.project_id
        person_id = params.person_id
        data = {"properties": params.properties}
        
        response = self.client.update_person(project_id, person_id, data)
        if isinstance(response, dict) and response.get("detail") == "Person not found":
            return self.prepare_response({"error": "Person not found"}, "Error")
        person = Person(**response)
        return self.prepare_response(person, "Person")

    def delete_person(self, params: DeletePersonParams) -> SuccessResponse:
        """Delete a person and optionally their events"""
        project_id = params.project_id
        self.client.delete_person(project_id, params.person_id, params.delete_events)
        return SuccessResponse(success=True)

    def bulk_delete_persons(self, params: BulkDeletePersonsParams) -> SuccessResponse:
        """Bulk delete persons by IDs or distinct_ids"""
        project_id = params.project_id
        data = {}
        if params.ids:
            data["ids"] = params.ids
        if params.distinct_ids:
            data["distinct_ids"] = params.distinct_ids
        
        self.client.bulk_delete_persons(project_id, data, params.delete_events)
        return SuccessResponse(success=True)

    def get_actions(self, params: ListActionsParams) -> ApiResponse:
        """Retrieve a paginated list of actions"""
        project_id = params.project_id
        query_params = params.model_dump(exclude={"project_id"}, exclude_none=True)
        response = self.client.get_actions(project_id, query_params)
        actions_list = ActionsList(**response)
        return self.prepare_response(actions_list, "ActionsList")

    def create_action(self, params: ActionParams) -> ApiResponse:
        """Create a new action"""
        project_id = params.project_id
        data = params.model_dump(exclude={"project_id"}, exclude_none=True)
        response = self.client.create_action(project_id, data)
        action = Action(**response)
        return self.prepare_response(action, "Action")

    def get_action(self, params: GetActionParams) -> ApiResponse:
        """Retrieve a specific action by ID"""
        project_id = params.project_id
        action_id = params.action_id
        query_params = {}
        if params.format:
            query_params["format"] = params.format
        
        response = self.client.get_action(project_id, action_id, query_params)
        action = Action(**response)
        return self.prepare_response(action, "Action")

    def update_action(self, params: UpdateActionParams) -> ApiResponse:
        """Update an action's properties"""
        project_id = params.project_id
        action_id = params.action_id
        data = params.model_dump(exclude={"project_id", "action_id"}, exclude_none=True)
        
        response = self.client.update_action(project_id, action_id, data)
        action = Action(**response)
        return self.prepare_response(action, "Action")

    def delete_action(self, params: DeleteActionParams) -> SuccessResponse:
        """Delete an action (set it as deleted)"""
        project_id = params.project_id
        action_id = params.action_id
        result = self.client.delete_action(project_id, action_id)
        return SuccessResponse(success=result.get("success", True))

    def get_feature_flags(self, params: ListFeatureFlagsParams) -> ApiResponse:
        """Retrieve a paginated list of feature flags"""
        project_id = params.project_id
        query_params = params.model_dump(exclude={"project_id"}, exclude_none=True)
        response = self.client.get_feature_flags(project_id, query_params)
        flags_list = FeatureFlagsList(**response)
        return self.prepare_response(flags_list, "FeatureFlagsList")

    def create_feature_flag(self, params: FeatureFlagParams) -> ApiResponse:
        """Create a new feature flag"""
        project_id = params.project_id
        data = params.model_dump(exclude={"project_id"}, exclude_none=True)
        
        if params.rollout_percentage is not None and params.filters is None:
            data["filters"] = {
                "groups": [
                    {
                        "rollout_percentage": params.rollout_percentage
                    }
                ]
            }
            if "rollout_percentage" in data:
                del data["rollout_percentage"]
        
        response = self.client.create_feature_flag(project_id, data)
        flag = FeatureFlag(**response)
        return self.prepare_response(flag, "FeatureFlag")

    def get_feature_flag(self, params: GetFeatureFlagParams) -> ApiResponse:
        """Retrieve a specific feature flag by ID"""
        project_id = params.project_id
        response = self.client.get_feature_flag(project_id, params.flag_id)
        flag = FeatureFlag(**response)
        return self.prepare_response(flag, "FeatureFlag")

    def update_feature_flag(self, params: UpdateFeatureFlagParams) -> ApiResponse:
        """Update a feature flag"""
        project_id = params.project_id
        flag_id = params.flag_id
        data = params.model_dump(exclude={"project_id", "flag_id"}, exclude_none=True)
        
        if params.rollout_percentage is not None:
            if "filters" not in data:
                data["filters"] = {"groups": [{"rollout_percentage": params.rollout_percentage}]}
            if "rollout_percentage" in data:
                del data["rollout_percentage"]
        
        response = self.client.update_feature_flag(project_id, flag_id, data)
        flag = FeatureFlag(**response)
        return self.prepare_response(flag, "FeatureFlag")

    def delete_feature_flag(self, params: DeleteFeatureFlagParams) -> SuccessResponse:
        """Delete a feature flag"""
        project_id = params.project_id
        self.client.delete_feature_flag(project_id, params.flag_id)
        return SuccessResponse(success=True)
