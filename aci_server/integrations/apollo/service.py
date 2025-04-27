from typing import Dict, Any
import os
from .client import ApolloClient
from .schema import (
    SearchPeopleParams,
    SearchPeopleByUrlParams,
    SearchOrganizationsParams,
    SearchOrganizationsByUrlParams,
    GetPersonDetailsParams,
    GetOrganizationDetailsParams,
    SearchPeopleResponse,
    SearchOrganizationsResponse,
    PersonDetailsResponse,
    OrganizationDetailsResponse,
    ApiResponse,
    PeopleList,
    OrganizationsList,
    PersonDetails,
    OrganizationDetails
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

    def search_people(self, params: SearchPeopleParams) -> ApiResponse:
        processed_params = self._process_search_people_params(params)
        response = self.client.search_people(processed_params)
        
        raw_data = response.get("data")
        
        # Provide defaults if data is missing or not a dict, or keys are missing
        people_data = []
        pagination_data = {}
        
        if isinstance(raw_data, dict):
            people_data = raw_data.get("people", [])
            pagination_data = raw_data.get("pagination", {})
            # Ensure people_data is actually a list, default to empty if not
            if not isinstance(people_data, list):
                people_data = []
            # Ensure pagination_data is actually a dict, default to empty if not
            if not isinstance(pagination_data, dict):
                pagination_data = {}
                
        people_list = PeopleList(
            people=people_data,
            pagination=pagination_data
        )
        return self.prepare_response(people_list, "ApolloPeopleList")
        
    def search_people_by_url(self, params: SearchPeopleByUrlParams) -> ApiResponse:
        processed_params = params.model_dump(exclude_none=True)
        response = self.client.search_people_by_url(processed_params)
        people_list = PeopleList(**response["data"])
        return self.prepare_response(people_list, "ApolloPeopleList")
        
    def search_organizations(self, params: SearchOrganizationsParams) -> ApiResponse:
        processed_params = params.model_dump(exclude_none=True)
        response = self.client.search_organizations(processed_params)
        orgs_list = OrganizationsList(**response["data"])
        return self.prepare_response(orgs_list, "ApolloOrganizationsList")
        
    def search_organizations_by_url(self, params: SearchOrganizationsByUrlParams) -> ApiResponse:
        processed_params = params.model_dump(exclude_none=True)
        response = self.client.search_organizations_by_url(processed_params)
        orgs_list = OrganizationsList(**response["data"])
        return self.prepare_response(orgs_list, "ApolloOrganizationsList")
        
    def get_person_details(self, params: GetPersonDetailsParams) -> ApiResponse:
        processed_params = params.model_dump(exclude_none=True)
        response = self.client.get_person_details(processed_params)
        person_details = PersonDetails(person=response["data"])
        return self.prepare_response(person_details, "ApolloPersonDetails")
        
    def get_organization_details(self, params: GetOrganizationDetailsParams) -> ApiResponse:
        processed_params = params.model_dump(exclude_none=True)
        response = self.client.get_organization_details(processed_params)
        org_details = OrganizationDetails(organization=response["data"])
        return self.prepare_response(org_details, "ApolloOrganizationDetails")

    def _process_search_people_params(self, params: SearchPeopleParams) -> Dict[str, Any]:
        return params.model_dump(exclude_none=True)
