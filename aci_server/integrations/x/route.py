from fastapi import APIRouter, Depends, Body, Request, HTTPException
from typing import Dict, Any
from .service import TwitterService
from .client import TwitterClient
from .schema import *
from ..common.auth import validate_provider_api_key
from ..common.input_schema_decorator import schema
from ..common.utils import apply_error_handler_to_service, apply_error_handler_to_router, apply_error_handler_to_client
from ..common.examples_handler import ExamplesLoader
from ..common.auth import get_provider_custom_auth
import os

router = APIRouter(prefix="/x", tags=["x"])
examples = ExamplesLoader()

async def get_twitter_service(request: Request):
    try:
        api_key = os.environ.get("RAPID_API_TWITTER_API_KEY") or  os.environ.get("RAPID_API_LINKEDIN_API_KEY")
        auth_params = await get_provider_custom_auth(request, "x")
        raw_username = auth_params.get("username")
        # The TwitterClient constructor will use the parse_twitter_username method
        client = TwitterClient(api_key, raw_username)
        service = TwitterService(client)
        apply_error_handler_to_client(client)
        apply_error_handler_to_service(service)
        return service
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Twitter service initialization failed: {str(e)}")

@router.post("/get_user_profile", response_model=ApiResponse)
@schema(
    input_schema_class=GetUserProfileParams,
    output_schema_class=UserProfileResponse,
    examples=examples["/x/get_user_profile"]
)
async def get_user_profile(
    params: Dict[str, Any] = Body(...),
    service: TwitterService = Depends(get_twitter_service)
):
    validated_params = GetUserProfileParams(**params)
    return service.get_user_profile(validated_params)

@router.post("/get_me", response_model=ApiResponse)
@schema(
    input_schema_class=GetMeParams,
    output_schema_class=UserProfileResponse,
    examples=examples["/x/get_me"]
)
async def get_me(
    params: Dict[str, Any] = Body(...),
    service: TwitterService = Depends(get_twitter_service)
):
    validated_params = GetMeParams(**params)
    return service.get_me(validated_params)

@router.post("/get_user_timeline", response_model=ApiResponse)
@schema(
    input_schema_class=GetUserTimelineParams,
    output_schema_class=UserTimelineResponse,
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
    output_schema_class=UserFollowingResponse,
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
    output_schema_class=UserFollowersResponse,
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
    output_schema_class=TweetRetweetsResponse,
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
    output_schema_class=SearchTweetsResponse,
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
    output_schema_class=TweetThreadResponse,
    examples=examples["/x/get_tweet_thread"]
)
async def get_tweet_thread(
    params: GetTweetThreadParams,
    service: TwitterService = Depends(get_twitter_service)
):
    return service.get_tweet_thread(params)

@router.post("/get_latest_replies", response_model=ApiResponse)
@schema(
    input_schema_class=GetLatestRepliesParams,
    output_schema_class=LatestRepliesResponse,
    examples=examples["/x/get_latest_replies"]
)
async def get_latest_replies(
    params: GetLatestRepliesParams,
    service: TwitterService = Depends(get_twitter_service)
):
    return service.get_latest_replies(params)

@router.post("/get_list_timeline", response_model=ApiResponse)
@schema(
    input_schema_class=GetListTimelineParams,
    output_schema_class=ListTimelineResponse,
    examples=examples["/x/get_list_timeline"]
)
async def get_list_timeline(
    params: GetListTimelineParams,
    service: TwitterService = Depends(get_twitter_service)
):
    return service.get_list_timeline(params)

@router.post("/get_community_timeline", response_model=ApiResponse)
@schema(
    input_schema_class=GetCommunityTimelineParams,
    output_schema_class=CommunityTimelineResponse,
    examples=examples["/x/get_community_timeline"]
)
async def get_community_timeline(
    params: GetCommunityTimelineParams,
    service: TwitterService = Depends(get_twitter_service)
):
    return service.get_community_timeline(params)

@router.post("/get_list_followers", response_model=ApiResponse)
@schema(
    input_schema_class=GetListFollowersParams,
    output_schema_class=ListFollowersResponse,
    examples=examples["/x/get_list_followers"]
)
async def get_list_followers(
    params: GetListFollowersParams,
    service: TwitterService = Depends(get_twitter_service)
):
    return service.get_list_followers(params)

@router.post("/get_list_members", response_model=ApiResponse)
@schema(
    input_schema_class=GetListMembersParams,
    output_schema_class=ListMembersResponse,
    examples=examples["/x/get_list_members"]
)
async def get_list_members(
    params: GetListMembersParams,
    service: TwitterService = Depends(get_twitter_service)
):
    return service.get_list_members(params)

@router.post("/get_space", response_model=ApiResponse)
@schema(
    input_schema_class=GetSpaceParams,
    output_schema_class=SpaceResponse,
    examples=examples["/x/get_space"]
)
async def get_space(
    params: GetSpaceParams,
    service: TwitterService = Depends(get_twitter_service)
):
    return service.get_space(params)

@router.post("/validate_key")
async def validate_key(params: Dict[str, Any] = Body(...)):
    try:
        raw_username = params.get("username", "")
        
        # Handle empty username
        if not raw_username:
            return {"valid": False, "message": "Username is required"}
        
        # Parse the username using our utility function
        username = TwitterClient.parse_twitter_username(raw_username)
        
        # Handle empty username after parsing
        if not username:
            return {"valid": False, "message": "Could not extract a valid Twitter/X username"}
        
        # Basic validation - Twitter usernames should be between 1-15 characters
        # and contain only alphanumeric characters and underscores
        if not 1 <= len(username) <= 15:
            return {"valid": False, "message": f"Twitter username '{username}' must be between 1-15 characters"}
        
        if not all(c.isalnum() or c == '_' for c in username):
            return {"valid": False, "message": f"Twitter username '{username}' can only contain letters, numbers, and underscores"}
        
        # If we have the API key in environment, we could do a more thorough validation
        # by actually checking if the user exists, but for now we'll just do basic validation
        api_key = os.environ.get("RAPID_API_TWITTER_API_KEY") or os.environ.get("RAPID_API_LINKEDIN_API_KEY")
        if api_key:
            client = TwitterClient(api_key, username)
            try:
                # Try to get the user profile to verify the username exists
                result = client.get_user_profile(screenname=username)
                if result and 'id' in result:
                    return {"valid": True, "message": f"Username '{username}' is valid"}
                else:
                    return {"valid": False, "message": f"Username '{username}' not found"}
            except Exception as e:
                return {"valid": False, "message": f"Error validating username '{username}': {str(e)}"}
        
        # If we don't have an API key or couldn't validate against the API,
        # we'll just return valid based on the format check
        return {"valid": True, "message": f"Username '{username}' format is valid"}
    except Exception as e:
        return {"valid": False, "message": f"Error validating username: {str(e)}"}

# Apply centralized error handling
apply_error_handler_to_router(router) 