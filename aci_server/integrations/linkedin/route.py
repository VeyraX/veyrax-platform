import os
from fastapi import APIRouter, Body, Depends, HTTPException
from starlette.requests import Request as FastAPIRequest
from typing import Dict, Any
from .schema import (
    GetProfileParams,
    GetMeParams,
    SearchPeopleParams,
    GetProfilePostsParams,
    GetConnectionCountParams,
    GetDataConnectionCountParams,
    GetPostCommentsParams,
    ProfileResponse,
    SearchPeopleResponse,
    GetProfilePostsResponse,
    ConnectionCountResponse,
    DataConnectionCountResponse,
    GetPostCommentsResponse,
    SimilarProfilesParams,
    SimilarProfilesResponse,
    GetCompanyDetailsParams,
    CompanyDetailsResponse,
    SearchCompaniesParams,
    SearchCompaniesEndpointResponse,
    CompanyJobsParams,
    CompanyJobsEndpointResponse,
    GetCompanyPostsParams,
    GetCompanyPostsEndpointResponse,
    GetCompanyPostCommentsParams,
    GetCompanyPostCommentsEndpointResponse,
    SearchPostsParams,
    SearchPostsEndpointResponse,
    GetPostParams,
    GetPostEndpointResponse,
    GetJobDetailsParams,
    GetJobDetailsResponse,
    SearchJobsParams,
    JobSearchEndpointResponse,
    SearchLocationsParams,
    SearchLocationsEndpointResponse,
    ApiResponse
)
from .service import LinkedInService
from .client import LinkedInClient
from ..common.auth import validate_provider_api_key, get_provider_custom_auth
from ..common.input_schema_decorator import schema, input_schema, output_schema
from ..common.utils import apply_error_handler_to_service, apply_error_handler_to_router, format_validation_error, apply_error_handler_to_client
from ..common.examples_handler import ExamplesLoader

router = APIRouter(prefix="/linkedin", tags=["linkedin"])
examples = ExamplesLoader()

async def get_linkedin_service(request: FastAPIRequest):
    try:
        api_key = os.getenv("RAPID_API_LINKEDIN_API_KEY")
        
        # Get custom auth params to retrieve username
        auth_params = await get_provider_custom_auth(request, "linkedin")
        raw_username = auth_params.get("username")
        
        client = LinkedInClient(api_key)
        if raw_username:
            # Use the parser to clean and extract the username
            client.set_username(raw_username)  # set_username internally uses the parser
            
        apply_error_handler_to_client(client)
        service = LinkedInService(client)
        
        apply_error_handler_to_service(service)
        
        return service
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Failed to initialize LinkedIn service: {str(e)}"
        )

@router.post("/get_me", response_model=ApiResponse)
@schema(
    input_schema_class=GetMeParams,
    output_schema_class=ProfileResponse,
    examples=examples["/linkedin/get_me"]
)
async def get_me(
    params: Dict[str, Any] = Body(...),
    service: LinkedInService = Depends(get_linkedin_service)
):
    validated_params = GetMeParams(**params)
    return service.get_me(validated_params)

@router.post("/get_profile", response_model=ApiResponse)
@schema(
    input_schema_class=GetProfileParams,
    output_schema_class=ProfileResponse,
    examples=examples["/linkedin/get_profile"]
)
async def get_profile(
    params: Dict[str, Any] = Body(...),
    service: LinkedInService = Depends(get_linkedin_service)
):
    validated_params = GetProfileParams(**params)
    return service.get_profile(validated_params)

@router.post("/search_people", response_model=ApiResponse)
@schema(
    input_schema_class=SearchPeopleParams,
    output_schema_class=SearchPeopleResponse,
    examples=examples["/linkedin/search_people"]
)
async def search_people(
    params: Dict[str, Any] = Body(...),
    service: LinkedInService = Depends(get_linkedin_service)
):
    validated_params = SearchPeopleParams(**params)
    return service.search_people(validated_params)

