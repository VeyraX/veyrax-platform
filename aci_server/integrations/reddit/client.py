import requests
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin

class RedditClient:
    BASE_URL = "https://oauth.reddit.com"
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "User-Agent": "Veyrax/1.0",
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

    def create_comment(self, parent_id: str, text: str) -> Dict:
        endpoint = "/api/comment"
        
        headers = dict(self.headers)
        if 'Content-Type' in headers:
            del headers['Content-Type']
        
        form_data = {
            "thing_id": parent_id, 
            "text": text,
            "api_type": "json"
        }
        
        response = requests.post(
            urljoin(self.BASE_URL, endpoint),
            headers=headers,
            data=form_data
        )
        response.raise_for_status()
        
        return self._format_comment(response.json()['json']['data']['things'][0]['data'])

    def create_post(self, subreddit: str, title: str, text: Optional[str] = None,
                   url: Optional[str] = None, flair_id: Optional[str] = None) -> Dict:
        endpoint = "/api/submit"
        
        headers = dict(self.headers)
        if 'Content-Type' in headers:
            del headers['Content-Type']
        
        form_data = {
            "sr": subreddit,
            "title": title,
            "kind": "self" if text else "link",
            "api_type": "json"
        }
        
        if text:
            form_data["text"] = text
        if url:
            form_data["url"] = url
        if flair_id:
            form_data["flair_id"] = flair_id
        
        response = requests.post(
            urljoin(self.BASE_URL, endpoint),
            headers=headers,
            data=form_data
        )
        response.raise_for_status()
    
        return response.json()

    def get_comment(self, comment_id: str) -> Dict:
        if not comment_id.startswith('t1_'):
            comment_id = f"t1_{comment_id}"
        
        endpoint = f"/api/info"
        params = {"id": comment_id, "raw_json": 1}
        
        headers = dict(self.headers)
        if 'Content-Type' in headers:
            del headers['Content-Type']
        
        response = requests.get(
            urljoin(self.BASE_URL, endpoint),
            headers=headers,
            params=params
        )
        response.raise_for_status()
        
        data = response.json()
        if not data['data']['children'] or len(data['data']['children']) == 0:
            raise ValueError(f"Comment {comment_id} not found")
        
        return self._format_comment(data['data']['children'][0]['data'])

    def delete_post(self, post_id: str) -> bool:
        thing_id = f"t3_{post_id}" if not post_id.startswith('t3_') else post_id
        endpoint = "/api/del"
        
        headers = dict(self.headers)
        if 'Content-Type' in headers:
            del headers['Content-Type']
        
        form_data = {"id": thing_id}
        
        response = requests.post(
            urljoin(self.BASE_URL, endpoint),
            headers=headers,
            data=form_data 
        )
        response.raise_for_status()
        
        return True

    def delete_comment(self, comment_id: str) -> bool:
        thing_id = f"t1_{comment_id}" if not comment_id.startswith('t1_') else comment_id
        endpoint = "/api/del"
        
        headers = dict(self.headers)
        if 'Content-Type' in headers:
            del headers['Content-Type']
        
        form_data = {"id": thing_id}
        
        response = requests.post(
            urljoin(self.BASE_URL, endpoint),
            headers=headers,
            data=form_data 
        )
        response.raise_for_status()
        
        return True

    def edit_post(self, post_id: str, text: str) -> Dict:
        thing_id = f"t3_{post_id}" if not post_id.startswith('t3_') else post_id
        endpoint = "/api/editusertext"
        
        headers = dict(self.headers)
        if 'Content-Type' in headers:
            del headers['Content-Type']
        
        form_data = {
            "thing_id": thing_id,
            "text": text,
            "api_type": "json"
        }
        
        response = requests.post(
            urljoin(self.BASE_URL, endpoint),
            headers=headers,
            data=form_data 
        )
        response.raise_for_status()
        post_id_clean = post_id.replace('t3_', '')
        post_endpoint = f"/api/info"
        params = {"id": f"t3_{post_id_clean}"}
        
        post_response = requests.get(
            urljoin(self.BASE_URL, post_endpoint),
            headers=self.headers,
            params=params
        )
        post_response.raise_for_status()
        
        post_data = post_response.json()
        return self._format_post(post_data['data']['children'][0]['data'])

    def edit_comment(self, comment_id: str, text: str) -> Dict:
        thing_id = f"t1_{comment_id}" if not comment_id.startswith('t1_') else comment_id
        endpoint = "/api/editusertext"
        
        headers = dict(self.headers)
        if 'Content-Type' in headers:
            del headers['Content-Type']
        
        form_data = {
            "thing_id": thing_id,
            "text": text,
            "api_type": "json"
        }
        
        response = requests.post(
            urljoin(self.BASE_URL, endpoint),
            headers=headers,
            data=form_data 
        )
        response.raise_for_status()
        
        comment_id_clean = comment_id.replace('t1_', '')
        comment_endpoint = f"/api/info"
        params = {"id": f"t1_{comment_id_clean}"}
        
        comment_response = requests.get(
            urljoin(self.BASE_URL, comment_endpoint),
            headers=self.headers,
            params=params
        )
        comment_response.raise_for_status()
        
        comment_data = comment_response.json()
        return self._format_comment(comment_data['data']['children'][0]['data'])

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

    def get_user_info(self, username: str) -> Dict:
        endpoint = f"/user/{username}/about"
        
        response = requests.get(
            urljoin(self.BASE_URL, endpoint),
            headers=self.headers
        )
        response.raise_for_status()
        
        return self._format_user(response.json()['data'])
    
    def vote_post(self, post_id: str, direction: int) -> Dict:
        endpoint = "/api/vote"
        
        thing_id = f"t3_{post_id}" if not post_id.startswith('t3_') else post_id
        
        headers = dict(self.headers)
        if 'Content-Type' in headers:
            del headers['Content-Type']
        
        form_data = {
            "id": thing_id,
            "dir": direction
        }
        
        response = requests.post(
            urljoin(self.BASE_URL, endpoint),
            headers=headers,
            data=form_data
        )
        
        response.raise_for_status()
        
        return {
            "post_id": post_id,
            "direction": direction,
            "success": True
        }

    def vote_comment(self, comment_id: str, direction: int) -> Dict:
        endpoint = "/api/vote"
        
        thing_id = f"t1_{comment_id}" if not comment_id.startswith('t1_') else comment_id
        
        headers = dict(self.headers)
        if 'Content-Type' in headers:
            del headers['Content-Type']
        
        form_data = {
            "id": thing_id,
            "dir": direction
        }
        
        response = requests.post(
            urljoin(self.BASE_URL, endpoint),
            headers=headers,
            data=form_data
        )
        
        response.raise_for_status()
        
        return {
            "comment_id": comment_id,
            "direction": direction,
            "success": True
        }

    def save_post(self, post_id: str) -> Dict:
        thing_id = f"t3_{post_id}" if not post_id.startswith('t3_') else post_id
        endpoint = "/api/save"
        
        headers = dict(self.headers)
        if 'Content-Type' in headers:
            del headers['Content-Type']
        
        form_data = {"id": thing_id}
        
        response = requests.post(
            urljoin(self.BASE_URL, endpoint),
            headers=headers,
            data=form_data
        )
        response.raise_for_status()
        
        return {
            "post_id": post_id,
            "success": True
        }

    def save_comment(self, comment_id: str) -> Dict:
        thing_id = f"t1_{comment_id}" if not comment_id.startswith('t1_') else comment_id
        endpoint = "/api/save"
        
        headers = dict(self.headers)
        if 'Content-Type' in headers:
            del headers['Content-Type']
        
        form_data = {"id": thing_id}
        
        response = requests.post(
            urljoin(self.BASE_URL, endpoint),
            headers=headers,
            data=form_data
        )
        response.raise_for_status()
        
        return {
            "comment_id": comment_id,
            "success": True
        }

    def unsave_post(self, post_id: str) -> Dict:
        """Unsave a post."""
        thing_id = f"t3_{post_id}" if not post_id.startswith('t3_') else post_id
        endpoint = "/api/unsave"
        
        headers = dict(self.headers)
        if 'Content-Type' in headers:
            del headers['Content-Type']
        
        form_data = {"id": thing_id}
        
        response = requests.post(
            urljoin(self.BASE_URL, endpoint),
            headers=headers,
            data=form_data 
        )
        response.raise_for_status()
        
        return {
            "post_id": post_id,
            "success": True
        }

    def unsave_comment(self, comment_id: str) -> Dict:
        thing_id = f"t1_{comment_id}" if not comment_id.startswith('t1_') else comment_id
        endpoint = "/api/unsave"
        
        headers = dict(self.headers)
        if 'Content-Type' in headers:
            del headers['Content-Type']
        
        form_data = {"id": thing_id}
        
        response = requests.post(
            urljoin(self.BASE_URL, endpoint),
            headers=headers,
            data=form_data
        )
        response.raise_for_status()
        
        return {
            "comment_id": comment_id,
            "success": True
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

    def get_my_subreddits(self, limit: int = 100, after: Optional[str] = None) -> List[Dict]:
        endpoint = "/subreddits/mine/subscriber"
        params = {
            "limit": min(limit, 100)
        }
        
        if after:
            params["after"] = after
            
        response = requests.get(
            urljoin(self.BASE_URL, endpoint),
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        
        data = response.json()
        subreddits = [self._format_subreddit(sub['data']) for sub in data['data']['children']]
        
        if 'after' in data['data'] and data['data']['after'] and limit > 100:
            next_after = data['data']['after']
            next_limit = limit - 100
            more_subreddits = self.get_my_subreddits(next_limit, next_after)
            subreddits.extend(more_subreddits)
            
        return subreddits
    
    def _format_subreddit(self, subreddit_data: Dict) -> Dict:
        return {
            "id": subreddit_data.get('id', ''),
            "display_name": subreddit_data.get('display_name', ''),
            "name": subreddit_data.get('name', ''),
            "title": subreddit_data.get('title', ''),
            "description": subreddit_data.get('public_description', ''),
            "subscribers": subreddit_data.get('subscribers', 0),
            "created_utc": subreddit_data.get('created_utc', 0),
            "url": subreddit_data.get('url', ''),
            "over18": subreddit_data.get('over18', False),
            "community_icon": subreddit_data.get('community_icon', ''),
            "banner_img": subreddit_data.get('banner_img', ''),
            "header_img": subreddit_data.get('header_img', ''),
            "icon_img": subreddit_data.get('icon_img', '')
        }

    def _format_user(self, user_data: Dict) -> Dict:
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

    def get_link_flairs(self, subreddit: str) -> List[Dict]:
        endpoint = f"/r/{subreddit}/api/link_flair_v2"
        
        headers = dict(self.headers)
        if "Content-Type" in headers:
            del headers["Content-Type"]
        
        response = requests.get(
            urljoin(self.BASE_URL, endpoint),
            headers=headers
        )
        
        response.raise_for_status()
        return response.json()
