import requests
import re
from typing import Dict, Any, Optional
from fastapi import HTTPException

class InstagramClient:
    BASE_URL = "https://instagram230.p.rapidapi.com"
    
    def __init__(self, api_key: str, username: Optional[str] = None):
        self.api_key = api_key
        self.username = self.parse_instagram_username(username) if username else None
        self.headers = {
            "x-rapidapi-host": "instagram230.p.rapidapi.com",
            "x-rapidapi-key": api_key
        }
    
    @staticmethod
    def parse_instagram_username(username_input: str) -> str:
        if not username_input:
            return ""
            
        instagram_format = re.match(r'^(.+)@instagram$', username_input)
        if instagram_format:
            return instagram_format.group(1)
            
        if username_input.startswith('@'):
            username_input = username_input[1:]
            
        instagram_url_pattern = r'(?:https?:\/\/)?(?:www\.)?(?:instagram\.com)\/([a-zA-Z0-9_\.]+)(?:\?.*)?$'
        url_match = re.search(instagram_url_pattern, username_input)
        
        if url_match:
            return url_match.group(1)
        
        return username_input.strip()
    
    def get_user_details(self, username: str) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/user/details"
        response = requests.get(
            url,
            headers=self.headers,
            params={"username": username}
        )
        response.raise_for_status()
        return response.json()
    
    def get_me(self) -> Dict[str, Any]:
        if not self.username:
            raise HTTPException(status_code=405, detail="Username is not set. Please provide a username during client initialization.")
        
        return self.get_user_details(username=self.username)
        
    def get_user_posts(self, username: str, cursor: Optional[str] = None) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/user/posts"
        params = {"username": username}
        if cursor:
            params["cursor"] = cursor
        
        response = requests.get(
            url,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
        
    def get_user_following(self, user_id: str, count: int = 20, cursor: Optional[str] = None) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/user/following"
        params = {
            "user_id": user_id,
            "count": count
        }
        if cursor:
            params["cursor"] = cursor
            
        response = requests.get(
            url,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
        
    def get_user_followers(self, user_id: str, count: int = 20, cursor: Optional[str] = None) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/user/followers"
        params = {
            "user_id": user_id,
            "count": count
        }
        if cursor:
            params["cursor"] = cursor
            
        response = requests.get(
            url,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
        
    def get_post_details(self, shortcode: str) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/post/details"
        params = {"shortcode": shortcode}
        
        response = requests.get(
            url,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
        
    def get_post_comments(self, pk: str, next_min_id: Optional[str] = None) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/post/comments"
        params = {"pk": pk}
        if next_min_id:
            params["next_min_id"] = next_min_id
            
        response = requests.get(
            url, 
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
