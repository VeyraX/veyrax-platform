from fastapi import APIRouter, Depends, Body, Request, HTTPException
from typing import Dict, Any
from .service import LinkedInService
from .client import LinkedInClient
from .schema import (
    ApiResponse,
    GetProfileParams,
    SearchPeopleParams,
    GetProfilePostsParams,
    GetProfilePostCommentsParams,
    GetConnectionCountParams,
    GetDataConnectionCountParams,
    GetCompanyDetailsParams,
    SearchCompaniesParams,
    CompanyJobsParams,
    GetCompanyPostsParams,
    GetProfileEmailParams,
    GetCompanyEmployeesCountParams,
    SearchJobsParams,
    GetJobDetailsParams,
    GetHiringTeamParams,
    SearchPostsParams,
    GetPostParams,
    GetArticleParams,
    GetArticleCommentsParams,
    SearchLocationsParams
)
from ..common.auth import validate_provider_api_key
from ..common.input_schema_decorator import schema
from ..common.utils import apply_error_handler_to_service, apply_error_handler_to_router, apply_error_handler_to_client
from ..common.examples_handler import ExamplesLoader
import os

router = APIRouter(prefix="/linkedin", tags=["linkedin"])
examples = ExamplesLoader()

async def get_linkedin_service(request: Request):
    try:
        api_key = os.environ.get("RAPID_API_LINKEDIN_API_KEY")
        client = LinkedInClient(api_key)
        service = LinkedInService(client)
        apply_error_handler_to_client(client)
        apply_error_handler_to_service(service)
        return service
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LinkedIn service initialization failed: {str(e)}")


@router.post("/get_profile", response_model=ApiResponse)
@schema(
    input_schema_class=GetProfileParams,
    output_schema_class=ApiResponse,
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
    output_schema_class=ApiResponse,
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
    output_schema_class=ApiResponse,
    examples=examples["/linkedin/get_profile_posts"]
)
async def get_profile_posts(
    params: Dict[str, Any] = Body(...),
    service: LinkedInService = Depends(get_linkedin_service)
):
    print("[get_profile_posts] params", params)
    validated_params = GetProfilePostsParams(**params)
    return service.get_profile_posts(validated_params)

@router.post("/get_profile_post_comments", response_model=ApiResponse)
@schema(
    input_schema_class=GetProfilePostCommentsParams,
    output_schema_class=ApiResponse,
    examples=examples["/linkedin/get_profile_post_comments"]
)
async def get_profile_post_comments(
    params: Dict[str, Any] = Body(...),
    service: LinkedInService = Depends(get_linkedin_service)
):
    validated_params = GetProfilePostCommentsParams(**params)
    return service.get_profile_post_comments(validated_params)

@router.post("/get_connection_count", response_model=ApiResponse)
@schema(
    input_schema_class=GetConnectionCountParams,
    output_schema_class=ApiResponse,
    examples=examples["/linkedin/get_connection_count"]
)
async def get_connection_count(
    params: Dict[str, Any] = Body(...),
    service: LinkedInService = Depends(get_linkedin_service)
):
    validated_params = GetConnectionCountParams(**params)
    return service.get_connection_count(validated_params)

@router.post("/get_data_connection_count", response_model=ApiResponse)
@schema(
    input_schema_class=GetDataConnectionCountParams,
    output_schema_class=ApiResponse,
    examples=examples["/linkedin/get_data_connection_count"]
)
async def get_data_connection_count(
    params: Dict[str, Any] = Body(...),
    service: LinkedInService = Depends(get_linkedin_service)
):
    validated_params = GetDataConnectionCountParams(**params)
    return service.get_data_connection_count(validated_params)

@router.post("/get_company_details", response_model=ApiResponse)
@schema(
    input_schema_class=GetCompanyDetailsParams,
    output_schema_class=ApiResponse,
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
    output_schema_class=ApiResponse,
    examples=examples["/linkedin/search_companies"]
)
async def search_companies(
    params: Dict[str, Any] = Body(...),
    service: LinkedInService = Depends(get_linkedin_service)
):
    validated_params = SearchCompaniesParams(**params)
    return service.search_companies(validated_params)

@router.post("/company-jobs", response_model=ApiResponse)
@schema(
    input_schema_class=CompanyJobsParams,
    output_schema_class=ApiResponse,
    examples=examples["/linkedin/company-jobs"]
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
    output_schema_class=ApiResponse,
    examples=examples["/linkedin/get_company_posts"]
)
async def get_company_posts(
    params: Dict[str, Any] = Body(...),
    service: LinkedInService = Depends(get_linkedin_service)
):
    validated_params = GetCompanyPostsParams(**params)
    return service.get_company_posts(validated_params)

