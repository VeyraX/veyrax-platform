from fastapi import APIRouter, Depends, Body, Request, HTTPException
from typing import Dict, Any
from .service import TwitterService
from .client import TwitterClient
from .schema import *
from ..common.auth import validate_provider_api_key
from ..common.input_schema_decorator import schema
from ..common.utils import apply_error_handler_to_service, apply_error_handler_to_router, apply_error_handler_to_client
from ..common.examples_handler import ExamplesLoader
import os

router = APIRouter(prefix="/x", tags=["x"])
examples = ExamplesLoader()

async def get_twitter_service(request: Request):
    try:
        api_key = os.environ.get("RAPID_API_TWITTER_API_KEY") or  os.environ.get("RAPID_API_LINKEDIN_API_KEY")  # they are usually same
        client = TwitterClient(api_key)
        service = TwitterService(client)
        apply_error_handler_to_client(client)
        apply_error_handler_to_service(service)
        return service
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Twitter service initialization failed: {str(e)}")

@router.post("/get_user_profile", response_model=ApiResponse)
@schema(
    input_schema_class=GetUserProfileParams,
    output_schema_class=ApiResponse,
    examples=examples["/x/get_user_profile"]
)
async def get_user_profile(
    params: Dict[str, Any] = Body(...),
    service: TwitterService = Depends(get_twitter_service)
):
    validated_params = GetUserProfileParams(**params)
    return service.get_user_profile(validated_params)

@router.post("/get_user_timeline", response_model=ApiResponse)
@schema(
    input_schema_class=GetUserTimelineParams,
    output_schema_class=ApiResponse,
    examples=examples["/x/get_user_timeline"]
)
async def get_user_timeline(
    params: Dict[str, Any] = Body(...),
    service: TwitterService = Depends(get_twitter_service)
):
    validated_params = GetUserTimelineParams(**params)
    return service.get_user_timeline(validated_params)

@router.post("/get_user_following", response_model=ApiResponse)
@schema(
    input_schema_class=GetUserFollowingParams,
    output_schema_class=ApiResponse,
    examples=examples["/x/get_user_following"]
)
async def get_user_following(
    params: Dict[str, Any] = Body(...),
    service: TwitterService = Depends(get_twitter_service)
):
    validated_params = GetUserFollowingParams(**params)
    return service.get_user_following(validated_params)

@router.post("/get_user_followers", response_model=ApiResponse)
@schema(
    input_schema_class=GetUserFollowersParams,
    output_schema_class=ApiResponse,
    examples=examples["/x/get_user_followers"]
)
async def get_user_followers(
    params: Dict[str, Any] = Body(...),
    service: TwitterService = Depends(get_twitter_service)
):
    validated_params = GetUserFollowersParams(**params)
    return service.get_user_followers(validated_params)

@router.post("/get_tweet", response_model=ApiResponse)
@schema(
    input_schema_class=GetTweetParams,
    output_schema_class=TweetResponse,
    examples=examples["/x/get_tweet"]
)
async def get_tweet(
    params: Dict[str, Any] = Body(...),
    service: TwitterService = Depends(get_twitter_service)
):
    validated_params = GetTweetParams(**params)
    return service.get_tweet(validated_params)

@router.post("/get_tweet_retweets", response_model=ApiResponse)
@schema(
    input_schema_class=GetTweetRetweetsParams,
    output_schema_class=ApiResponse,
    examples=examples["/x/get_tweet_retweets"]
)
async def get_tweet_retweets(
    params: Dict[str, Any] = Body(...),
    service: TwitterService = Depends(get_twitter_service)
):
    validated_params = GetTweetRetweetsParams(**params)
    return service.get_tweet_retweets(validated_params)

@router.post("/search_tweets", response_model=ApiResponse)
@schema(
    input_schema_class=SearchTweetsParams,
    output_schema_class=ApiResponse,
    examples=examples["/x/search_tweets"]
)
async def search_tweets(
    params: Dict[str, Any] = Body(...),
    service: TwitterService = Depends(get_twitter_service)
):
    validated_params = SearchTweetsParams(**params)
    return service.search_tweets(validated_params)

@router.post("/get_tweet_thread", response_model=ApiResponse)
@schema(
    input_schema_class=GetTweetThreadParams,
    output_schema_class=ApiResponse,
    examples=examples["/x/get_tweet_thread"]
)
async def get_tweet_thread(
    params: GetTweetThreadParams,
    service: TwitterService = Depends(get_twitter_service)
):
    return service.get_tweet_thread(params)

@router.post("/get_latest_replies", response_model=ApiResponse)
async def get_latest_replies(
    params: GetLatestRepliesParams,
    service: TwitterService = Depends(get_twitter_service)
):
    return service.get_latest_replies(params)

@router.post("/get_list_timeline", response_model=ApiResponse)
async def get_list_timeline(
    params: GetListTimelineParams,
    service: TwitterService = Depends(get_twitter_service)
):
    return service.get_list_timeline(params)

@router.post("/get_community_timeline", response_model=ApiResponse)
async def get_community_timeline(
    params: GetCommunityTimelineParams,
    service: TwitterService = Depends(get_twitter_service)
):
    return service.get_community_timeline(params)

@router.post("/get_list_followers", response_model=ApiResponse)
async def get_list_followers(
    params: GetListFollowersParams,
    service: TwitterService = Depends(get_twitter_service)
):
    return service.get_list_followers(params)

@router.post("/get_list_members", response_model=ApiResponse)
async def get_list_members(
    params: GetListMembersParams,
    service: TwitterService = Depends(get_twitter_service)
):
    return service.get_list_members(params)

@router.post("/get_space", response_model=ApiResponse)
async def get_space(
    params: GetSpaceParams,
    service: TwitterService = Depends(get_twitter_service)
):
    return service.get_space(params)

# Apply centralized error handling
apply_error_handler_to_router(router) 