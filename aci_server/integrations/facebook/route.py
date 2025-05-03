from fastapi import APIRouter, Depends, Body, Request, HTTPException
from typing import Dict, Any
from starlette.requests import Request as FastAPIRequest
from .service import FacebookService
from .client import FacebookClient
from .schema import (
    ApiResponse,
    SearchLocationsParams,
    SearchPostsParams,
    SearchPlacesParams,
    SearchPagesParams,
    SearchEventsParams,
    GetPageDetailsParams,
    GetPageIdParams,
    GetPagePostsParams,
    GetPageReviewsParams,
    GetPostCommentsParams,
    GetPostDetailsParams,
    SearchLocationsResponse,
    SearchPostsResponse,
    SearchPlacesResponse,
    SearchPagesResponse,
    SearchEventsResponse,
    GetPageDetailsResponse,
    GetPageIdResponse,
    GetPagePostsResponse,
    GetPageReviewsResponse,
    GetPostCommentsResponse,
    GetPostDetailsResponse,
    GetGroupPostsParams,
    GetGroupDetailsParams,
    GetGroupIdParams,
    GetGroupPostsResponse,
    GetGroupDetailsResponse,
    GetGroupIdResponse,
    GetProfilePostsParams,
    GetProfileDetailsIdParams,
    GetProfileDetailsUrlParams,
    GetProfileIdParams,
    GetProfilePostsResponse,
    GetProfileDetailsResponse,
    GetProfileIdResponse,
    GetMeParams,
    GetMeResponse
)
from ..common.auth import validate_provider_api_key
from ..common.input_schema_decorator import schema
from ..common.utils import apply_error_handler_to_service, apply_error_handler_to_router, apply_error_handler_to_client
from ..common.examples_handler import ExamplesLoader
from ..common.auth import get_provider_custom_auth
import os 

router = APIRouter(prefix="/facebook", tags=["facebook"])
examples = ExamplesLoader()

async def get_facebook_service(request: FastAPIRequest):
    try:
        api_key = os.environ.get('RAPID_API_FACEBOK_API_KEY')
        try:
            auth_params = await get_provider_custom_auth(request, "facebook")
            profile_url = auth_params.get("profile_url")
        except Exception as e:
            profile_url = None
        client = FacebookClient(api_key, profile_url)
        apply_error_handler_to_client(client)
        service = FacebookService(client)
        apply_error_handler_to_service(service)
        return service
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Failed to initialize Facebook service: {str(e)}"
        )

@router.post("/search_locations", response_model=ApiResponse)
@schema(
    input_schema_class=SearchLocationsParams,
    output_schema_class=SearchLocationsResponse,
    examples=examples["/facebook/search_locations"]
)
async def search_locations(
    params: Dict[str, Any] = Body(...),
    service: FacebookService = Depends(get_facebook_service)
):
    validated_params = SearchLocationsParams(**params)
    return service.search_locations(validated_params)

@router.post("/search_posts", response_model=ApiResponse)
@schema(
    input_schema_class=SearchPostsParams,
    output_schema_class=SearchPostsResponse,
    examples=examples["/facebook/search_posts"]
)
async def search_posts(
    params: Dict[str, Any] = Body(...),
    service: FacebookService = Depends(get_facebook_service)
):
    validated_params = SearchPostsParams(**params)
    return service.search_posts(validated_params)

@router.post("/search_places", response_model=ApiResponse)
@schema(
    input_schema_class=SearchPlacesParams,
    output_schema_class=SearchPlacesResponse,
    examples=examples["/facebook/search_places"]
)
async def search_places(
    params: Dict[str, Any] = Body(...),
    service: FacebookService = Depends(get_facebook_service)
):
    validated_params = SearchPlacesParams(**params)
    return service.search_places(validated_params)

