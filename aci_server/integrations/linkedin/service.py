from typing import Dict, Any, List, Optional
import os
from .client import LinkedInClient
from .schema import (
    ApiResponse,
    GetProfileParams,
    ProfileData,
    SearchPeopleParams,
    SearchPeopleResponse,
    GetProfilePostsParams,
    ProfilePostsResponse,
    GetProfilePostCommentsParams,
    ProfilePostCommentsResponse,
    GetConnectionCountParams,
    ConnectionCountResponse,
    GetDataConnectionCountParams,
    GetCompanyDetailsParams,
    CompanyDetailsResponse,
    SearchCompaniesParams,
    SearchCompaniesResponse,
    CompanyJobsParams,
    CompanyJobsResponse,
    GetCompanyPostsParams,
    CompanyPostsResponse,
    GetProfileEmailParams,
    ProfileEmailResponse,
    GetCompanyEmployeesCountParams,
    CompanyEmployeesCountResponse,
    SearchJobsParams,
    SearchJobsResponse,
    GetJobDetailsParams,
    JobDetailsResponse,
    GetHiringTeamParams,
    HiringTeamResponse,
    SearchPostsParams,
    SearchPostsResponse,
    GetPostParams,
    GetPostResponse,
    GetArticleParams,
    GetArticleResponse,
    GetArticleCommentsParams,
    GetArticleCommentsResponse,
    SearchLocationsParams,
    SearchLocationsResponse
)
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
        """Get LinkedIn profile data"""
        username = params.username
        response = self.client.get_profile(username)
        transformed_profile = ProfileData(**response)
        return self.prepare_response(transformed_profile, None)
        
    def search_people(self, params: SearchPeopleParams) -> ApiResponse:
        """Search for people on LinkedIn"""
        response = self.client.search_people(
            keywords=params.keywords,
            start=params.start,
            geo=params.geo
        )    
        
        # Transform the raw response to match our schema
        transformed_response = {
            "success": True,
            "message": "",
            "data": {
                "total": response.get("data", {}).get("total", 0),
                "items": []
            }
        }
        
        # Transform items if they exist in the response
        items = response.get("data", {}).get("items", [])
        if items:
            transformed_response["data"]["items"] = [
                {
                    "fullName": item.get("fullName", ""),
                    "headline": item.get("headline", ""),
                    "summary": item.get("summary", ""),
                    "profilePicture": item.get("profilePicture", ""),
                    "location": item.get("location", ""),
                    "profileURL": item.get("profileURL", ""),
                    "username": item.get("username", "")
                }
                for item in items
            ]
        
        # Transform response data to match our schema
        search_response = SearchPeopleResponse(**transformed_response)
        
        return self.prepare_response(search_response, None)
        
    def get_profile_posts(self, params: GetProfilePostsParams) -> ApiResponse:
        """Get posts from a LinkedIn profile"""
        response = self.client.get_profile_posts(
            username=params.username,
            pagination_token=params.pagination_token
        )

        # Transform response data to match our schema
        posts_response = ProfilePostsResponse(**response)
        
        return self.prepare_response(posts_response, None)
        
    def get_profile_post_comments(self, params: GetProfilePostCommentsParams) -> ApiResponse:
        """Get comments for a LinkedIn post"""
        response = self.client.get_profile_post_comments(
            urn=params.urn,
            sort=params.sort,
            page=params.page
        )
        
        if response.get('data') is None:
            response['data'] = []
            
        # Transform response data to match our schema
        comments_response = ProfilePostCommentsResponse(**response)
        
        return self.prepare_response(comments_response, None)
        
    def get_connection_count(self, params: GetConnectionCountParams) -> ApiResponse:
        """Get connection count and profile information for a LinkedIn user"""
        response = self.client.get_connection_count(
            username=params.username
        )
        
        # Transform response data to match our schema
        connection_count_response = ConnectionCountResponse(**response)
        
        return self.prepare_response(connection_count_response, None)
        
    def get_data_connection_count(self, params: GetDataConnectionCountParams) -> ApiResponse:
        """Get detailed connection count data for a LinkedIn user"""
        response = self.client.get_data_connection_count(
            username=params.username
        )
        
        # Since the schema might be similar to ConnectionCountResponse, we'll use the same model
        data_connection_count_response = ConnectionCountResponse(**response)
        
        return self.prepare_response(data_connection_count_response, None)
        
    def get_company_details(self, params: GetCompanyDetailsParams) -> ApiResponse:
        """Get detailed information about a LinkedIn company"""
        response = self.client.get_company_details(
            username=params.username
        )
        
        # Transform response data to match our schema
        company_details_response = CompanyDetailsResponse(**response)
        
        return self.prepare_response(company_details_response, None)
        
    def search_companies(self, params: SearchCompaniesParams) -> ApiResponse:
        """Search for companies on LinkedIn"""
        response = self.client.search_companies(
            keyword=params.keyword,
            locations=params.locations,
            company_sizes=params.companySizes,
            has_jobs=params.hasJobs,
            industries=params.industries,
            page=params.page
        )
        
        # Transform response data to match our schema
        search_companies_response = SearchCompaniesResponse(**response)
        
        return self.prepare_response(search_companies_response, None)
        
    def get_company_jobs(self, params: CompanyJobsParams) -> ApiResponse:
        """Get jobs from specified companies on LinkedIn"""
        response = self.client.get_company_jobs(
            company_ids=params.companyIds,
            page=params.page,
            sort=params.sort
        )
        
        # Transform response data to match our schema
        company_jobs_response = CompanyJobsResponse(**response)
        
        return self.prepare_response(company_jobs_response, None)
        
    def get_company_posts(self, params: GetCompanyPostsParams) -> ApiResponse:
        """Get posts from a LinkedIn company"""
        response = self.client.get_company_posts(
            username=params.username,
            start=params.start
        )
        
        # Transform response data to match our schema
        company_posts_response = CompanyPostsResponse(**response)
        
        return self.prepare_response(company_posts_response, None)
        
    def get_profile_email(self, params: GetProfileEmailParams) -> ApiResponse:
        """Get email and profile data for a LinkedIn profile URL"""
        response = self.client.get_profile_email(
            profile_url=params.url
        )
        
        # Transform response data to match our schema
        profile_email_response = ProfileEmailResponse(**response)
        
        return self.prepare_response(profile_email_response, None)
        
    def get_company_employees_count(self, params: GetCompanyEmployeesCountParams) -> ApiResponse:
        """Get employee count and distribution data for a LinkedIn company"""
        response = self.client.get_company_employees_count(
            company_id=params.companyId,
            locations=params.locations
        )
        
        # Transform response data to match our schema
        employees_count_response = CompanyEmployeesCountResponse(**response)
        
        return self.prepare_response(employees_count_response, None)

    def search_jobs(self, params: SearchJobsParams) -> ApiResponse:

        if 'urn:li:geo:' in params.locationId:
            location_id = params.locationId.split('urn:li:geo:')[1]
        else:
            location_id = params.locationId
        
        response = self.client.search_jobs(
            keywords=params.keywords,
            location_id=location_id,
            date_posted=params.datePosted,
            sort=params.sort
        )

        if response.get('data', None) is None:
            response['data'] = []
        
        # Transform response data to match our schema
        search_jobs_response = SearchJobsResponse(**response)
        
        return self.prepare_response(search_jobs_response, None)

    def get_job_details(self, params: GetJobDetailsParams) -> ApiResponse:
        """Get detailed information about a specific LinkedIn job"""
        response = self.client.get_job_details(
            job_id=params.id
        )
        
        # Transform response data to match our schema
        job_details_response = JobDetailsResponse(**response)
        
        return self.prepare_response(job_details_response, None)

    def get_hiring_team(self, params: GetHiringTeamParams) -> ApiResponse:
        """Get hiring team information for a specific LinkedIn job"""
        response = self.client.get_hiring_team(
            job_id=params.id,
            job_url=params.url
        )
        
        # Handle case where items is None by converting to empty list
        if response.get('data', {}).get('items') is None:
            response['data']['items'] = []
        
        # Transform response data to match our schema
        hiring_team_response = HiringTeamResponse(**response)
        
        return self.prepare_response(hiring_team_response, None)

    def search_posts(self, params: SearchPostsParams) -> ApiResponse:
        """Search for posts on LinkedIn with various filters"""
        response = self.client.search_posts(
            keyword=params.keyword,
            sort_by=params.sortBy,
            date_posted=params.datePosted,
            page=params.page,
            content_type=params.contentType,
            from_member=params.fromMember,
            from_company=params.fromCompany,
            mentions_member=params.mentionsMember,
            mentions_organization=params.mentionsOrganization,
            author_industry=params.authorIndustry,
            author_company=params.authorCompany,
            author_title=params.authorTitle
        )
        
        # Transform response data to match our schema
        search_posts_response = SearchPostsResponse(**response)
        
        return self.prepare_response(search_posts_response, None)

    def get_post(self, params: GetPostParams) -> ApiResponse:
        """Get detailed information about a specific LinkedIn post"""
        response = self.client.get_post(
            post_url=params.url
        )
        
        # Transform response data to match our schema
        post_response = GetPostResponse(**response)
        
        return self.prepare_response(post_response, None)

    def get_article(self, params: GetArticleParams) -> ApiResponse:
        """Get detailed information about a LinkedIn article"""
        response = self.client.get_article(
            article_url=params.url
        )
        
        # Transform response data to match our schema
        article_response = GetArticleResponse(**response)
        
        return self.prepare_response(article_response, None)

    def get_article_comments(self, params: GetArticleCommentsParams) -> ApiResponse:
        """Get comments for a LinkedIn article"""
        response = self.client.get_article_comments(
            article_url=params.url,
            page=params.page,
            sort=params.sort
        )
        
        # Transform response data to match our schema
        article_comments_response = GetArticleCommentsResponse(**response)
        
        return self.prepare_response(article_comments_response, None)

    def search_locations(self, params: SearchLocationsParams) -> ApiResponse:
        """Search for LinkedIn locations"""
        response = self.client.search_locations(
            keyword=params.keyword
        )
        
        # Transform response data to match our schema
        locations_response = SearchLocationsResponse(**response)
        
        return self.prepare_response(locations_response, None)