from typing import Dict, Any, List, Optional
from .client import LinkedInClient
from .schema import (
    GetProfileParams,
    SearchPeopleParams,
    GetProfilePostsParams,
    GetConnectionCountParams,
    GetDataConnectionCountParams,
    GetPostCommentsParams,
    Profile,
    SearchPeopleResults,
    ProfilePost,
    GetProfilePostsResult,
    ConnectionCount,
    DataConnectionCount,
    PostComment,
    GetPostCommentsResult,
    ProfileResponse,
    SearchPeopleResponse,
    GetProfilePostsResponse,
    ConnectionCountResponse,
    DataConnectionCountResponse,
    GetPostCommentsResponse,
    PostCommentAuthor,
    ApiResponse,
    SimilarProfilesParams,
    SimilarProfilesResponse,
    GetCompanyDetailsParams,
    CompanyDetails,
    CompanyDetailsResponse,
    CompanyHeadquarter,
    SearchCompaniesParams,
    SearchCompaniesData,
    SearchCompaniesResponse,
    CompanyJobsParams,
    CompanyJobsData,
    CompanyJobsResponse,
    GetCompanyPostsParams,
    CompanyPostsList,
    GetCompanyPostCommentsParams,
    CompanyPostCommentsList,
    SortOption,
    SearchPostsParams,
    SearchPostsData,
    GetPostParams,
    GetPostData,
    GetJobDetailsParams,
    JobDetails,
    SearchJobsParams,
    JobSearchItem,
    JobSearchList,
    SearchLocationsParams,
    LocationItem,
    LocationsList
)
import os
from ..common.component_handler import load_components, prepare_components_auto

