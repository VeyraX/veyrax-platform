from typing import Dict, Any, List, Optional
from .client import RedditClient
from .schema import (
    PostList, CommentList, RedditPost, RedditComment, 
    ActionResponse, ApiResponse, RedditUser, VoteResponse, SaveResponse,
    SubredditList, Subreddit, FlairList
)
import os
from ..common.component_handler import load_components, prepare_components_auto
import requests

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

    def create_comment(self, parent_id: str, text: str) -> ApiResponse:
        comment = self.client.create_comment(parent_id, text)
        data = RedditComment(**comment)
        return self.prepare_response(data, "RedditComment")

    def create_post(self, subreddit: str, title: str, text: Optional[str] = None,
                   url: Optional[str] = None, flair_id: Optional[str] = None) -> ApiResponse:
        raw_response = self.client.create_post(subreddit, title, text, url, flair_id)
        
        response_data = raw_response.get('json', {})
        
        post_data = response_data.get('data', {})
        data = RedditPost(
            id=post_data.get('id', 'unknown'),
            title=title,
            author="me",
            subreddit=subreddit,
            score=0,
            url=post_data.get('url', url or f"https://reddit.com/r/{subreddit}"),
            created_utc=post_data.get('created_utc', 0.0),
            num_comments=0,
            is_self=text is not None,
            selftext=text or "",
            permalink=post_data.get('permalink', f"/r/{subreddit}")
        )
        
        return self.prepare_response(data, "RedditPost")

    def get_comment(self, comment_id: str) -> ApiResponse:
        comment = self.client.get_comment(comment_id)
        data = RedditComment(**comment)
        return self.prepare_response(data, "RedditComment")

    def delete_post(self, post_id: str) -> ApiResponse:
        success = self.client.delete_post(post_id)
        data = ActionResponse(success=success, message="Post successfully deleted" if success else "Failed to delete post")
        return self.prepare_response(data, "RedditDeletePost")

    def delete_comment(self, comment_id: str) -> ApiResponse:
        success = self.client.delete_comment(comment_id)
        data = ActionResponse(success=success, message="Comment successfully deleted" if success else "Failed to delete comment")
        return self.prepare_response(data, "RedditDeleteComment")

    def edit_post(self, post_id: str, text: str) -> ApiResponse:
        post_data = self.client.edit_post(post_id, text)
        data = RedditPost(**post_data)
        return self.prepare_response(data, "RedditPost")

    def edit_comment(self, comment_id: str, text: str) -> ApiResponse:
        edited = self.client.edit_comment(comment_id, text)
        data = RedditComment(**edited)
        return self.prepare_response(data, "RedditEditComment")

    def get_user_info(self, username: str) -> ApiResponse:
        """Get information about a Reddit user."""
        user_data = self.client.get_user_info(username)
        data = RedditUser(**user_data)
        return self.prepare_response(data, "RedditUserProfile")
    
    def search(self, query: str, subreddit: Optional[str] = None, limit: int = 25) -> ApiResponse:
        results = self.client.search(query, subreddit, limit)
        data = PostList(posts=[RedditPost(**post) for post in results])
        return self.prepare_response(data, "RedditSearchResults")

    def get_comments(self, post_id: str, limit: int = 25, sort: str = "top") -> ApiResponse:
        comments = self.client.get_comments(post_id, limit, sort)
        data = CommentList(comments=[RedditComment(**comment) for comment in comments])
        return self.prepare_response(data, "RedditCommentList")

    def get_my_info(self) -> ApiResponse:
        """Get information about the currently authenticated user."""
        user_data = self.client.get_my_info()
        data = RedditUser(**user_data)
        return self.prepare_response(data, "RedditUserProfile")

    def vote_post(self, post_id: str, direction: int) -> ApiResponse:
        result = self.client.vote_post(post_id, direction)
        action_text = {1: "upvoted", -1: "downvoted", 0: "vote cleared"}
        message = f"Successfully {action_text[direction]} post"
        data = VoteResponse(success=result['success'], thing_id=f"t3_{post_id}", 
                          direction=result['direction'], message=message)
        return self.prepare_response(data, "RedditVotePost")

    def vote_comment(self, comment_id: str, direction: int) -> ApiResponse:
        result = self.client.vote_comment(comment_id, direction)
        action_text = {1: "upvoted", -1: "downvoted", 0: "vote cleared"}
        message = f"Successfully {action_text[direction]} comment"
        data = VoteResponse(success=result['success'], thing_id=f"t1_{comment_id}", 
                          direction=result['direction'], message=message)
        return self.prepare_response(data, "RedditVoteComment")

    def save_post(self, post_id: str) -> ApiResponse:
        """Save a post."""
        result = self.client.save_post(post_id)
        data = SaveResponse(success=result['success'], thing_id=f"t3_{post_id}", 
                          message="Post successfully saved")
        return self.prepare_response(data, "RedditSavePost")

    def save_comment(self, comment_id: str) -> ApiResponse:
        """Save a comment."""
        result = self.client.save_comment(comment_id)
        data = SaveResponse(success=result['success'], thing_id=f"t1_{comment_id}", 
                          message="Comment successfully saved")
        return self.prepare_response(data, "RedditSaveComment")

    def unsave_post(self, post_id: str) -> ApiResponse:
        """Unsave a post."""
        result = self.client.unsave_post(post_id)
        data = SaveResponse(success=result['success'], thing_id=f"t3_{post_id}", 
                          message="Post successfully unsaved")
        return self.prepare_response(data, "RedditUnsavePost")

    def unsave_comment(self, comment_id: str) -> ApiResponse:
        """Unsave a comment."""
        result = self.client.unsave_comment(comment_id)
        data = SaveResponse(success=result['success'], thing_id=f"t1_{comment_id}", 
                          message="Comment successfully unsaved")
        return self.prepare_response(data, "RedditUnsaveComment")

    def get_my_subreddits(self, limit: int = 100) -> ApiResponse:
        """Get list of subreddits the user is subscribed to."""
        subreddits = self.client.get_my_subreddits(limit)
        data = SubredditList(subreddits=[Subreddit(**sub) for sub in subreddits])
        return self.prepare_response(data, "RedditSubredditList")

    def get_link_flairs(self, subreddit: str) -> ApiResponse:
        """Get available link flairs for a subreddit."""
        raw_flairs = self.client.get_link_flairs(subreddit)
        formatted_flairs = []
        for flair in raw_flairs:
            formatted_flair = {
                "id": flair.get("id", ""),
                "text": flair.get("text", ""),
                "text_editable": flair.get("text_editable", False),
                "css_class": flair.get("css_class", ""),
                "background_color": flair.get("background_color", ""),
                "text_color": flair.get("text_color", ""),
                "type": flair.get("type", "text")
            }
            formatted_flairs.append(formatted_flair)
        
        data = FlairList(flairs=formatted_flairs)
        return self.prepare_response(data, "RedditFlairList")