@router.post("/search_pages", response_model=ApiResponse)
@schema(
    input_schema_class=SearchPagesParams,
    output_schema_class=SearchPagesResponse,
    examples=examples["/facebook/search_pages"]
)
async def search_pages(
    params: Dict[str, Any] = Body(...),
    service: FacebookService = Depends(get_facebook_service)
):
    validated_params = SearchPagesParams(**params)
    return service.search_pages(validated_params)

@router.post("/search_events", response_model=ApiResponse)
@schema(
    input_schema_class=SearchEventsParams,
    output_schema_class=SearchEventsResponse,
    examples=examples["/facebook/search_events"]
)
async def search_events(
    params: Dict[str, Any] = Body(...),
    service: FacebookService = Depends(get_facebook_service)
):
    validated_params = SearchEventsParams(**params)
    return service.search_events(validated_params)

@router.post("/get_page_details", response_model=ApiResponse)
@schema(
    input_schema_class=GetPageDetailsParams,
    output_schema_class=GetPageDetailsResponse,
    examples=examples["/facebook/get_page_details"]
)
async def get_page_details(
    params: Dict[str, Any] = Body(...),
    service: FacebookService = Depends(get_facebook_service)
):
    validated_params = GetPageDetailsParams(**params)
    return service.get_page_details(validated_params)

@router.post("/get_page_id", response_model=ApiResponse)
@schema(
    input_schema_class=GetPageIdParams,
    output_schema_class=GetPageIdResponse,
    examples=examples["/facebook/get_page_id"]
)
async def get_page_id(
    params: Dict[str, Any] = Body(...),
    service: FacebookService = Depends(get_facebook_service)
):
    validated_params = GetPageIdParams(**params)
    return service.get_page_id(validated_params)

@router.post("/get_page_posts", response_model=ApiResponse)
@schema(
    input_schema_class=GetPagePostsParams,
    output_schema_class=GetPagePostsResponse,
    examples=examples["/facebook/get_page_posts"]
)
async def get_page_posts(
    params: Dict[str, Any] = Body(...),
    service: FacebookService = Depends(get_facebook_service)
):
    validated_params = GetPagePostsParams(**params)
    return service.get_page_posts(validated_params)

@router.post("/get_page_reviews", response_model=ApiResponse)
@schema(
    input_schema_class=GetPageReviewsParams,
    output_schema_class=GetPageReviewsResponse,
    examples=examples["/facebook/get_page_reviews"]
)
async def get_page_reviews(
    params: Dict[str, Any] = Body(...),
    service: FacebookService = Depends(get_facebook_service)
):
    validated_params = GetPageReviewsParams(**params)
    return service.get_page_reviews(validated_params)

@router.post("/get_post_comments", response_model=ApiResponse)
@schema(
    input_schema_class=GetPostCommentsParams,
    output_schema_class=GetPostCommentsResponse,
    examples=examples["/facebook/get_post_comments"]
)
async def get_post_comments(
    params: Dict[str, Any] = Body(...),
    service: FacebookService = Depends(get_facebook_service)
):
    validated_params = GetPostCommentsParams(**params)
    return service.get_post_comments(validated_params)

@router.post("/get_post_details", response_model=ApiResponse)
@schema(
    input_schema_class=GetPostDetailsParams,
    output_schema_class=GetPostDetailsResponse,
    examples=examples["/facebook/get_post_details"]
)
async def get_post_details(
    params: Dict[str, Any] = Body(...),
    service: FacebookService = Depends(get_facebook_service)
):
    validated_params = GetPostDetailsParams(**params)
    return service.get_post_details(validated_params)

@router.post("/get_group_posts", response_model=ApiResponse)
@schema(
    input_schema_class=GetGroupPostsParams,
    output_schema_class=GetGroupPostsResponse,
    examples=examples["/facebook/get_group_posts"]
)
async def get_group_posts(
    params: Dict[str, Any] = Body(...),
    service: FacebookService = Depends(get_facebook_service)
):
    validated_params = GetGroupPostsParams(**params)
    return service.get_group_posts(validated_params)

