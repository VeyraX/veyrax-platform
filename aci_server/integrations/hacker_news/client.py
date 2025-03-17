import requests
from typing import Dict, Any, List, Optional

class HackerNewsClient:
    """Client for interacting with Hacker News API"""
    
    BASE_URL = "https://hacker-news.firebaseio.com/v0"
    
    def __init__(self):
        pass
    
    def get_top_stories(self) -> List[int]:
        response = requests.get(f"{self.BASE_URL}/topstories.json")
        response.raise_for_status()
        return response.json()
    
    def get_new_stories(self) -> List[int]:
        response = requests.get(f"{self.BASE_URL}/newstories.json")
        response.raise_for_status()
        return response.json()
    
    def get_best_stories(self) -> List[int]:
        response = requests.get(f"{self.BASE_URL}/beststories.json")
        response.raise_for_status()
        return response.json()
    
    def get_ask_stories(self) -> List[int]:
        response = requests.get(f"{self.BASE_URL}/askstories.json")
        response.raise_for_status()
        return response.json()
    
    def get_show_stories(self) -> List[int]:
        """Get IDs of Show HN stories"""
        response = requests.get(f"{self.BASE_URL}/showstories.json")
        response.raise_for_status()
        return response.json()
    
    def get_job_stories(self) -> List[int]:
        """Get IDs of job stories"""
        response = requests.get(f"{self.BASE_URL}/jobstories.json")
        response.raise_for_status()
        return response.json()
    
    def get_item(self, item_id: int) -> Dict[str, Any]:
        """Get details of a specific item (story, comment, etc.)"""
        response = requests.get(f"{self.BASE_URL}/item/{item_id}.json")
        response.raise_for_status()
        return response.json()
    
    def get_user(self, username: str) -> Dict[str, Any]:
        """Get details of a specific user"""
        response = requests.get(f"{self.BASE_URL}/user/{username}.json")
        response.raise_for_status()
        return response.json()
    
    def get_items_batch(self, item_ids: List[int]) -> List[Dict[str, Any]]:
        """Get details of multiple items in batch"""
        items = []
        for item_id in item_ids:
            try:
                item = self.get_item(item_id)
                if item:
                    items.append(item)
            except requests.exceptions.RequestException:
                continue
        return items