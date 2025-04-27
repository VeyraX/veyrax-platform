import requests
import re
from typing import Dict, Any, Optional
from fastapi import HTTPException


class TwitterClient:
    BASE_URL = "https://twitter-api45.p.rapidapi.com"
    
    def __init__(self, api_key: str, username: Optional[str] = None):
        self.api_key = api_key
        self.username = self.parse_twitter_username(username) if username else None
        self.headers = {
            "x-rapidapi-host": "twitter-api45.p.rapidapi.com",
            "x-rapidapi-key": api_key
        }
    
    @staticmethod
    def parse_twitter_username(username_input: str) -> str:
        """
        Parse Twitter/X username from various formats:
        - @username
        - https://twitter.com/username
        - http://twitter.com/username
        - https://x.com/username
        - http://x.com/username
        - twitter.com/username
        - x.com/username
        - mobile.twitter.com/username
        - username

        Returns the clean username without @ or URL components.
        """
        if not username_input:
            return ""
            
        # Remove leading @ if present
        if username_input.startswith('@'):
            username_input = username_input[1:]
            
        # Extract username from Twitter/X URL using regex
        # This handles both twitter.com and x.com domains
        twitter_url_pattern = r'(?:https?:\/\/)?(?:www\.|mobile\.)?(?:twitter\.com|x\.com)\/([a-zA-Z0-9_]+)(?:\?.*)?$'
        url_match = re.search(twitter_url_pattern, username_input)
        
        if url_match:
            # Return the username part from the URL
            return url_match.group(1)
        
        # If not a URL, return the input as is (should be just the username)
        return username_input.strip()
    
    def get_user_profile(self, **params) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/screenname.php"
        response = requests.get(
            url,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def get_me(self) -> Dict[str, Any]:
        """Get the authenticated user's profile based on the stored username."""
        if not self.username:
            raise HTTPException(status_code=405, detail="Username is not set. Please provide a username during client initialization.")
        
        # Use the get_user_profile method with the stored username
        return self.get_user_profile(screenname=self.username)
        
    def get_user_timeline(self, **params) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/timeline.php"
        response = requests.get(
            url,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
        
    def get_user_following(self, **params) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/following.php"
        response = requests.get(
            url,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
        
    def get_user_followers(self, **params) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/followers.php"
        response = requests.get(
            url,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
        
    def get_tweet(self, **params) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/tweet.php"
        response = requests.get(
            url,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
        
    def get_tweet_retweets(self, **params) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/retweets.php"
        response = requests.get(
            url,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
        
    def search_tweets(self, **params) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/search.php"
        response = requests.get(
            url,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
        
    def get_tweet_thread(self, **params) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/tweet_thread.php"
        response = requests.get(
            url,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
        
    def get_latest_replies(self, **params) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/latest_replies.php"
        response = requests.get(
            url,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
        
    def get_list_timeline(self, **params) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/listtimeline.php"
        response = requests.get(
            url,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
        
    def get_community_timeline(self, **params) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/community_timeline.php"
        response = requests.get(
            url,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
        
    def get_list_followers(self, **params) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/list_followers.php"
        response = requests.get(
            url,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
        
    def get_list_members(self, **params) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/list_members.php"
        response = requests.get(
            url,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
        
    def get_space(self, **params) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/spaces.php"
        response = requests.get(
            url,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json() 