class LinkedInService:
    def __init__(self, client: LinkedInClient):
        self.client = client
        self.components_data = self._load_components()

    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
        
    def prepare_response(self, data: Any, component_name: str = None) -> ApiResponse:
        tool_name = "linkedin"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)

    def get_profile(self, params: GetProfileParams) -> ApiResponse:
        response = self.client.get_profile(params.username)
        processed_data = self._process_profile_data(response)
        validated_profile = Profile(**processed_data)
        return self.prepare_response(validated_profile)
    
    def search_people(self, params: SearchPeopleParams) -> ApiResponse:
        query_params = {k: v for k, v in params.model_dump().items() if v is not None}
        response = self.client.search_people(query_params)
        
        search_data = response.get("data", {})
        validated_results = SearchPeopleResults(
            total=search_data.get("total", 0),
            items=search_data.get("items", [])
        )
        return self.prepare_response(validated_results, "LinkedInSearchResultsCard")

    def get_profile_posts(self, params: GetProfilePostsParams) -> ApiResponse:
        query_params = {k: v for k, v in params.model_dump().items() if v is not None}
        response = self.client.get_profile_posts(query_params)

        posts_data = response.get("data", [])
        pagination_token = response.get("paginationToken")

        validated_posts = [ProfilePost(post_data=post) for post in posts_data]
        
        result = GetProfilePostsResult(
            items=validated_posts,
            paginationToken=pagination_token
        )
        return self.prepare_response(result, "LinkedInPostsCard")

    def get_connection_count(self, params: GetConnectionCountParams) -> ApiResponse:
        response = self.client.get_connection_count(params.username)
        validated_count = ConnectionCount(**response)
        return self.prepare_response(validated_count, "LinkedInConnectionCountCard")

    def get_post_comments(self, params: GetPostCommentsParams) -> ApiResponse:
        query_params = {k: v for k, v in params.model_dump().items() if v is not None}
        if 'sort' in query_params:
            query_params['sort'] = query_params['sort'].value
            
        response = self.client.get_post_comments(query_params)

        comments_data = response.get("data", [])
        
        validated_comments = []
        for comment in comments_data:
            author_data = comment.pop('author', None)
            validated_comment = PostComment(**comment)
            if author_data:
                validated_comment.author = PostCommentAuthor(author_data=author_data)
            validated_comments.append(validated_comment)

        result = GetPostCommentsResult(
            items=validated_comments,
            total=response.get("total"),
            totalPage=response.get("totalPage"),
            paginationToken=response.get("paginationToken")
        )
        return self.prepare_response(result, "LinkedInCommentsCard")

    def get_similar_profiles(self, params: SimilarProfilesParams) -> ApiResponse:
        response = self.client.get_similar_profiles(params.url)
        validated_response = SimilarProfilesResponse(**response)
        return self.prepare_response(validated_response, "LinkedInSimilarProfilesCard")

    def get_company_details(self, params: GetCompanyDetailsParams) -> ApiResponse:
        api_response = self.client.get_company_details(params.username)
        raw_data = api_response.get("data") if isinstance(api_response, dict) else None

        if not raw_data or not isinstance(raw_data, dict):
            validated_details = CompanyDetails() 
        else:
            processed_data = {
                "id": raw_data.get("id"),
                "name": raw_data.get("name"),
                "universalName": raw_data.get("universalName"),
                "linkedinUrl": raw_data.get("linkedinUrl"),
                "tagline": raw_data.get("tagline"),
                "description": raw_data.get("description"),
                "logoUrl": raw_data.get("Images", {}).get("logo"),
                "staffCount": raw_data.get("staffCount"),
                "headquarter": raw_data.get("headquarter"),
                "industries": raw_data.get("industries"),
                "specialities": raw_data.get("specialities"),
                "website": raw_data.get("website"),
                "followerCount": raw_data.get("followerCount"),
                "staffCountRange": raw_data.get("staffCountRange"),
                "fundingType": raw_data.get("fundingData", {}).get("lastFundingRound", {}).get("fundingType")
            }
            validated_details = CompanyDetails(**processed_data)
            
        return self.prepare_response(validated_details, "LinkedInCompanyCard")

    def search_companies(self, params: SearchCompaniesParams) -> ApiResponse:
        payload = params.model_dump(exclude_none=True)
        api_response = self.client.search_companies(payload)
        response_data = api_response.get("data") if isinstance(api_response, dict) else None

        if not response_data or not isinstance(response_data, dict):
            validated_data = SearchCompaniesData(items=[])
        else:
            if response_data.get('items') is None:
                response_data['items'] = []
            validated_data = SearchCompaniesData(**response_data)
        
        return self.prepare_response(validated_data, "LinkedInCompanySearchResultsCard")

    def get_company_jobs(self, params: CompanyJobsParams) -> ApiResponse:
        payload = params.model_dump(exclude_none=True)
        if 'sort' in payload and payload['sort'] is not None:
             payload['sort'] = payload['sort'].value

        api_response = self.client.get_company_jobs(payload)
        response_data = api_response.get("data") if isinstance(api_response, dict) else None
        
        if not response_data or not isinstance(response_data, dict):
            validated_data = CompanyJobsData(items=[])
        else:
            if response_data.get('items') is None:
                response_data['items'] = []
            validated_data = CompanyJobsData(**response_data)
            
        return self.prepare_response(validated_data, "LinkedInCompanyJobsCard")

    def get_company_posts(self, params: GetCompanyPostsParams) -> ApiResponse:
        query_params = params.model_dump(exclude_none=True)
        api_response = self.client.get_company_posts(query_params)
        posts_list = []
        if api_response.get("success") and isinstance(api_response.get("data"), list):
            posts_list = api_response["data"]
        else:
            pass 
            
        validated_data = CompanyPostsList(posts=posts_list)
        return self.prepare_response(validated_data, "LinkedInCompanyPostsCard")

    def get_company_post_comments(self, params: GetCompanyPostCommentsParams) -> ApiResponse:
        query_params = params.model_dump(exclude_none=True)
        if 'sort' in query_params and query_params['sort'] is not None:
            query_params['sort'] = query_params['sort'].value

        api_response = self.client.get_company_post_comments(query_params)
        comments_list = []
        if api_response.get("success") and isinstance(api_response.get("data"), list):
            comments_list = api_response["data"]
        else:
            pass

        validated_data = CompanyPostCommentsList(comments=comments_list)
        return self.prepare_response(validated_data, "LinkedInCompanyPostCommentsCard")

    def _process_profile_data(self, response: Dict[str, Any]) -> Dict[str, Any]:
        processed_data = {}
        data_to_process = response
        if isinstance(response, dict) and 'data' in response and isinstance(response['data'], dict):
             pass

        for key in Profile.__annotations__:
            if key in data_to_process:
                 processed_data[key] = data_to_process.get(key)
        
        return processed_data

    def search_posts(self, params: SearchPostsParams) -> ApiResponse:
        payload = params.model_dump(exclude_none=True)
        if 'sortBy' in payload and payload['sortBy'] is not None:
             payload['sortBy'] = payload['sortBy'].value
             
        api_response = self.client.search_posts(payload)
        response_data = api_response.get("data") if isinstance(api_response, dict) else None

        if not response_data or not isinstance(response_data, dict):
             validated_data = SearchPostsData(items=[]) 
        else:
             
             validated_data = SearchPostsData(**response_data)

        
        return self.prepare_response(validated_data, "LinkedInPostsSearchResultsCard")

    def get_post(self, params: GetPostParams) -> ApiResponse:
        api_response = self.client.get_post(params.url)
        response_data = api_response.get("data") if isinstance(api_response, dict) else None

        if not response_data or not isinstance(response_data, dict):
            validated_data = None 
        else:
            validated_data = GetPostData(**response_data)
            
        
        return self.prepare_response(validated_data, "LinkedInPostDetailsCard")

    def get_job_details(self, params: GetJobDetailsParams) -> ApiResponse:
        api_response = self.client.get_job_details(params.id)
        
        if not api_response.get("success") or not isinstance(api_response.get("data"), dict):
            validated_data = JobDetails()
        else:
            validated_data = JobDetails(**api_response.get("data", {}))
        
        return self.prepare_response(validated_data, "LinkedInJobDetailsCard")

    def search_jobs(self, params: SearchJobsParams) -> ApiResponse:
        query_params = params.model_dump(exclude_none=True)
        api_response = self.client.search_jobs(query_params)
        
        job_items = []
        total = 0
        
        if api_response.get("success") and isinstance(api_response.get("data"), list):
            job_items = [JobSearchItem(**item) for item in api_response.get("data", [])]
            total = api_response.get("total", 0)
        
        validated_data = JobSearchList(jobs=job_items, total=total)
        return self.prepare_response(validated_data, "LinkedInJobSearchResultsCard")

    def search_locations(self, params: SearchLocationsParams) -> ApiResponse:
        api_response = self.client.search_locations(params.keyword)
        
        location_items = []
        
        if api_response.get("success") and isinstance(api_response.get("data"), dict):
            items = api_response.get("data", {}).get("items", [])
            location_items = [LocationItem(**item) for item in items]
        
        validated_data = LocationsList(locations=location_items)
        return self.prepare_response(validated_data, "LinkedInLocationsCard")
