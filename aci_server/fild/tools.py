from agents import function_tool
import httpx
import os
from typing import Dict, Any, Optional, List
from .schema import (
    BraveWebSearchRequest, BraveWebSearchResponse,
    LinkedInProfileRequest, LinkedInProfileResponse,
    LinkedInSearchPeopleRequest, LinkedInSearchPeopleResponse,
    LinkedInCompanyDetailsRequest, LinkedInCompanyDetailsResponse,
    LinkedInSearchCompaniesRequest, LinkedInSearchCompaniesResponse
)


@function_tool
async def web_search(query: str) -> Dict[str, Any]:
    base_url = os.environ.get("API_URL", "https://veyraxapp.com")
    veyrax_api_key = os.environ.get("VEYRAX_API_KEY")
    headers = {"VEYRAX_API_KEY": veyrax_api_key}
    
    request_data = BraveWebSearchRequest(q=query)
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{base_url}/brave/web_search",
            headers=headers,
            json=request_data.dict()
        )
        response.raise_for_status()
        response_json = response.json()
        return BraveWebSearchResponse(**response_json).dict()

@function_tool
async def linkedin_search_people(**kwargs) -> Dict[str, Any]:
    base_url = os.environ.get("API_URL", "https://veyraxapp.com")
    veyrax_api_key = os.environ.get("VEYRAX_API_KEY")
    headers = {"VEYRAX_API_KEY": veyrax_api_key}
    
    if 'first_name' in kwargs:
        kwargs['firstName'] = kwargs.pop('first_name')
    if 'last_name' in kwargs:
        kwargs['lastName'] = kwargs.pop('last_name')
    if 'school_id' in kwargs:
        kwargs['schoolId'] = kwargs.pop('school_id')
    if 'keyword_title' in kwargs:
        kwargs['keywordTitle'] = kwargs.pop('keyword_title')
    if 'keyword_school' in kwargs:
        kwargs['keywordSchool'] = kwargs.pop('keyword_school')
    
    request_data = LinkedInSearchPeopleRequest(**kwargs)
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{base_url}/linkedin/search_people",
            headers=headers,
            json=request_data.dict(exclude_none=True)
        )
        response.raise_for_status()
        response_json = response.json()
        return LinkedInSearchPeopleResponse(**response_json).dict()


@function_tool
async def linkedin_get_profile(username: Optional[str] = None) -> Dict[str, Any]:
    base_url = os.environ.get("API_URL", "https://veyraxapp.com")
    veyrax_api_key = os.environ.get("VEYRAX_API_KEY")
    headers = {"VEYRAX_API_KEY": veyrax_api_key}
    
    request_data = LinkedInProfileRequest(username=username)
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{base_url}/linkedin/get_profile",
            headers=headers,
            json=request_data.dict(exclude_none=True)
        )
        response.raise_for_status()
        response_json = response.json()
        return LinkedInProfileResponse(**response_json).dict()


@function_tool
async def linkedin_get_company_details(username: Optional[str] = None) -> Dict[str, Any]:
    base_url = os.environ.get("API_URL", "https://veyraxapp.com")
    veyrax_api_key = os.environ.get("VEYRAX_API_KEY")
    headers = {"VEYRAX_API_KEY": veyrax_api_key}
    
    request_data = LinkedInCompanyDetailsRequest(username=username)
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{base_url}/linkedin/get_company_details",
            headers=headers,
            json=request_data.dict(exclude_none=True)
        )
        response.raise_for_status()
        response_json = response.json()
        return LinkedInCompanyDetailsResponse(**response_json).dict()


@function_tool
async def linkedin_search_companies(**kwargs) -> Dict[str, Any]:
    base_url = os.environ.get("API_URL", "https://veyraxapp.com")
    veyrax_api_key = os.environ.get("VEYRAX_API_KEY")
    headers = {"VEYRAX_API_KEY": veyrax_api_key}
    
    if 'company_sizes' in kwargs:
        kwargs['companySizes'] = kwargs.pop('company_sizes')
    if 'has_jobs' in kwargs:
        kwargs['hasJobs'] = kwargs.pop('has_jobs')
    
    request_data = LinkedInSearchCompaniesRequest(**kwargs)
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{base_url}/linkedin/search_companies",
            headers=headers,
            json=request_data.dict(exclude_none=True)
        )
        response.raise_for_status()
        response_json = response.json()
        return LinkedInSearchCompaniesResponse(**response_json).dict()

