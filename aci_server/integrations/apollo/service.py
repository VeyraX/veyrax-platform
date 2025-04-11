from typing import Dict, Any, List, Optional
import os
from .client import ApolloClient
from .schema import (
    SearchPersonParams,
    SearchOrganizationParams,
    SearchPeopleViaUrlParams,
    SearchOrganizationsViaUrlParams,
    PersonDetailsParams,
    OrganizationDetailsParams,
    ApiResponse,
    PersonData,
    OrganizationData,
    PersonDetailData,
    OrganizationDetailData,
    SearchPersonResponse,
    SearchOrganizationResponse
)
from ..common.component_handler import load_components, prepare_components_auto

class ApolloService:
    def __init__(self, client: ApolloClient):
        self.client = client
        self.components_data = self._load_components()

    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
    
    def prepare_response(self, data: Any, component_name: str = None) -> ApiResponse:
        tool_name = "apollo"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)

    def search_people(self, params: SearchPersonParams) -> ApiResponse:
        processed_params = self._process_search_params(params)
        response = self.client.search_people(processed_params)
        validated_data = PersonData(**response)
        return self.prepare_response(validated_data, "ApolloPersonCard")
    
    def search_organizations(self, params: SearchOrganizationParams) -> ApiResponse:
        processed_params = self._process_organization_params(params)
        response = self.client.search_organizations(processed_params)
        validated_data = OrganizationData(**response)
        return self.prepare_response(validated_data, "ApolloOrganizationCard")
        
    def search_people_via_url(self, params: SearchPeopleViaUrlParams) -> ApiResponse:
        response = self.client.search_people_via_url(params.apollo_url, params.page)
        validated_data = PersonData(**response)
        return self.prepare_response(validated_data, "ApolloPersonCard")
        
    def search_organizations_via_url(self, params: SearchOrganizationsViaUrlParams) -> ApiResponse:
        response = self.client.search_organizations_via_url(params.apollo_url, params.page)
        validated_data = OrganizationData(**response)
        return self.prepare_response(validated_data, "ApolloOrganizationCard")
        
    def person_details(self, params: PersonDetailsParams) -> ApiResponse:
        response = self.client.person_details(params.person_id)
        validated_data = PersonDetailData(**response)
        return self.prepare_response(validated_data, "ApolloPersonCard")
    
    def organization_details(self, params: OrganizationDetailsParams) -> ApiResponse:
        response = self.client.organization_details(params.organization_id)
        validated_data = OrganizationDetailData(**response)
        return self.prepare_response(validated_data, "ApolloOrganizationCard")

    def _process_search_params(self, params: SearchPersonParams) -> Dict[str, Any]:
        return params.model_dump(exclude_none=True)
        
    def _process_organization_params(self, params: SearchOrganizationParams) -> Dict[str, Any]:
        return params.model_dump(exclude_none=True)