@router.post("/get_profile_posts", response_model=ApiResponse)
@schema(
    input_schema_class=GetProfilePostsParams,
    output_schema_class=GetProfilePostsResponse,
    examples=examples["/linkedin/get_profile_posts"]
)
async def get_profile_posts(
    params: Dict[str, Any] = Body(...),
    service: LinkedInService = Depends(get_linkedin_service)
):
    validated_params = GetProfilePostsParams(**params)
    return service.get_profile_posts(validated_params)

@router.post("/get_connection_count", response_model=ApiResponse)
@schema(
    input_schema_class=GetConnectionCountParams,
    output_schema_class=ConnectionCountResponse,
    examples=examples["/linkedin/get_connection_count"]
)
async def get_connection_count(
    params: Dict[str, Any] = Body(...),
    service: LinkedInService = Depends(get_linkedin_service)
):
    validated_params = GetConnectionCountParams(**params)
    return service.get_connection_count(validated_params)

@router.post("/get_post_comments", response_model=ApiResponse)
@schema(
    input_schema_class=GetPostCommentsParams,
    output_schema_class=GetPostCommentsResponse,
    examples=examples["/linkedin/get_post_comments"]
)
async def get_post_comments(
    params: Dict[str, Any] = Body(...),
    service: LinkedInService = Depends(get_linkedin_service)
):
    validated_params = GetPostCommentsParams(**params)
    return service.get_post_comments(validated_params)

@router.post("/similar_profiles", response_model=ApiResponse)
@schema(
    input_schema_class=SimilarProfilesParams,
    output_schema_class=ApiResponse,
    examples=examples["/linkedin/similar_profiles"]
)
async def get_similar_profiles(
    params: Dict[str, Any] = Body(...),
    service: LinkedInService = Depends(get_linkedin_service)
):
    validated_params = SimilarProfilesParams(**params)
    return service.get_similar_profiles(validated_params)

@router.post("/get_company_details", response_model=ApiResponse)
@schema(
    input_schema_class=GetCompanyDetailsParams,
    output_schema_class=CompanyDetailsResponse,
    examples=examples["/linkedin/get_company_details"]
)
async def get_company_details(
    params: Dict[str, Any] = Body(...),
    service: LinkedInService = Depends(get_linkedin_service)
):
    validated_params = GetCompanyDetailsParams(**params)
    return service.get_company_details(validated_params)

@router.post("/search_companies", response_model=ApiResponse)
@schema(
    input_schema_class=SearchCompaniesParams,
    output_schema_class=SearchCompaniesEndpointResponse,
    examples=examples["/linkedin/search_companies"]
)
async def search_companies(
    params: Dict[str, Any] = Body(...),
    service: LinkedInService = Depends(get_linkedin_service)
):
    validated_params = SearchCompaniesParams(**params)
    return service.search_companies(validated_params)

@router.post("/company_jobs", response_model=ApiResponse)
@schema(
    input_schema_class=CompanyJobsParams,
    output_schema_class=CompanyJobsEndpointResponse,
    examples=examples["/linkedin/company_jobs"] 
)
async def get_company_jobs(
    params: Dict[str, Any] = Body(...),
    service: LinkedInService = Depends(get_linkedin_service)
):
    validated_params = CompanyJobsParams(**params)
    return service.get_company_jobs(validated_params)

@router.post("/get_company_posts", response_model=ApiResponse)
@schema(
    input_schema_class=GetCompanyPostsParams,
    output_schema_class=GetCompanyPostsEndpointResponse,
    examples=examples["/linkedin/get_company_posts"] 
)
async def get_company_posts(
    params: Dict[str, Any] = Body(...),
    service: LinkedInService = Depends(get_linkedin_service)
):
    validated_params = GetCompanyPostsParams(**params)
    return service.get_company_posts(validated_params)

@router.post("/get_company_post_comments", response_model=ApiResponse)
@schema(
    input_schema_class=GetCompanyPostCommentsParams,
    output_schema_class=GetCompanyPostCommentsEndpointResponse,
    examples=examples["/linkedin/get_company_post_comments"] 
)
async def get_company_post_comments(
    params: Dict[str, Any] = Body(...),
    service: LinkedInService = Depends(get_linkedin_service)
):
    validated_params = GetCompanyPostCommentsParams(**params)
    return service.get_company_post_comments(validated_params)

