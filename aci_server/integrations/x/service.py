from typing import Dict, Any, Optional
import os
import logging
from fastapi import HTTPException
from .client import TwitterClient
from .schema import *
from ..common.component_handler import load_components, prepare_components_auto

logger = logging.getLogger(__name__)

class TwitterServiceError(Exception):
    """Exception raised for errors in the Twitter service."""
    pass

class TwitterService:
    def __init__(self, client: TwitterClient):
        self.client = client
        self.components_data = self._load_components()
    
    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
    
    def prepare_response(self, data: Any, component_name: str = None) -> ApiResponse:
        tool_name = "x"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)
    
    def get_user_profile(self, params: GetUserProfileParams) -> ApiResponse:
        # Prepare request parameters
        request_params = {}
        
        # Check if screenname is provided in the params
        if params.screenname:
            request_params["screenname"] = params.screenname
        # If not provided, use the client's username
        elif self.client.username:
            request_params["screenname"] = self.client.username
        else:
            # If neither is available, raise an HTTP error
            raise HTTPException(status_code=401, detail="Screenname is required but not provided, and no authenticated username is available")
        
        if params.rest_id:
            request_params["rest_id"] = params.rest_id
        
        # Make API call through client
        response = self.client.get_user_profile(**request_params)
        
        # Transform the API response to match our schema
        user_profile_data = UserProfileData(**response)
        
        # Create the standard response structure
        user_profile_response = UserProfileResponse(
            success=True,
            message="User profile retrieved successfully",
            data=user_profile_data
        )
        
        return self.prepare_response(user_profile_response, None)
    
    def get_me(self, params: GetMeParams) -> ApiResponse:
        """
        Retrieve the authenticated user's profile based on the stored username.
        """
        # Make API call through client
        response = self.client.get_me()
        
        # Transform the API response to match our schema
        user_profile_data = UserProfileData(**response)
        
        # Create the standard response structure
        user_profile_response = UserProfileResponse(
            success=True,
            message="User profile retrieved successfully",
            data=user_profile_data
        )
        
        return self.prepare_response(user_profile_response, None)
        
    def get_user_timeline(self, params: GetUserTimelineParams) -> ApiResponse:
        # Prepare request parameters
        request_params = {}
        
        # Check if screenname is provided in the params
        if params.screenname:
            request_params["screenname"] = params.screenname
        # If not provided, use the client's username
        elif self.client.username:
            request_params["screenname"] = self.client.username
        else:
            # If neither is available, raise an HTTP error
            raise HTTPException(status_code=401, detail="Screenname is required but not provided, and no authenticated username is available")
        
        if params.cursor:
            request_params["cursor"] = params.cursor
        
        # Make API call through client
        response = self.client.get_user_timeline(**request_params)
        
        # Transform the API response to match our schema
        # If 'user' exists in response, transform it to UserProfileData
        user_data = None
        if 'user' in response and response['user']:
            user_data = UserProfileData(**response['user'])
        
        # Create the timeline data structure
        timeline_data = UserTimelineData(
            timeline=response.get('timeline', []),
            user=user_data,
            next_cursor=response.get('next_cursor'),
            prev_cursor=response.get('prev_cursor'),
            status=response.get('status')
        )
        
        # Create the standard response structure
        timeline_response = UserTimelineResponse(
            success=True,
            message="User timeline retrieved successfully",
            data=timeline_data
        )
        
        return self.prepare_response(timeline_response, None)
        
    def get_user_following(self, params: GetUserFollowingParams) -> ApiResponse:
        # Prepare request parameters
        request_params = {}
        
        # Check if screenname is provided in the params
        if params.screenname:
            request_params["screenname"] = params.screenname
        # If not provided, use the client's username
        elif self.client.username:
            request_params["screenname"] = self.client.username
        else:
            # If neither is available, raise an HTTP error
            raise HTTPException(status_code=401, detail="Screenname is required but not provided, and no authenticated username is available")
        
        if params.cursor:
            request_params["cursor"] = params.cursor
        
        # Make API call through client
        response = self.client.get_user_following(**request_params)
        
        # Create the following data structure
        following_data = UserFollowingData(
            following=response.get('following', []),
            next_cursor=response.get('next_cursor')
        )
        
        # Create the standard response structure
        following_response = UserFollowingResponse(
            success=True,
            message="User following list retrieved successfully",
            data=following_data
        )
        
        return self.prepare_response(following_response, None)
        
    def get_user_followers(self, params: GetUserFollowersParams) -> ApiResponse:
        # Prepare request parameters
        request_params = {}
        
        # Check if screenname is provided in the params
        if params.screenname:
            request_params["screenname"] = params.screenname
        # If not provided, use the client's username
        elif self.client.username:
            request_params["screenname"] = self.client.username
        else:
            # If neither is available, raise an HTTP error
            raise HTTPException(status_code=401, detail="Screenname is required but not provided, and no authenticated username is available")
        
        if params.cursor:
            request_params["cursor"] = params.cursor
        
        # Make API call through client
        response = self.client.get_user_followers(**request_params)
        
        # Create the followers data structure
        followers_data = UserFollowersData(
            followers_count=response.get('followers_count'),
            followers=response.get('followers', []),
            next_cursor=response.get('next_cursor'),
            status=response.get('status')
        )
        
        # Create the standard response structure
        followers_response = UserFollowersResponse(
            success=True,
            message="User followers list retrieved successfully",
            data=followers_data
        )
        
        return self.prepare_response(followers_response, None)
        
    def get_tweet(self, params: GetTweetParams) -> ApiResponse:
        # Make API call through client
        response = self.client.get_tweet(id=params.id)
        
        # Create the tweet data structure
        tweet_data = TweetData(
            id=response.get('id'),
            likes=response.get('likes'),
            created_at=response.get('created_at'),
            text=response.get('text'),
            retweets=response.get('retweets'),
            bookmarks=response.get('bookmarks'),
            quotes=response.get('quotes'),
            replies=response.get('replies'),
            lang=response.get('lang'),
            conversation_id=response.get('conversation_id'),
            author=response.get('author'),
            media=response.get('media')
        )
        
        # Create the standard response structure
        tweet_response = TweetResponse(
            success=True,
            message="Tweet retrieved successfully",
            data=tweet_data
        )
        
        return self.prepare_response(tweet_response, None)
        
    def get_tweet_retweets(self, params: GetTweetRetweetsParams) -> ApiResponse:
        # Prepare request parameters
        request_params = {"id": params.id}
        if params.cursor:
            request_params["cursor"] = params.cursor
        
        # Make API call through client
        response = self.client.get_tweet_retweets(**request_params)
        
        # Create the retweets data structure
        retweets_data = TweetRetweetsData(
            retweets=response.get('retweets', []),
            next_cursor=response.get('next_cursor')
        )
        
        # Create the standard response structure
        retweets_response = TweetRetweetsResponse(
            success=True,
            message="Tweet retweets retrieved successfully",
            data=retweets_data
        )
        
        return self.prepare_response(retweets_response, None)
        
    def search_tweets(self, params: SearchTweetsParams) -> ApiResponse:
        # Make API call through client
        response = self.client.search_tweets(
            query=params.query,
            search_type=params.search_type
        )
        
        # Create the search data structure
        search_data = {
            "timeline": response.get('timeline', []),
            "next_cursor": response.get('next_cursor')
        }
        
        # Create the standard response structure
        search_response = {
            "success": True,
            "message": "Tweets retrieved successfully",
            "data": search_data
        }
        
        return self.prepare_response(search_response, None)
        
    def get_tweet_thread(self, params: GetTweetThreadParams) -> ApiResponse:
        # Prepare request parameters
        request_params = {"id": params.id}
        if params.cursor:
            request_params["cursor"] = params.cursor
        
        # Make API call through client
        response = self.client.get_tweet_thread(**request_params)
        
        # Create the thread data structure, copying all fields from the response
        thread_data = TweetThreadData(
            id=response.get("id"),
            likes=response.get("likes", 0),
            created_at=response.get("created_at"),
            text=response.get("text"),
            display_text=response.get("display_text"),
            status=response.get("status"),
            retweets=response.get("retweets", 0),
            bookmarks=response.get("bookmarks", 0),
            quotes=response.get("quotes", 0),
            replies=response.get("replies", 0),
            views=response.get("views"),
            lang=response.get("lang"),
            conversation_id=response.get("conversation_id"),
            source=response.get("source"),
            author=response.get("author"),
            media=response.get("media"),
            thread=response.get("thread", []),
            cursor=response.get("cursor")
        )
        
        # Create the standard response structure
        thread_response = TweetThreadResponse(
            success=True,
            message="Tweet thread retrieved successfully",
            data=thread_data
        )
        
        return self.prepare_response(thread_response, None)
        
    def get_latest_replies(self, params: GetLatestRepliesParams) -> ApiResponse:
        # Prepare request parameters
        request_params = {"id": params.id}
        if params.cursor:
            request_params["cursor"] = params.cursor
        
        # Make API call through client
        response = self.client.get_latest_replies(**request_params)
        
        # Create the replies data structure
        replies_data = LatestRepliesData(
            status=response.get("status"),
            timeline=response.get("timeline", []),
            next_cursor=response.get("next_cursor"),
            prev_cursor=response.get("prev_cursor")
        )
        
        # Create the standard response structure
        replies_response = LatestRepliesResponse(
            success=True,
            message="Latest replies retrieved successfully",
            data=replies_data
        )
        
        return self.prepare_response(replies_response, None)
        
    def get_list_timeline(self, params: GetListTimelineParams) -> ApiResponse:
        try:
            response = self.client.get_list_timeline(
                list_id=params.list_id,
                cursor=params.cursor,
                limit=params.limit
            )
            
            timeline_data = ListTimelineData(
                timeline=response.get("timeline", []),
                next_cursor=response.get("next_cursor")
            )
            
            # Create the standard response structure
            timeline_response = ListTimelineResponse(
                success=True,
                message="List timeline retrieved successfully",
                data=timeline_data
            )
            
            return self.prepare_response(timeline_response, None)
        except Exception as e:
            logger.error(f"Error getting list timeline: {e}")
            raise TwitterServiceError(f"Failed to get list timeline: {str(e)}")
            
    def get_community_timeline(self, params: GetCommunityTimelineParams) -> ApiResponse:
        try:
            response = self.client.get_community_timeline(
                community_id=params.community_id,
                ranking=params.ranking,
                cursor=params.cursor,
                limit=params.limit
            )
            
            timeline_data = CommunityTimelineData(
                timeline=response.get("timeline", []),
                next_cursor=response.get("next_cursor")
            )
            
            # Create the standard response structure
            timeline_response = CommunityTimelineResponse(
                success=True,
                message="Community timeline retrieved successfully",
                data=timeline_data
            )
            
            return self.prepare_response(timeline_response, None)
        except Exception as e:
            logger.error(f"Error getting community timeline: {e}")
            raise TwitterServiceError(f"Failed to get community timeline: {str(e)}")
            
    def get_list_followers(self, params: GetListFollowersParams) -> ApiResponse:
        try:
            response = self.client.get_list_followers(
                list_id=params.list_id,
                cursor=params.cursor,
                limit=params.limit
            )
            
            # Process followers to ensure they match the expected model
            followers = []
            for follower in response.get("followers", []):
                # Convert each follower to the expected model format
                follower_data = ListFollowerData(
                    user_id=follower.get("user_id", ""),
                    screen_name=follower.get("screen_name", ""),
                    name=follower.get("name", ""),
                    profile_image=follower.get("profile_image", ""),
                    description=follower.get("description"),
                    followers_count=follower.get("followers_count", 0),
                    friends_count=follower.get("friends_count", 0),
                    statuses_count=follower.get("statuses_count", 0),
                    media_count=follower.get("media_count", 0),
                    created_at=follower.get("created_at", ""),
                    location=follower.get("location"),
                    blue_verified=follower.get("blue_verified", False),
                    verified=follower.get("verified", False),
                    website=follower.get("website"),
                    affiliates=follower.get("affiliates", []),
                    business_account=follower.get("business_account")
                )
                followers.append(follower_data)
            
            followers_data = ListFollowersData(
                followers=followers,
                next_cursor=response.get("next_cursor")
            )
            
            # Create the standard response structure
            followers_response = ListFollowersResponse(
                success=True,
                message="List followers retrieved successfully",
                data=followers_data
            )
            
            return self.prepare_response(followers_response, None)
        except Exception as e:
            logger.error(f"Error getting list followers: {e}")
            raise TwitterServiceError(f"Failed to get list followers: {str(e)}")
            
    def get_list_members(self, params: GetListMembersParams) -> ApiResponse:
        try:
            response = self.client.get_list_members(
                list_id=params.list_id,
                cursor=params.cursor,
                limit=params.limit
            )
            
            # Process members to ensure they match the expected model
            members = []
            for member in response.get("members", []):
                # Convert each member to the expected model format
                member_data = ListMemberData(
                    user_id=member.get("user_id", ""),
                    screen_name=member.get("screen_name", ""),
                    name=member.get("name", ""),
                    profile_image=member.get("profile_image", ""),
                    description=member.get("description"),
                    followers_count=member.get("followers_count", 0),
                    friends_count=member.get("friends_count", 0),
                    statuses_count=member.get("statuses_count", 0),
                    media_count=member.get("media_count", 0),
                    created_at=member.get("created_at", ""),
                    location=member.get("location"),
                    blue_verified=member.get("blue_verified", False),
                    verified=member.get("verified", False),
                    website=member.get("website"),
                    affiliates=member.get("affiliates", []),
                    business_account=member.get("business_account")
                )
                members.append(member_data)
            
            members_data = ListMembersData(
                members=members,
                next_cursor=response.get("next_cursor")
            )
            
            # Create the standard response structure
            members_response = ListMembersResponse(
                success=True,
                message="List members retrieved successfully",
                data=members_data
            )
            
            return self.prepare_response(members_response, None)
        except Exception as e:
            logger.error(f"Error getting list members: {e}")
            raise TwitterServiceError(f"Failed to get list members: {str(e)}")
            
    def get_space(self, params: GetSpaceParams) -> ApiResponse:
        try:
            response = self.client.get_space(
                id=params.id
            )
            
            space_data = SpaceData(**response)
            
            # Create the standard response structure
            space_response = SpaceResponse(
                success=True,
                message="Space retrieved successfully",
                data=space_data
            )
            
            return self.prepare_response(space_response, None)
        except Exception as e:
            logger.error(f"Error getting space: {e}")
            raise TwitterServiceError(f"Failed to get space: {str(e)}") 