import os
from fastapi import APIRouter, Body, Depends, HTTPException
from starlette.requests import Request as FastAPIRequest
from typing import Dict, Any
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
    ApiResponse
)
from .service import ApolloService
from .client import ApolloClient
from ..common.auth import validate_provider_api_key
from ..common.input_schema_decorator import schema
from ..common.utils import apply_error_handler_to_service, apply_error_handler_to_router, apply_error_handler_to_client
from ..common.examples_handler import ExamplesLoader

router = APIRouter(prefix="/apollo", tags=["apollo"])
examples = ExamplesLoader()

async def get_apollo_service(request: FastAPIRequest):
    try:
        api_key = os.getenv("RAPID_API_APOLLO_KEY")
        client = ApolloClient(api_key)
        apply_error_handler_to_client(client)
        service = ApolloService(client)
        
        apply_error_handler_to_service(service)
        
        return service
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Failed to initialize Apollo service: {str(e)}"
        )

@router.post("/search_people", response_model=ApiResponse)
@schema(
    input_schema_class=SearchPeopleParams,
    output_schema_class=SearchPeopleResponse,
    examples=examples["/apollo/search_people"]
)
async def search_people(
    params: Dict[str, Any] = Body(...),
    service: ApolloService = Depends(get_apollo_service)
):
    validated_params = SearchPeopleParams(**params)
    return service.search_people(validated_params)

@router.post("/search_people_by_url", response_model=ApiResponse)
@schema(
    input_schema_class=SearchPeopleByUrlParams,
    output_schema_class=SearchPeopleResponse,
    examples=examples["/apollo/search_people_by_url"]
)
async def search_people_by_url(
    params: Dict[str, Any] = Body(...),
    service: ApolloService = Depends(get_apollo_service)
):
    validated_params = SearchPeopleByUrlParams(**params)
    return service.search_people_by_url(validated_params)

@router.post("/search_organizations", response_model=ApiResponse)
@schema(
    input_schema_class=SearchOrganizationsParams,
    output_schema_class=SearchOrganizationsResponse,
    examples=examples["/apollo/search_organizations"]
)
async def search_organizations(
    params: Dict[str, Any] = Body(...),
    service: ApolloService = Depends(get_apollo_service)
):
    validated_params = SearchOrganizationsParams(**params)
    return service.search_organizations(validated_params)

@router.post("/search_organizations_by_url", response_model=ApiResponse)
@schema(
    input_schema_class=SearchOrganizationsByUrlParams,
    output_schema_class=SearchOrganizationsResponse,
    examples=examples["/apollo/search_organizations_by_url"]
)
async def search_organizations_by_url(
    params: Dict[str, Any] = Body(...),
    service: ApolloService = Depends(get_apollo_service)
):
    validated_params = SearchOrganizationsByUrlParams(**params)
    return service.search_organizations_by_url(validated_params)

@router.post("/get_person_details", response_model=ApiResponse)
@schema(
    input_schema_class=GetPersonDetailsParams,
    output_schema_class=PersonDetailsResponse,
    examples=examples["/apollo/get_person_details"]
)
async def get_person_details(
    params: Dict[str, Any] = Body(...),
    service: ApolloService = Depends(get_apollo_service)
):
    validated_params = GetPersonDetailsParams(**params)
    return service.get_person_details(validated_params)

@router.post("/get_organization_details", response_model=ApiResponse)
@schema(
    input_schema_class=GetOrganizationDetailsParams,
    output_schema_class=OrganizationDetailsResponse,
    examples=examples["/apollo/get_organization_details"]
)
async def get_organization_details(
    params: Dict[str, Any] = Body(...),
    service: ApolloService = Depends(get_apollo_service)
):
    validated_params = GetOrganizationDetailsParams(**params)
    return service.get_organization_details(validated_params)

apply_error_handler_to_router(router)
