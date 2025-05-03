import requests
import re
from typing import Dict, Any, Optional
from fastapi import HTTPException


class FacebookClient:
    BASE_URL = "https://facebook-scraper3.p.rapidapi.com"
    
    def __init__(self, api_key: str, profile_url: Optional[str] = None):
        self.api_key = api_key
        self.profile_url = self.parse_facebook_url(profile_url) if profile_url else None
        self.headers = {
            "x-rapidapi-host": "facebook-scraper3.p.rapidapi.com",
            "x-rapidapi-key": api_key
        }
    
    @staticmethod
    def parse_facebook_url(url_input: str) -> str:
        if not url_input:
            return ""
            
        facebook_url_pattern = r'(?:https?:\/\/)?(?:www\.|m\.)?facebook\.com\/([a-zA-Z0-9\.\-_]+)(?:\/)?(?:\?.*)?$'
        url_match = re.search(facebook_url_pattern, url_input)
        
        if url_match:
            return f"https://www.facebook.com/{url_match.group(1)}"
        
        return url_input.strip()
    
    def search_locations(self, query: str) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/search/locations"
        response = requests.get(
            url,
            headers=self.headers,
            params={"query": query}
        )
        response.raise_for_status()
        return response.json()
    
    def search_posts(self, **params) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/search/posts"
        response = requests.get(
            url,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def search_places(self, **params) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/search/places"
        response = requests.get(
            url,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
        
    def search_pages(self, **params) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/search/pages"
        response = requests.get(
            url,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
        
    def search_events(self, **params) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/search/events"
        response = requests.get(
            url,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
        
    def get_page_details(self, url: str) -> Dict[str, Any]:
        endpoint = f"{self.BASE_URL}/page/details"
        response = requests.get(
            endpoint,
            headers=self.headers,
            params={"url": url}
        )
        response.raise_for_status()
        return response.json()
        
    def get_page_id(self, url: str) -> Dict[str, Any]:
        endpoint = f"{self.BASE_URL}/page/page_id"
        response = requests.get(
            endpoint,
            headers=self.headers,
            params={"url": url}
        )
        response.raise_for_status()
        return response.json()
            
    def get_page_posts(self, **params) -> Dict[str, Any]:
        endpoint = f"{self.BASE_URL}/page/posts"
        response = requests.get(
            endpoint,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
        
    def get_page_reviews(self, **params) -> Dict[str, Any]:
        endpoint = f"{self.BASE_URL}/page/reviews"
        response = requests.get(
            endpoint,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()

    def get_post_comments(self, post_id: str, cursor: Optional[str] = None) -> Dict[str, Any]:
        endpoint = f"{self.BASE_URL}/post/comments"
        params = {"post_id": post_id}
        if cursor:
            params["cursor"] = cursor
        response = requests.get(
            endpoint,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()

    def get_post_details(self, post_id: str) -> Dict[str, Any]:
        endpoint = f"{self.BASE_URL}/post"
        params = {"post_id": post_id}
            
        response = requests.get(
            endpoint,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()

    def get_group_posts(self, group_id: str, cursor: Optional[str] = None, sorting_order: Optional[str] = None) -> Dict[str, Any]:
        endpoint = f"{self.BASE_URL}/group/posts"
        params = {"group_id": group_id}
        if cursor:
            params["cursor"] = cursor
        if sorting_order:
            params["sorting_order"] = sorting_order
            
        response = requests.get(
            endpoint,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def get_group_details(self, url: str) -> Dict[str, Any]:
        endpoint = f"{self.BASE_URL}/group/details"
        params = {"url": url}
            
        response = requests.get(
            endpoint,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def get_group_id(self, url: str) -> Dict[str, Any]:
        endpoint = f"{self.BASE_URL}/group/id"
        params = {"url": url}
            
        response = requests.get(
            endpoint,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
        
    def get_profile_posts(self, profile_id: str, cursor: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        endpoint = f"{self.BASE_URL}/profile/posts"
        params = {"profile_id": profile_id}
        if cursor:
            params["cursor"] = cursor
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
            
        response = requests.get(
            endpoint,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def get_profile_details_id(self, profile_id: str) -> Dict[str, Any]:
        endpoint = f"{self.BASE_URL}/profile/details_id"
        params = {"profile_id": profile_id}
            
        response = requests.get(
            endpoint,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def get_profile_details_url(self, url: str) -> Dict[str, Any]:
        endpoint = f"{self.BASE_URL}/profile/details_url"
        params = {"url": url}
            
        response = requests.get(
            endpoint,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def get_profile_id(self, url: str) -> Dict[str, Any]:
        endpoint = f"{self.BASE_URL}/profile/profile_id"
        params = {"url": url}
            
        response = requests.get(
            endpoint,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
        
    def get_me(self) -> Dict[str, Any]:
        if not self.profile_url:
            raise HTTPException(status_code=405, detail="Profile URL is not set. Please provide a URL during client initialization.")
        
        return self.get_profile_details_url(url=self.profile_url)
