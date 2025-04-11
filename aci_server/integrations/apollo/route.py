import os
from fastapi import APIRouter, Body, Depends, HTTPException
from starlette.requests import Request as FastAPIRequest
from typing import Dict, Any
from .schema import (
    SearchPersonParams,
    SearchOrganizationParams,
    SearchPeopleViaUrlParams,
    SearchOrganizationsViaUrlParams,
    PersonDetailsParams,
    OrganizationDetailsParams,
    ApiResponse,
    SearchPersonResponse,
    SearchOrganizationResponse,
    PersonDetailResponse,
    OrganizationDetailResponse
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
        #api_key = await validate_provider_api_key(request, "apollo")
        api_key= os.environ.get("RAPID_API_APOLLO_KEY")
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
    input_schema_class=SearchPersonParams,
    output_schema_class=SearchPersonResponse,
    examples=examples["/apollo/search_people"]
)
async def search_people(
    params: Dict[str, Any] = Body(...),
    service: ApolloService = Depends(get_apollo_service)
):
    validated_params = SearchPersonParams(**params)
    return service.search_people(validated_params)

@router.post("/search_organizations", response_model=ApiResponse)
@schema(
    input_schema_class=SearchOrganizationParams,
    output_schema_class=SearchOrganizationResponse,
    examples=examples["/apollo/search_organizations"]
)
async def search_organizations(
    params: Dict[str, Any] = Body(...),
    service: ApolloService = Depends(get_apollo_service)
):
    validated_params = SearchOrganizationParams(**params)
    return service.search_organizations(validated_params)

@router.post("/search_people_via_url", response_model=ApiResponse)
@schema(
    input_schema_class=SearchPeopleViaUrlParams,
    output_schema_class=SearchPersonResponse,
    examples=examples["/apollo/search_people_via_url"]
)
async def search_people_via_url(
    params: Dict[str, Any] = Body(...),
    service: ApolloService = Depends(get_apollo_service)
):
    validated_params = SearchPeopleViaUrlParams(**params)
    return service.search_people_via_url(validated_params)

@router.post("/search_organizations_via_url", response_model=ApiResponse)
@schema(
    input_schema_class=SearchOrganizationsViaUrlParams,
    output_schema_class=SearchOrganizationResponse,
    examples=examples["/apollo/search_organizations_via_url"]
)
async def search_organizations_via_url(
    params: Dict[str, Any] = Body(...),
    service: ApolloService = Depends(get_apollo_service)
):
    validated_params = SearchOrganizationsViaUrlParams(**params)
    return service.search_organizations_via_url(validated_params)

@router.post("/person_details", response_model=ApiResponse)
@schema(
    input_schema_class=PersonDetailsParams,
    output_schema_class=PersonDetailResponse,
    examples=examples["/apollo/person_details"]
)
async def person_details(
    params: Dict[str, Any] = Body(...),
    service: ApolloService = Depends(get_apollo_service)
):
    validated_params = PersonDetailsParams(**params)
    return service.person_details(validated_params)

@router.post("/organization_details", response_model=ApiResponse)
@schema(
    input_schema_class=OrganizationDetailsParams,
    output_schema_class=OrganizationDetailResponse,
    examples=examples.get("/apollo/organization_details", [])
)
async def organization_details(
    params: Dict[str, Any] = Body(...),
    service: ApolloService = Depends(get_apollo_service)
):
    validated_params = OrganizationDetailsParams(**params)
    return service.organization_details(validated_params)

@router.post("/validate_key")
async def validate_key(
    params: Dict[str, Any] = Body(...)
):
    try:
        api_key = params.get("api_key")
        if not api_key:
            return {"valid": False, "message": "API key is required"}
        
        client = ApolloClient(api_key)
        test_params = {"q_person_name": "test", "page": 1}
        client.search_people(test_params)
        return {"valid": True, "message": "API key is valid"}
    except Exception as e:
        return {"valid": False, "message": "Invalid API key"}

apply_error_handler_to_router(router)
