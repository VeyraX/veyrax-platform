from typing import Dict, Any, Optional
import os
from .client import InstagramClient
from .schema import (
    ApiResponse,
    GetUserDetailsParams,
    UserResponse,
    GetUserDetailsResponse,
    GetUserPostsParams,
    PostResponse,
    GetUserPostsResponse,
    GetUserFollowingParams,
    GetUserFollowersParams,
    UserListResponse,
    GetUserFollowingResponse,
    GetUserFollowersResponse,
    GetPostDetailsParams,
    PostDetailData,
    GetPostDetailsResponse,
    GetPostCommentsParams,
    PostCommentsResponse,
    GetPostCommentsResponse,
    GetMeParams
)
from ..common.component_handler import load_components, prepare_components_auto
from fastapi import HTTPException

class InstagramService:
    def __init__(self, client: InstagramClient):
        self.client = client
        self.components_data = self._load_components()
    
    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
    
    def prepare_response(self, data: Any, component_name: str = None) -> ApiResponse:
        tool_name = "instagram"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)
    
    def get_user_details(self, params: GetUserDetailsParams) -> ApiResponse:
        response = self.client.get_user_details(params.username)
        validated_data = UserResponse(**response)
        return self.prepare_response(validated_data, "InstagramUserDetailsCard")
    
    def get_me(self, params: GetMeParams) -> ApiResponse:
        response = self.client.get_me()
        
        validated_data = UserResponse(**response)
        
        return self.prepare_response(validated_data, "InstagramUserDetailsCard")
        
    def get_user_posts(self, params: GetUserPostsParams) -> ApiResponse:
        response = self.client.get_user_posts(params.username, params.cursor)
        
        
        filtered_response = {
            "items": response.get("items", []),
            "num_results": response.get("num_results", 0),
            "user": response.get("user", {}),
            "more_available": response.get("more_available", False),
            "cursor": response.get("next_max_id")
        }
        
        validated_data = PostResponse(**filtered_response)
        return self.prepare_response(validated_data, "InstagramUserPostsCard")
        
    def get_user_following(self, params: GetUserFollowingParams) -> ApiResponse:
        response = self.client.get_user_following(
            user_id=params.user_id,
            count=params.count,
            cursor=params.cursor
        )
        
        validated_data = UserListResponse(**response)
        return self.prepare_response(validated_data, "InstagramUserFollowingCard")
        
    def get_user_followers(self, params: GetUserFollowersParams) -> ApiResponse:
        response = self.client.get_user_followers(
            user_id=params.user_id,
            count=params.count,
            cursor=params.cursor
        )
        
        validated_data = UserListResponse(**response)
        return self.prepare_response(validated_data, "InstagramUserFollowersCard")
        
    def get_post_details(self, params: GetPostDetailsParams) -> ApiResponse:
        response = self.client.get_post_details(params.shortcode)

        validated_data = PostDetailData(**response)
        return self.prepare_response(validated_data, "InstagramPostDetailsCard")
        
    def get_post_comments(self, params: GetPostCommentsParams) -> ApiResponse:
        response = self.client.get_post_comments(
            pk=params.pk,
            next_min_id=params.next_min_id
        )
        
        validated_data = PostCommentsResponse(**response)
        return self.prepare_response(validated_data, "InstagramPostCommentsCard")
