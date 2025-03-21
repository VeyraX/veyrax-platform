import requests
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin

class RedditClient:
    BASE_URL = "https://oauth.reddit.com"
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "User-Agent": "Veyrax/1.0",  # Reddit требует User-Agent
            "Content-Type": "application/json"
        }

    def get_subreddit_posts(self, subreddit: str, limit: int = 25, sort: str = "hot") -> List[Dict]:
        endpoint = f"/r/{subreddit}/{sort}"
        params = {"limit": limit}
        
        response = requests.get(
            urljoin(self.BASE_URL, endpoint),
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        
        data = response.json()
        return [self._format_post(post['data']) for post in data['data']['children']]

    def create_comment(self, thing_id: str, text: str) -> Dict:
        endpoint = "/api/comment"
        data = {
            "thing_id": thing_id,
            "text": text
        }
        
        response = requests.post(
            urljoin(self.BASE_URL, endpoint),
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        
        return self._format_comment(response.json()['data'])

    def create_post(self, subreddit: str, title: str, text: Optional[str] = None,
                   url: Optional[str] = None, flair_id: Optional[str] = None) -> Dict:
        endpoint = f"/r/{subreddit}/submit"
        data = {
            "title": title,
            "kind": "self" if text else "link",
            "sr": subreddit,
            "flair_id": flair_id
        }
        
        if text:
            data["text"] = text
        if url:
            data["url"] = url
            
        response = requests.post(
            urljoin(self.BASE_URL, endpoint),
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        
        return self._format_post(response.json()['data'])

    def get_subreddit_flairs(self, subreddit: str) -> List[Dict]:
        endpoint = f"/r/{subreddit}/api/link_flair_v2"
        
        response = requests.get(
            urljoin(self.BASE_URL, endpoint),
            headers=self.headers
        )
        response.raise_for_status()
        
        return [self._format_flair(flair) for flair in response.json()]

    def get_comment(self, comment_id: str) -> Dict:
        endpoint = f"/api/info"
        params = {"id": comment_id}
        
        response = requests.get(
            urljoin(self.BASE_URL, endpoint),
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        
        data = response.json()
        if not data['data']['children']:
            raise ValueError(f"Comment {comment_id} not found")
            
        return self._format_comment(data['data']['children'][0]['data'])

    def delete_thing(self, thing_id: str) -> bool:
        endpoint = "/api/del"
        data = {"id": thing_id}
        
        response = requests.post(
            urljoin(self.BASE_URL, endpoint),
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        
        return True

    def edit_thing(self, thing_id: str, text: str) -> Dict:
        endpoint = "/api/editusertext"
        data = {
            "thing_id": thing_id,
            "text": text
        }
        
        response = requests.post(
            urljoin(self.BASE_URL, endpoint),
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        
        return self._format_comment(response.json()['data']) if thing_id.startswith('t1_') else self._format_post(response.json()['data'])

    def search(self, query: str, subreddit: Optional[str] = None, limit: int = 25) -> List[Dict]:
        endpoint = f"/r/{subreddit}/search" if subreddit else "/search"
        params = {
            "q": query,
            "limit": limit,
            "type": "link"
        }
        
        response = requests.get(
            urljoin(self.BASE_URL, endpoint),
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        
        data = response.json()
        return [self._format_post(post['data']) for post in data['data']['children']]

    def get_comments(self, post_id: str, limit: int = 25, sort: str = "top") -> List[Dict]:
        if post_id.startswith('t3_'):
            post_id = post_id[3:]
            
        endpoint = f"/comments/{post_id}"
        params = {
            "limit": limit,
            "sort": sort
        }
        
        response = requests.get(
            urljoin(self.BASE_URL, endpoint),
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        
        data = response.json()
        
        if len(data) >= 2:
            comments_data = data[1]['data']['children']
            return self._extract_comments(comments_data)
        
        return []
    
    def _extract_comments(self, comments_list) -> List[Dict]:
        result = []
        for comment in comments_list:
            if comment['kind'] == 't1': 
                result.append(self._format_comment(comment['data']))
                
                if ('replies' in comment['data'] and comment['data']['replies'] and
                    isinstance(comment['data']['replies'], dict) and 'data' in comment['data']['replies']):
                    nested_comments = comment['data']['replies']['data']['children']
                    result.extend(self._extract_comments(nested_comments))
            
        
        return result

    def _format_post(self, post_data: Dict) -> Dict:
        return {
            "id": post_data['id'],
            "title": post_data['title'],
            "author": post_data['author'],
            "subreddit": post_data['subreddit'],
            "score": post_data['score'],
            "url": post_data['url'],
            "created_utc": post_data['created_utc'],
            "num_comments": post_data['num_comments'],
            "is_self": post_data['is_self'],
            "selftext": post_data.get('selftext'),
            "permalink": post_data['permalink']
        }

    def _format_comment(self, comment_data: Dict) -> Dict:
        return {
            "id": comment_data['id'],
            "author": comment_data['author'],
            "body": comment_data['body'],
            "score": comment_data['score'],
            "created_utc": comment_data['created_utc'],
            "permalink": comment_data['permalink'],
            "parent_id": comment_data['parent_id']
        }

    def _format_flair(self, flair_data: Dict) -> Dict:
        return {
            "id": flair_data['id'],
            "text": flair_data['text'],
            "type": flair_data['type'],
            "text_color": flair_data['text_color'],
            "background_color": flair_data['background_color']
        }

    def get_user_info(self, username: str) -> Dict:
        """Get information about a Reddit user."""
        endpoint = f"/user/{username}/about"
        
        response = requests.get(
            urljoin(self.BASE_URL, endpoint),
            headers=self.headers
        )
        response.raise_for_status()
        
        return self._format_user(response.json()['data'])
    
    def vote(self, thing_id: str, direction: int) -> Dict:
        """Vote on a post or comment.
        
        Args:
            thing_id: The full name of the post/comment
            direction: 1 (upvote), -1 (downvote), 0 (clear vote)
        """
        endpoint = "/api/vote"
        data = {
            "id": thing_id,
            "dir": direction
        }
        
        response = requests.post(
            urljoin(self.BASE_URL, endpoint),
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        
        return {
            "thing_id": thing_id,
            "direction": direction,
            "success": True
        }
    
    def save_thing(self, thing_id: str) -> Dict:
        """Save a post or comment."""
        endpoint = "/api/save"
        data = {"id": thing_id}
        
        response = requests.post(
            urljoin(self.BASE_URL, endpoint),
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        
        return {
            "thing_id": thing_id,
            "success": True
        }
    
    def unsave_thing(self, thing_id: str) -> Dict:
        """Unsave a post or comment."""
        endpoint = "/api/unsave"
        data = {"id": thing_id}
        
        response = requests.post(
            urljoin(self.BASE_URL, endpoint),
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        
        return {
            "thing_id": thing_id,
            "success": True
        }
    
    def get_saved(self, limit: int = 25) -> List[Dict]:
        """Get saved posts and comments for current user."""
        endpoint = "/user/me/saved"
        params = {"limit": limit}
        
        response = requests.get(
            urljoin(self.BASE_URL, endpoint),
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        
        data = response.json()
        results = []
        
        for item in data['data']['children']:
            if item['kind'] == 't3':  # Post
                results.append(self._format_post(item['data']))
            elif item['kind'] == 't1':  # Comment
                results.append(self._format_comment(item['data']))
                
        return results
    
    def _format_user(self, user_data: Dict) -> Dict:
        """Format user data from Reddit API."""
        return {
            "id": user_data['id'],
            "name": user_data['name'],
            "created_utc": user_data['created_utc'],
            "comment_karma": user_data['comment_karma'],
            "link_karma": user_data['link_karma'],
            "is_gold": user_data.get('is_gold', False),
            "is_mod": user_data.get('is_mod', False),
            "has_verified_email": user_data.get('has_verified_email', False)
        }

    def get_my_info(self) -> Dict:
        """Get information about the currently authenticated user."""
        endpoint = "/api/v1/me"
        
        response = requests.get(
            urljoin(self.BASE_URL, endpoint),
            headers=self.headers
        )
        response.raise_for_status()
        
        return self._format_user(response.json())
