from typing import Dict, Any, List, Optional
from .client import RedditClient
from .schema import (
    PostList, CommentList, FlairList, RedditPost, RedditComment, 
    ActionResponse, ApiResponse, RedditUser, VoteResponse, SaveResponse,
    SavedItemsList
)
import os
from ..common.component_handler import load_components, prepare_components_auto

class RedditService:
    def __init__(self, client: RedditClient):
        self.client = client
        self.components_data = self._load_components()

    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)

    def prepare_response(self, data: Any, component_name: str = None) -> ApiResponse:
        tool_name = "reddit"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)

    def get_subreddit_posts(self, subreddit: str, limit: int = 25, sort: str = "hot") -> ApiResponse:
        posts = self.client.get_subreddit_posts(subreddit, limit, sort)
        data = PostList(posts=[RedditPost(**post) for post in posts])
        return self.prepare_response(data, "RedditPostList")

    def create_comment(self, thing_id: str, text: str) -> ApiResponse:
        comment = self.client.create_comment(thing_id, text)
        data = RedditComment(**comment)
        return self.prepare_response(data, "RedditComment")

    def create_post(self, subreddit: str, title: str, text: Optional[str] = None,
                   url: Optional[str] = None, flair_id: Optional[str] = None) -> ApiResponse:
        post = self.client.create_post(subreddit, title, text, url, flair_id)
        data = RedditPost(**post)
        return self.prepare_response(data, "RedditPost")

    def get_subreddit_flairs(self, subreddit: str) -> ApiResponse:
        flairs = self.client.get_subreddit_flairs(subreddit)
        data = FlairList(flairs=flairs)
        return self.prepare_response(data, "RedditFlairList")

    def get_comment(self, comment_id: str) -> ApiResponse:
        comment = self.client.get_comment(comment_id)
        data = RedditComment(**comment)
        return self.prepare_response(data, "RedditComment")

    def delete_thing(self, thing_id: str) -> ApiResponse:
        success = self.client.delete_thing(thing_id)
        data = ActionResponse(success=success, message="Successfully deleted" if success else "Failed to delete")
        return self.prepare_response(data, "RedditAction")

    def edit_thing(self, thing_id: str, text: str) -> ApiResponse:
        edited = self.client.edit_thing(thing_id, text)
        if thing_id.startswith('t1_'):
            data = RedditComment(**edited)
        else:
            data = RedditPost(**edited)
        return self.prepare_response(data, "RedditEdit")

    def search(self, query: str, subreddit: Optional[str] = None, limit: int = 25) -> ApiResponse:
        results = self.client.search(query, subreddit, limit)
        data = PostList(posts=[RedditPost(**post) for post in results])
        return self.prepare_response(data, "RedditSearchResults")

    def get_comments(self, post_id: str, limit: int = 25, sort: str = "top") -> ApiResponse:
        comments = self.client.get_comments(post_id, limit, sort)
        data = CommentList(comments=[RedditComment(**comment) for comment in comments])
        return self.prepare_response(data, "RedditCommentList")

    def delete_post(self, post_id: str) -> ApiResponse:
        success = self.client.delete_post(post_id)
        data = ActionResponse(success=success, message="Post successfully deleted" if success else "Failed to delete post")
        return self.prepare_response(data, "RedditAction")

    def delete_comment(self, comment_id: str) -> ApiResponse:
        success = self.client.delete_comment(comment_id)
        data = ActionResponse(success=success, message="Comment successfully deleted" if success else "Failed to delete comment")
        return self.prepare_response(data, "RedditAction")

    def edit_post(self, post_id: str, text: str) -> ApiResponse:
        edited = self.client.edit_post(post_id, text)
        data = RedditPost(**edited)
        return self.prepare_response(data, "RedditPost")

    def edit_comment(self, comment_id: str, text: str) -> ApiResponse:
        edited = self.client.edit_comment(comment_id, text)
        data = RedditComment(**edited)
        return self.prepare_response(data, "RedditComment")

    def get_user_info(self, username: str) -> ApiResponse:
        """Get information about a Reddit user."""
        user_data = self.client.get_user_info(username)
        data = RedditUser(**user_data)
        return self.prepare_response(data, "RedditUserProfile")
    
    def vote(self, thing_id: str, direction: int) -> ApiResponse:
        """Vote on a post or comment."""
        result = self.client.vote(thing_id, direction)
        action_text = {1: "upvoted", -1: "downvoted", 0: "vote cleared"}
        message = f"Successfully {action_text[direction]} item"
        data = VoteResponse(success=result['success'], thing_id=result['thing_id'], 
                          direction=result['direction'], message=message)
        return self.prepare_response(data, "RedditAction")
    
    def save_thing(self, thing_id: str) -> ApiResponse:
        """Save a post or comment."""
        result = self.client.save_thing(thing_id)
        data = SaveResponse(success=result['success'], thing_id=result['thing_id'], 
                          message="Item successfully saved")
        return self.prepare_response(data, "RedditAction")
    
    def unsave_thing(self, thing_id: str) -> ApiResponse:
        """Unsave a post or comment."""
        result = self.client.unsave_thing(thing_id)
        data = SaveResponse(success=result['success'], thing_id=result['thing_id'], 
                          message="Item successfully unsaved")
        return self.prepare_response(data, "RedditAction")
    
    def get_saved(self, limit: int = 25) -> ApiResponse:
        """Get saved posts and comments for current user."""
        items = self.client.get_saved(limit)
        
        processed_items = []
        for item in items:
            if 'selftext' in item:  
                processed_items.append(RedditPost(**item))
            else:  
                processed_items.append(RedditComment(**item))
                
        data = SavedItemsList(items=processed_items)
        return self.prepare_response(data, "RedditSavedList")

    def get_my_info(self) -> ApiResponse:
        """Get information about the currently authenticated user."""
        user_data = self.client.get_my_info()
        data = RedditUser(**user_data)
        return self.prepare_response(data, "RedditUserProfile")