@router.post("/get_group_details", response_model=ApiResponse)
@schema(
    input_schema_class=GetGroupDetailsParams,
    output_schema_class=GetGroupDetailsResponse,
    examples=examples["/facebook/get_group_details"]
)
async def get_group_details(
    params: Dict[str, Any] = Body(...),
    service: FacebookService = Depends(get_facebook_service)
):
    validated_params = GetGroupDetailsParams(**params)
    return service.get_group_details(validated_params)

@router.post("/get_group_id", response_model=ApiResponse)
@schema(
    input_schema_class=GetGroupIdParams,
    output_schema_class=GetGroupIdResponse,
    examples=examples["/facebook/get_group_id"]
)
async def get_group_id(
    params: Dict[str, Any] = Body(...),
    service: FacebookService = Depends(get_facebook_service)
):
    validated_params = GetGroupIdParams(**params)
    return service.get_group_id(validated_params)

@router.post("/get_profile_posts", response_model=ApiResponse)
@schema(
    input_schema_class=GetProfilePostsParams,
    output_schema_class=GetProfilePostsResponse,
    examples=examples["/facebook/get_profile_posts"]
)
async def get_profile_posts(
    params: Dict[str, Any] = Body(...),
    service: FacebookService = Depends(get_facebook_service)
):
    validated_params = GetProfilePostsParams(**params)
    return service.get_profile_posts(validated_params)

@router.post("/get_profile_details_id", response_model=ApiResponse)
@schema(
    input_schema_class=GetProfileDetailsIdParams,
    output_schema_class=GetProfileDetailsResponse,
    examples=examples["/facebook/get_profile_details_id"]
)
async def get_profile_details_id(
    params: Dict[str, Any] = Body(...),
    service: FacebookService = Depends(get_facebook_service)
):
    validated_params = GetProfileDetailsIdParams(**params)
    return service.get_profile_details_id(validated_params)

@router.post("/get_profile_details_url", response_model=ApiResponse)
@schema(
    input_schema_class=GetProfileDetailsUrlParams,
    output_schema_class=GetProfileDetailsResponse,
    examples=examples["/facebook/get_profile_details_url"]
)
async def get_profile_details_url(
    params: Dict[str, Any] = Body(...),
    service: FacebookService = Depends(get_facebook_service)
):
    validated_params = GetProfileDetailsUrlParams(**params)
    return service.get_profile_details_url(validated_params)

@router.post("/get_profile_id", response_model=ApiResponse)
@schema(
    input_schema_class=GetProfileIdParams,
    output_schema_class=GetProfileIdResponse,
    examples=examples["/facebook/get_profile_id"]
)
async def get_profile_id(
    params: Dict[str, Any] = Body(...),
    service: FacebookService = Depends(get_facebook_service)
):
    validated_params = GetProfileIdParams(**params)
    return service.get_profile_id(validated_params)

@router.post("/get_me", response_model=ApiResponse)
@schema(
    input_schema_class=GetMeParams,
    output_schema_class=GetMeResponse,
    examples=None
)
async def get_me(
    params: Dict[str, Any] = Body(...),
    service: FacebookService = Depends(get_facebook_service)
):
    validated_params = GetMeParams(**params)
    return service.get_me(validated_params)

@router.post("/validate_key")
async def validate_key(params: Dict[str, Any] = Body(...)):
    try:
        profile_url = params.get("profile_url", "")
        
        if not profile_url:
            return {"valid": False, "message": "Facebook profile URL is required"}
        
        clean_url = FacebookClient.parse_facebook_url(profile_url)
        
        if not clean_url:
            return {"valid": False, "message": "Could not extract a valid Facebook profile URL"}
        
        if "facebook.com" not in clean_url:
            return {"valid": False, "message": f"Invalid Facebook URL: {clean_url}"}
        
        return {
            "valid": True, 
            "message": "Facebook profile URL is valid", 
            "profile_url": clean_url
        }
        
    except Exception as e:
        return {"valid": False, "message": str(e)}

apply_error_handler_to_router(router)