@router.post("/search_posts", response_model=ApiResponse)
@schema(
    input_schema_class=SearchPostsParams,
    output_schema_class=SearchPostsEndpointResponse,
    examples=examples["/linkedin/search_posts"] 
)
async def search_posts(
    params: Dict[str, Any] = Body(...),
    service: LinkedInService = Depends(get_linkedin_service)
):
    validated_params = SearchPostsParams(**params)
    return service.search_posts(validated_params)

@router.post("/get_post", response_model=ApiResponse)
@schema(
    input_schema_class=GetPostParams,
    output_schema_class=GetPostEndpointResponse,
    examples=examples["/linkedin/get_post"] 
)
async def get_post(
    params: Dict[str, Any] = Body(...),
    service: LinkedInService = Depends(get_linkedin_service)
):
    validated_params = GetPostParams(**params)
    return service.get_post(validated_params)

@router.post("/get_job_details", response_model=ApiResponse)
@schema(
    input_schema_class=GetJobDetailsParams,
    output_schema_class=GetJobDetailsResponse,
    examples=examples["/linkedin/get_job_details"]
)
async def get_job_details(
    params: Dict[str, Any] = Body(...),
    service: LinkedInService = Depends(get_linkedin_service)
):
    validated_params = GetJobDetailsParams(**params)
    return service.get_job_details(validated_params)

@router.post("/search_jobs", response_model=ApiResponse)
@schema(
    input_schema_class=SearchJobsParams,
    output_schema_class=JobSearchEndpointResponse,
    examples=examples["/linkedin/search_jobs"]
)
async def search_jobs(
    params: Dict[str, Any] = Body(...),
    service: LinkedInService = Depends(get_linkedin_service)
):
    validated_params = SearchJobsParams(**params)
    return service.search_jobs(validated_params)

@router.post("/search_locations", response_model=ApiResponse)
@schema(
    input_schema_class=SearchLocationsParams,
    output_schema_class=SearchLocationsEndpointResponse,
    examples=examples["/linkedin/search_locations"]
)
async def search_locations(
    params: Dict[str, Any] = Body(...),
    service: LinkedInService = Depends(get_linkedin_service)
):
    validated_params = SearchLocationsParams(**params)
    return service.search_locations(validated_params)

@router.post("/validate_key")
async def validate_key(params: Dict[str, Any] = Body(...)):
    try:
        raw_username = params.get("username", "")
        
        # Handle empty username
        if not raw_username:
            return {"valid": False, "message": "LinkedIn username is required"}
        
        # Parse the username using our utility function
        username = LinkedInClient.parse_linkedin_username(raw_username)
        
        # Handle empty username after parsing
        if not username:
            return {"valid": False, "message": "Could not extract a valid LinkedIn username"}
        
        # Validate username format (LinkedIn usernames are typically alphanumeric with hyphens)
        if not all(c.isalnum() or c == '-' for c in username):
            return {"valid": False, "message": "LinkedIn username can only contain letters, numbers, and hyphens"}
        
        # If we have the API key in environment, we could do a more thorough validation
        # by actually checking if the user exists
        api_key = os.getenv("RAPID_API_LINKEDIN_API_KEY")
        if api_key:
            client = LinkedInClient(api_key)
            try:
                # Try to get the user profile to verify the username exists
                result = client.get_profile(username)
                if result and isinstance(result, dict) and result.get('id'):
                    return {"valid": True, "message": f"Username '{username}' is valid"}
                else:
                    return {"valid": False, "message": f"Username '{username}' not found or invalid"}
            except Exception as e:
                return {"valid": False, "message": f"Error validating username '{username}': {str(e)}"}
        
        # If we don't have an API key or couldn't validate, return based on format check
        return {"valid": True, "message": f"Username '{username}' format is valid"}
    except Exception as e:
        return {"valid": False, "message": f"Error validating username: {str(e)}"}

apply_error_handler_to_router(router)