@router.post("/linkedin-to-email", response_model=ApiResponse)
@schema(
    input_schema_class=GetProfileEmailParams,
    output_schema_class=ApiResponse,
    examples=examples["/linkedin/linkedin-to-email"]
)
async def get_profile_email(
    params: Dict[str, Any] = Body(...),
    service: LinkedInService = Depends(get_linkedin_service)
):
    validated_params = GetProfileEmailParams(**params)
    return service.get_profile_email(validated_params)

@router.post("/get-company-employees-count", response_model=ApiResponse)
@schema(
    input_schema_class=GetCompanyEmployeesCountParams,
    output_schema_class=ApiResponse,
    examples=examples["/linkedin/get-company-employees-count"]
)
async def get_company_employees_count(
    params: Dict[str, Any] = Body(...),
    service: LinkedInService = Depends(get_linkedin_service)
):
    validated_params = GetCompanyEmployeesCountParams(**params)
    return service.get_company_employees_count(validated_params)

@router.post("/search-jobs", response_model=ApiResponse)
@schema(
    input_schema_class=SearchJobsParams,
    output_schema_class=ApiResponse,
    examples=examples["/linkedin/search-jobs"]
)
async def search_jobs(
    params: Dict[str, Any] = Body(...),
    service: LinkedInService = Depends(get_linkedin_service)
):
    validated_params = SearchJobsParams(**params)
    return service.search_jobs(validated_params)

@router.post("/get-job-details", response_model=ApiResponse)
@schema(
    input_schema_class=GetJobDetailsParams,
    output_schema_class=ApiResponse,
    examples=examples["/linkedin/get-job-details"]
)
async def get_job_details(
    params: Dict[str, Any] = Body(...),
    service: LinkedInService = Depends(get_linkedin_service)
):
    validated_params = GetJobDetailsParams(**params)
    return service.get_job_details(validated_params)

@router.post("/get-hiring-team", response_model=ApiResponse)
@schema(
    input_schema_class=GetHiringTeamParams,
    output_schema_class=ApiResponse,
    examples=examples["/linkedin/get-hiring-team"]
)
async def get_hiring_team(
    params: Dict[str, Any] = Body(...),
    service: LinkedInService = Depends(get_linkedin_service)
):
    validated_params = GetHiringTeamParams(**params)
    return service.get_hiring_team(validated_params)

@router.post("/search-posts", response_model=ApiResponse)
@schema(
    input_schema_class=SearchPostsParams,
    output_schema_class=ApiResponse,
    examples=examples["/linkedin/search-posts"]
)
async def search_posts(
    params: Dict[str, Any] = Body(...),
    service: LinkedInService = Depends(get_linkedin_service)
):
    validated_params = SearchPostsParams(**params)
    return service.search_posts(validated_params)

@router.post("/get-post", response_model=ApiResponse)
@schema(
    input_schema_class=GetPostParams,
    output_schema_class=ApiResponse,
    examples=examples["/linkedin/get-post"]
)
async def get_post(
    params: Dict[str, Any] = Body(...),
    service: LinkedInService = Depends(get_linkedin_service)
):
    validated_params = GetPostParams(**params)
    return service.get_post(validated_params)

@router.post("/get-article", response_model=ApiResponse)
@schema(
    input_schema_class=GetArticleParams,
    output_schema_class=ApiResponse,
    examples=examples["/linkedin/get-article"]
)
async def get_article(
    params: Dict[str, Any] = Body(...),
    service: LinkedInService = Depends(get_linkedin_service)
):
    validated_params = GetArticleParams(**params)
    return service.get_article(validated_params)

@router.post("/get-article-comments", response_model=ApiResponse)
@schema(
    input_schema_class=GetArticleCommentsParams,
    output_schema_class=ApiResponse,
    examples=examples["/linkedin/get-article-comments"]
)
async def get_article_comments(
    params: Dict[str, Any] = Body(...),
    service: LinkedInService = Depends(get_linkedin_service)
):
    validated_params = GetArticleCommentsParams(**params)
    return service.get_article_comments(validated_params)

@router.post("/search-locations", response_model=ApiResponse)
@schema(
    input_schema_class=SearchLocationsParams,
    output_schema_class=ApiResponse,
    examples=examples["/linkedin/search-locations"]
)
async def search_locations(
    params: Dict[str, Any] = Body(...),
    service: LinkedInService = Depends(get_linkedin_service)
):
    validated_params = SearchLocationsParams(**params)
    return service.search_locations(validated_params)

# Apply centralized error handling
apply_error_handler_to_router(router) 