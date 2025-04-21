import requests
from typing import Dict, Any, Optional, List

class LinkedInClient:
    BASE_URL = "https://linkedin-api8.p.rapidapi.com"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "x-rapidapi-host": "linkedin-api8.p.rapidapi.com",
            "x-rapidapi-key": api_key
        }

    def get_profile(self, username: str) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/",
            headers=self.headers,
            params={"username": username}
        )
        response.raise_for_status()
        return response.json()
        
    def search_people(self, params: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/search-people",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
        
    def get_profile_posts(self, params: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/get-profile-posts",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()

    def get_connection_count(self, username: str) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/connection-count",
            headers=self.headers,
            params={"username": username}
        )
        response.raise_for_status()
        return response.json()

    def get_post_comments(self, params: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/get-post-comments",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()

    def get_similar_profiles(self, url: str) -> Dict[str, Any]:
        params = {"url": url}
        response = requests.get(
            f"{self.BASE_URL}/similar-profiles",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()

    def get_company_details(self, username: str) -> Dict[str, Any]:
        params = {"username": username}
        response = requests.get(
            f"{self.BASE_URL}/get-company-details",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()

    def search_companies(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        post_headers = self.headers.copy()
        post_headers["Content-Type"] = "application/json"
        response = requests.post(
            f"{self.BASE_URL}/companies/search",
            headers=post_headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()

    def get_company_jobs(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        post_headers = self.headers.copy()
        post_headers["Content-Type"] = "application/json"
        response = requests.post(
            f"{self.BASE_URL}/company-jobs",
            headers=post_headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()

    def get_company_posts(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        response = requests.get(
            f"{self.BASE_URL}/get-company-posts",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()

    def get_company_post_comments(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        response = requests.get(
            f"{self.BASE_URL}/get-company-post-comments",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()

    def search_posts(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        post_headers = self.headers.copy()
        post_headers["Content-Type"] = "application/json"
        response = requests.post(
            f"{self.BASE_URL}/search-posts",
            headers=post_headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()

    def get_post(self, url: str) -> Dict[str, Any]:
        params = {"url": url}
        response = requests.get(
            f"{self.BASE_URL}/get-post",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()

    def get_job_details(self, job_id: str) -> Dict[str, Any]:
        params = {"id": job_id}
        response = requests.get(
            f"{self.BASE_URL}/get-job-details",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()

    def search_jobs(self, params: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/search-jobs",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()

    def search_locations(self, keyword: str) -> Dict[str, Any]:
        params = {"keyword": keyword}
        response = requests.get(
            f"{self.BASE_URL}/search-locations",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
