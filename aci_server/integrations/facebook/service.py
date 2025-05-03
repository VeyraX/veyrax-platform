from typing import Dict, Any, List, Optional
import os
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
    LocationList,
    PostList,
    PlaceList,
    PageList,
    EventList,
    PageDetailsContainer,
    PageIdResult,
    ReviewList,
    CommentList,
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
    PostDetailsContainer,
    GetGroupPostsParams,
    GetGroupDetailsParams,
    GetGroupIdParams,
    GroupPostList,
    GroupDetailsContainer,
    GroupIdResult,
    GetGroupPostsResponse,
    GetGroupDetailsResponse,
    GetGroupIdResponse,
    GetProfilePostsParams,
    GetProfileDetailsIdParams,
    GetProfileDetailsUrlParams,
    GetProfileIdParams,
    ProfilePostList,
    ProfileDetailsContainer,
    ProfileIdResult,
    GetProfilePostsResponse,
    GetProfileDetailsResponse,
    GetProfileIdResponse,
    GetMeParams,
    GetMeResponse
)
from ..common.component_handler import load_components, prepare_components_auto
from fastapi import HTTPException


class FacebookService:
    def __init__(self, client: FacebookClient):
        self.client = client
        self.components_data = self._load_components()
    
    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
    
    def prepare_response(self, data: Any, component_name: str = None) -> ApiResponse:
        tool_name = "facebook"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)
    
    def search_locations(self, params: SearchLocationsParams) -> ApiResponse:
        response = self.client.search_locations(params.query)
        validated_data = LocationList(**response)
        return self.prepare_response(validated_data, "FacebookLocationsCard")
    
    def search_posts(self, params: SearchPostsParams) -> ApiResponse:
        query_params = params.model_dump(exclude_none=True)
        response = self.client.search_posts(**query_params)
        validated_data = PostList(**response)
        return self.prepare_response(validated_data, "FacebookPostsCard")
    
    def search_places(self, params: SearchPlacesParams) -> ApiResponse:
        query_params = params.model_dump(exclude_none=True)
        response = self.client.search_places(**query_params)
        validated_data = PlaceList(**response)
        return self.prepare_response(validated_data, "FacebookPlacesCard")
        
    def search_pages(self, params: SearchPagesParams) -> ApiResponse:
        query_params = params.model_dump(exclude_none=True)
        response = self.client.search_pages(**query_params)
        validated_data = PageList(**response)
        return self.prepare_response(validated_data, "FacebookPagesCard")
        
    def search_events(self, params: SearchEventsParams) -> ApiResponse:
        query_params = params.model_dump(exclude_none=True)
        response = self.client.search_events(**query_params)
        validated_data = EventList(**response)
        return self.prepare_response(validated_data, "FacebookEventsCard")
        
    def get_page_details(self, params: GetPageDetailsParams) -> ApiResponse:
        response = self.client.get_page_details(params.url)
        validated_data = PageDetailsContainer(**response)
        return self.prepare_response(validated_data, "FacebookPageDetailsCard")
        
    def get_page_id(self, params: GetPageIdParams) -> ApiResponse:
        response = self.client.get_page_id(params.url)
        validated_data = PageIdResult(**response)
        return self.prepare_response(validated_data, "FacebookPageIdCard")
        
    def get_page_posts(self, params: GetPagePostsParams) -> ApiResponse:
        query_params = params.model_dump(exclude_none=True)
        response = self.client.get_page_posts(**query_params)

        if 'results' in response and isinstance(response['results'], list):
            for post in response['results']:
                if isinstance(post.get('video'), str):
                    post['video'] = {'uri': post['video']}
                if isinstance(post.get('video_thumbnail'), str):
                    post['video_thumbnail'] = {'uri': post['video_thumbnail']}

        validated_data = PostList(**response)
        return self.prepare_response(validated_data, "FacebookPagePostsCard")

    def get_page_reviews(self, params: GetPageReviewsParams) -> ApiResponse:
        query_params = params.model_dump(exclude_none=True)
        response = self.client.get_page_reviews(**query_params)
        validated_data = ReviewList(**response)
        return self.prepare_response(validated_data, "FacebookPageReviewsCard")

    def get_post_comments(self, params: GetPostCommentsParams) -> ApiResponse:
        query_params = params.model_dump(exclude_none=True)
        response = self.client.get_post_comments(**query_params)
        validated_data = CommentList(**response)
        return self.prepare_response(validated_data, "FacebookPostCommentsCard")

    def get_post_details(self, params: GetPostDetailsParams) -> ApiResponse:
        response = self.client.get_post_details(post_id=params.post_id)
        validated_data = PostDetailsContainer(**response)
        return self.prepare_response(validated_data, "FacebookPostDetailsCard")
        
    def get_group_posts(self, params: GetGroupPostsParams) -> ApiResponse:
        query_params = params.model_dump(exclude_none=True)
        response = self.client.get_group_posts(**query_params)
        
        if 'posts' in response and isinstance(response['posts'], list):
            for post in response['posts']:
                if isinstance(post.get('video'), str):
                    post['video'] = {'uri': post['video']}
                if isinstance(post.get('video_thumbnail'), str):
                    post['video_thumbnail'] = {'uri': post['video_thumbnail']}
        
        validated_data = GroupPostList(**response)
        return self.prepare_response(validated_data, "FacebookGroupPostsCard")
        
    def get_group_details(self, params: GetGroupDetailsParams) -> ApiResponse:
        response = self.client.get_group_details(url=params.url)
        validated_data = GroupDetailsContainer(**response)
        return self.prepare_response(validated_data, "FacebookGroupDetailsCard")
        
    def get_group_id(self, params: GetGroupIdParams) -> ApiResponse:
        response = self.client.get_group_id(url=params.url)
        validated_data = GroupIdResult(**response)
        return self.prepare_response(validated_data, "FacebookGroupIdCard")
        
    def get_profile_posts(self, params: GetProfilePostsParams) -> ApiResponse:
        query_params = params.model_dump(exclude_none=True)
        response = self.client.get_profile_posts(**query_params)
        
        if 'results' in response and isinstance(response['results'], list):
            for post in response['results']:
                if isinstance(post.get('video'), str):
                    post['video'] = {'uri': post['video']}
                if isinstance(post.get('video_thumbnail'), str):
                    post['video_thumbnail'] = {'uri': post['video_thumbnail']}
        
        validated_data = ProfilePostList(**response)
        return self.prepare_response(validated_data, "FacebookProfilePostsCard")
        
    def get_profile_details_id(self, params: GetProfileDetailsIdParams) -> ApiResponse:
        response = self.client.get_profile_details_id(profile_id=params.profile_id)
        validated_data = ProfileDetailsContainer(**response)
        return self.prepare_response(validated_data, "FacebookProfileDetailsCard")
        
    def get_profile_details_url(self, params: GetProfileDetailsUrlParams) -> ApiResponse:
        response = self.client.get_profile_details_url(url=params.url)
        validated_data = ProfileDetailsContainer(**response)
        return self.prepare_response(validated_data, "FacebookProfileDetailsCard")
        
    def get_profile_id(self, params: GetProfileIdParams) -> ApiResponse:
        response = self.client.get_profile_id(url=params.url)
        validated_data = ProfileIdResult(**response)
        return self.prepare_response(validated_data, "FacebookProfileIdCard")
        
    def get_me(self, params: GetMeParams) -> ApiResponse:
        if not self.client.profile_url:
            raise HTTPException(status_code=405, detail="Profile URL is not set. Please authenticate with a valid Facebook profile URL.")
        
        response = self.client.get_me()
        
        validated_data = ProfileDetailsContainer(**response)
        
        return self.prepare_response(validated_data, "FacebookProfileDetailsCard")
