import requests
import re
from typing import Dict, Any, Optional, List
from fastapi import HTTPException


class LinkedInClient:
    BASE_URL = "https://linkedin-api8.p.rapidapi.com"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "x-rapidapi-host": "linkedin-api8.p.rapidapi.com",
            "x-rapidapi-key": api_key
        }
        self.username = None  # Store the authenticated username

    @staticmethod
    def parse_linkedin_username(username_input: str) -> str:
        """
        Parse LinkedIn username from various formats:
        - @username
        - https://www.linkedin.com/in/username
        - http://linkedin.com/in/username
        - linkedin.com/in/username
        - www.linkedin.com/in/username
        - username

        Returns the clean username without @ or URL components.
        """
        if not username_input:
            return ""
            
        # Remove leading @ if present
        if username_input.startswith('@'):
            username_input = username_input[1:]
            
        # Extract username from LinkedIn URL using regex
        linkedin_url_pattern = r'(?:https?:\/\/)?(?:www\.)?linkedin\.com\/in\/([a-zA-Z0-9\-]+)'
        url_match = re.search(linkedin_url_pattern, username_input)
        
        if url_match:
            # Return the username part from the URL
            return url_match.group(1)
        
        # If not a URL, return the input as is (should be just the username)
        return username_input.strip()

    def set_username(self, username: str):
        """Set the authenticated username for get_me calls"""
        self.username = self.parse_linkedin_username(username)

    def get_me(self) -> Dict[str, Any]:
        """Get the authenticated user's profile based on the stored username."""
        if not self.username:
            raise HTTPException(status_code=405, detail="Username is not set. Please provide a username during client initialization.")
        
        return self.get_profile(self.username)

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
