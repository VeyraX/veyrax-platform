from fastapi import APIRouter, Depends, Body, Request, HTTPException
from typing import Dict, Any
from starlette.requests import Request as FastAPIRequest
from .service import InstagramService
from .client import InstagramClient
from .schema import (
    ApiResponse,
    GetUserDetailsParams,
    GetUserDetailsResponse,
    GetUserPostsParams,
    GetUserPostsResponse,
    GetUserFollowingParams,
    GetUserFollowersParams,
    GetUserFollowingResponse,
    GetUserFollowersResponse,
    GetPostDetailsParams,
    GetPostDetailsResponse,
    GetPostCommentsParams,
    GetPostCommentsResponse,
    GetMeParams
)
from ..common.auth import validate_provider_api_key
from ..common.input_schema_decorator import schema
from ..common.utils import apply_error_handler_to_service, apply_error_handler_to_router, apply_error_handler_to_client
from ..common.examples_handler import ExamplesLoader
from ..common.auth import get_provider_custom_auth
import os

router = APIRouter(prefix="/instagram", tags=["instagram"])
examples = ExamplesLoader()

async def get_instagram_service(request: FastAPIRequest):
    try:
        api_key = os.environ.get("RAPID_API_INSTAGRAM_API_KEY")
        try:
            auth_params = await get_provider_custom_auth(request, "instagram")
            raw_username = auth_params.get("username")
        except Exception as e:
            raw_username = None
        client = InstagramClient(api_key, raw_username)
        apply_error_handler_to_client(client)
        service = InstagramService(client)
        apply_error_handler_to_service(service)
        return service
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Failed to initialize Instagram service: {str(e)}"
        )

@router.post("/get_user_details", response_model=ApiResponse)
@schema(
    input_schema_class=GetUserDetailsParams,
    output_schema_class=GetUserDetailsResponse,
    examples=examples["/instagram/get_user_details"]
)
async def get_user_details(
    params: Dict[str, Any] = Body(...),
    service: InstagramService = Depends(get_instagram_service)
):
    validated_params = GetUserDetailsParams(**params)
    return service.get_user_details(validated_params)

@router.post("/get_me", response_model=ApiResponse)
@schema(
    input_schema_class=GetMeParams,
    output_schema_class=GetUserDetailsResponse,
    examples=examples["/instagram/get_me"]
)
async def get_me(
    params: Dict[str, Any] = Body(...),
    service: InstagramService = Depends(get_instagram_service)
):
    validated_params = GetMeParams(**params)
    return service.get_me(validated_params)

@router.post("/get_user_posts", response_model=ApiResponse)
@schema(
    input_schema_class=GetUserPostsParams,
    output_schema_class=GetUserPostsResponse,
    examples=examples["/instagram/get_user_posts"]
)
async def get_user_posts(
    params: Dict[str, Any] = Body(...),
    service: InstagramService = Depends(get_instagram_service)
):
    validated_params = GetUserPostsParams(**params)
    return service.get_user_posts(validated_params)

@router.post("/get_user_following", response_model=ApiResponse)
@schema(
    input_schema_class=GetUserFollowingParams,
    output_schema_class=GetUserFollowingResponse,
    examples=examples["/instagram/get_user_following"]
)
async def get_user_following(
    params: Dict[str, Any] = Body(...),
    service: InstagramService = Depends(get_instagram_service)
):
    validated_params = GetUserFollowingParams(**params)
    return service.get_user_following(validated_params)

@router.post("/get_user_followers", response_model=ApiResponse)
@schema(
    input_schema_class=GetUserFollowersParams,
    output_schema_class=GetUserFollowersResponse,
    examples=examples["/instagram/get_user_followers"]
)
async def get_user_followers(
    params: Dict[str, Any] = Body(...),
    service: InstagramService = Depends(get_instagram_service)
):
    validated_params = GetUserFollowersParams(**params)
    return service.get_user_followers(validated_params)

@router.post("/get_post_details", response_model=ApiResponse)
@schema(
    input_schema_class=GetPostDetailsParams,
    output_schema_class=GetPostDetailsResponse,
    examples=examples["/instagram/get_post_details"]
)
async def get_post_details(
    params: Dict[str, Any] = Body(...),
    service: InstagramService = Depends(get_instagram_service)
):
    validated_params = GetPostDetailsParams(**params)
    return service.get_post_details(validated_params)

@router.post("/get_post_comments", response_model=ApiResponse)
@schema(
    input_schema_class=GetPostCommentsParams,
    output_schema_class=GetPostCommentsResponse,
    examples=examples["/instagram/get_post_comments"]
)
async def get_post_comments(
    params: Dict[str, Any] = Body(...),
    service: InstagramService = Depends(get_instagram_service)
):
    validated_params = GetPostCommentsParams(**params)
    return service.get_post_comments(validated_params)

@router.post("/validate_key")
async def validate_key(params: Dict[str, Any] = Body(...)):
    try:
        username = params.get("username", "")
        
        if not username:
            return {"valid": False, "message": "Instagram username is required"}
        
        clean_username = InstagramClient.parse_instagram_username(username)
        
        if not clean_username:
            return {"valid": False, "message": "Could not extract a valid Instagram username"}
        
        try:
            api_key = os.environ.get("RAPID_API_INSTAGRAM_API_KEY")
            if not api_key:
                return {"valid": False, "message": "Instagram API key not configured"}
                
            client = InstagramClient(api_key)
            client.get_user_details(username=clean_username)
            
            return {
                "valid": True, 
                "message": "Instagram username is valid and exists", 
                "username": clean_username
            }
        except Exception as e:
            return {"valid": False, "message": f"Username validation failed: {str(e)}"}
        
    except Exception as e:
        return {"valid": False, "message": str(e)}

apply_error_handler_to_router(router)
