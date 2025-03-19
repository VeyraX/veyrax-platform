import requests
from typing import Dict, Any, List, Optional, Union

class LinkedInClient:
    BASE_URL = "https://linkedin-data-api.p.rapidapi.com"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "linkedin-data-api.p.rapidapi.com"
        }

    def get_profile(self, profile_id: str) -> Dict[str, Any]:
        """Get LinkedIn profile data"""
        response = requests.get(
            f"{self.BASE_URL}?username={profile_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
        
    def search_people(self, keywords: str, start: int = 0, geo: Optional[str] = None) -> Dict[str, Any]:
        """Search for people on LinkedIn"""
        url = f"{self.BASE_URL}/search-people"
        params = {
            "keywords": keywords,
            "start": start
        }
        
        if geo:
            params["geo"] = geo
            
        response = requests.get(
            url,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
        
    def get_profile_posts(self, username: str, pagination_token: Optional[str] = None) -> Dict[str, Any]:
        """Get posts from a LinkedIn profile"""
        url = f"{self.BASE_URL}/get-profile-posts"
        params = {"username": username}
        
        if pagination_token:
            params["paginationToken"] = pagination_token
            
        response = requests.get(
            url,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
        
    def get_profile_post_comments(self, urn: str, sort: str = "mostRelevant", page: int = 1) -> Dict[str, Any]:
        """Get comments for a LinkedIn post"""
        url = f"{self.BASE_URL}/get-profile-posts-comments"
        params = {
            "urn": urn,
            "sort": sort,
            "page": page
        }
            
        response = requests.get(
            url,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
        
    def get_connection_count(self, username: str) -> Dict[str, Any]:
        """Get connection count and profile information for a LinkedIn user"""
        url = f"{self.BASE_URL}/connection-count"
        params = {"username": username}
            
        response = requests.get(
            url,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
        
    def get_data_connection_count(self, username: str) -> Dict[str, Any]:
        """Get detailed connection count data for a LinkedIn user"""
        url = f"{self.BASE_URL}/data-connection-count"
        params = {"username": username}
            
        response = requests.get(
            url,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
        
    def get_company_details(self, username: str) -> Dict[str, Any]:
        """Get detailed information about a LinkedIn company"""
        url = f"{self.BASE_URL}/get-company-details"
        params = {"username": username}
            
        response = requests.get(
            url,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
        
    def search_companies(self, keyword: str = "", locations: Optional[List[int]] = None, 
                         company_sizes: Optional[List[str]] = None, has_jobs: Optional[bool] = None,
                         industries: Optional[List[int]] = None, page: int = 1) -> Dict[str, Any]:
        """Search for companies on LinkedIn"""
        url = f"{self.BASE_URL}/companies/search"
        
        # Prepare request payload
        payload = {
            "keyword": keyword,
            "page": page
        }
        
        if locations:
            payload["locations"] = locations
            
        if company_sizes:
            payload["companySizes"] = company_sizes
            
        if has_jobs is not None:
            payload["hasJobs"] = has_jobs
            
        if industries:
            payload["industries"] = industries
        
        response = requests.post(
            url,
            headers=self.headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()
        
    def get_company_jobs(self, company_ids: List[int], page: int = 1, sort: str = "mostRecent") -> Dict[str, Any]:
        """Get jobs from specified companies on LinkedIn"""
        url = f"{self.BASE_URL}/company-jobs"
        
        payload = {
            "companyIds": company_ids,
            "page": page,
            "sort": sort
        }
        
        response = requests.post(
            url,
            headers=self.headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()
        
    def get_company_posts(self, username: str, start: int = 0) -> Dict[str, Any]:
        """Get posts from a LinkedIn company"""
        url = f"{self.BASE_URL}/get-company-posts"
        params = {
            "username": username,
            "start": start
        }
        
        response = requests.get(
            url,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
        
    def get_profile_email(self, profile_url: str) -> Dict[str, Any]:
        """Get email and profile data for a LinkedIn profile URL"""
        url = f"{self.BASE_URL}/linkedin-to-email"
        params = {"url": profile_url}
        
        response = requests.get(
            url,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
        
    def get_company_employees_count(self, company_id: str, locations: List[str] = None) -> Dict[str, Any]:
        """Get employee count and distribution data for a LinkedIn company"""
        url = f"{self.BASE_URL}/get-company-employees-count"
        
        payload = {
            "companyId": company_id,
            "locations": locations or []
        }
        
        response = requests.post(
            url,
            headers=self.headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()

    def search_jobs(self, keywords: str, location_id: str, date_posted: str = "anyTime", sort: str = "mostRelevant") -> Dict[str, Any]:
        """Search for jobs on LinkedIn"""
        url = f"{self.BASE_URL}/search-jobs"
        
        params = {
            "keywords": keywords,
            "locationId": location_id,
            "datePosted": date_posted,
            "sort": sort
        }
        
        response = requests.get(
            url,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()

    def get_job_details(self, job_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific LinkedIn job"""
        url = f"{self.BASE_URL}/get-job-details"
        
        params = {
            "id": job_id
        }
        
        response = requests.get(
            url,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()

    def get_hiring_team(self, job_id: str, job_url: str) -> Dict[str, Any]:
        """Get hiring team information for a specific LinkedIn job"""
        url = f"{self.BASE_URL}/get-hiring-team"
        
        params = {
            "id": job_id,
            "url": job_url
        }
        
        response = requests.get(
            url,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()

    def search_posts(
        self,
        keyword: str = "",
        sort_by: str = "date_posted",
        date_posted: str = "",
        page: int = 1,
        content_type: str = "",
        from_member: Optional[List[str]] = None,
        from_company: Optional[List[int]] = None,
        mentions_member: Optional[List[str]] = None,
        mentions_organization: Optional[List[int]] = None,
        author_industry: Optional[List[int]] = None,
        author_company: Optional[List[int]] = None,
        author_title: str = ""
    ) -> Dict[str, Any]:
        """Search for posts on LinkedIn with various filters"""
        url = f"{self.BASE_URL}/search-posts"
        
        payload = {
            "keyword": keyword,
            "sortBy": sort_by,
            "datePosted": date_posted,
            "page": page,
            "contentType": content_type,
            "fromMember": from_member or [],
            "fromCompany": from_company or [],
            "mentionsMember": mentions_member or [],
            "mentionsOrganization": mentions_organization or [],
            "authorIndustry": author_industry or [],
            "authorCompany": author_company or [],
            "authorTitle": author_title
        }
        
        response = requests.post(
            url,
            headers=self.headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()

    def get_post(self, post_url: str) -> Dict[str, Any]:
        """Get detailed information about a specific LinkedIn post"""
        url = f"{self.BASE_URL}/get-post"
        
        params = {
            "url": post_url
        }
        
        response = requests.get(
            url,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()

    def get_article(self, article_url: str) -> Dict[str, Any]:
        """Get detailed information about a LinkedIn article"""
        url = f"{self.BASE_URL}/get-article"
        
        params = {
            "url": article_url
        }
        
        response = requests.get(
            url,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()

    def get_article_comments(self, article_url: str, page: int = 1, sort: str = "REVERSE_CHRONOLOGICAL") -> Dict[str, Any]:
        """Get comments for a LinkedIn article"""
        url = f"{self.BASE_URL}/get-article-comments"
        
        params = {
            "url": article_url,
            "page": page,
            "sort": sort
        }
        
        response = requests.get(
            url,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()