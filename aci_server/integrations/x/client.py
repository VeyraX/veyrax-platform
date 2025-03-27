import requests
from typing import Dict, Any, Optional
import os

class TwitterClient:
    BASE_URL = "https://twitter-api45.p.rapidapi.com"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "x-rapidapi-host": "twitter-api45.p.rapidapi.com",
            "x-rapidapi-key": api_key
        }
    
    def get_user_profile(self, **params) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/screenname.php"
        response = requests.get(
            url,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
        
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