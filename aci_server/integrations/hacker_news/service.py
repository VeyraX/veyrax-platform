from typing import Optional, Dict, Any, List, Union
from .client import HackerNewsClient
from .schema import (
    ApiResponse,
    Story,
    StoryList,
    Comment,
    CommentList,
    User,
    GetStoriesParams,
    GetItemParams,
    GetUserParams,
    GetCommentsParams,
    SearchStoriesParams
)
import os
import time
from datetime import datetime
from ..common.component_handler import load_components, prepare_components_auto

class HackerNewsService:
    def __init__(self, client: HackerNewsClient):
        self.client = client
        self.components_data = self._load_components()

    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
        
    def prepare_response(self, data: Any, component_name: str = None) -> ApiResponse:
        tool_name = "hacker-news"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)

    def _convert_to_story(self, item: Dict[str, Any]) -> Story:
        return Story(
            id=item.get('id', 0),
            title=item.get('title', ''),
            url=item.get('url'),
            text=item.get('text'),
            by=item.get('by'),
            score=item.get('score'),
            time=item.get('time'),
            descendants=item.get('descendants'),
            kids=item.get('kids'),
            type=item.get('type')
        )

    def _convert_to_comment(self, item: Dict[str, Any]) -> Comment:
        return Comment(
            id=item.get('id', 0),
            text=item.get('text'),
            by=item.get('by'),
            time=item.get('time'),
            kids=item.get('kids'),
            parent=item.get('parent'),
            type=item.get('type')
        )

    def _convert_to_user(self, item: Dict[str, Any]) -> User:
        return User(
            id=item.get('id', ''),
            created=item.get('created'),
            karma=item.get('karma'),
            about=item.get('about'),
            submitted=item.get('submitted')
        )

    def get_top_stories(self, params: GetStoriesParams) -> ApiResponse:
        story_ids = self.client.get_top_stories()
        
        paginated_ids = story_ids[params.offset:params.offset + params.limit]
        
        stories_data = self.client.get_items_batch(paginated_ids)
        stories = [self._convert_to_story(item) for item in stories_data]
        
        story_list = StoryList(
            stories=stories,
            total=len(story_ids),
            offset=params.offset,
            limit=params.limit
        )
        
        return self.prepare_response(story_list, "HackerNewsStoryListCard")

    def get_new_stories(self, params: GetStoriesParams) -> ApiResponse:
        story_ids = self.client.get_new_stories()
        
        paginated_ids = story_ids[params.offset:params.offset + params.limit]
        
        stories_data = self.client.get_items_batch(paginated_ids)
        stories = [self._convert_to_story(item) for item in stories_data]
        
        story_list = StoryList(
            stories=stories,
            total=len(story_ids),
            offset=params.offset,
            limit=params.limit
        )
        
        return self.prepare_response(story_list, "HackerNewsStoryListCard")

    def get_best_stories(self, params: GetStoriesParams) -> ApiResponse:
        story_ids = self.client.get_best_stories()
        
        paginated_ids = story_ids[params.offset:params.offset + params.limit]
        
        stories_data = self.client.get_items_batch(paginated_ids)
        stories = [self._convert_to_story(item) for item in stories_data]
        
        story_list = StoryList(
            stories=stories,
            total=len(story_ids),
            offset=params.offset,
            limit=params.limit
        )
        
        return self.prepare_response(story_list, "HackerNewsStoryListCard")

    def get_ask_stories(self, params: GetStoriesParams) -> ApiResponse:
        story_ids = self.client.get_ask_stories()
        
        paginated_ids = story_ids[params.offset:params.offset + params.limit]
        
        stories_data = self.client.get_items_batch(paginated_ids)
        stories = [self._convert_to_story(item) for item in stories_data]
        
        story_list = StoryList(
            stories=stories,
            total=len(story_ids),
            offset=params.offset,
            limit=params.limit
        )
        
        return self.prepare_response(story_list, "HackerNewsStoryListCard")

    def get_show_stories(self, params: GetStoriesParams) -> ApiResponse:
        story_ids = self.client.get_show_stories()
        
        paginated_ids = story_ids[params.offset:params.offset + params.limit]
        
        stories_data = self.client.get_items_batch(paginated_ids)
        stories = [self._convert_to_story(item) for item in stories_data]
        
        story_list = StoryList(
            stories=stories,
            total=len(story_ids),
            offset=params.offset,
            limit=params.limit
        )
        
        return self.prepare_response(story_list, "HackerNewsStoryListCard")

    def get_job_stories(self, params: GetStoriesParams) -> ApiResponse:
        """Get job stories"""
        story_ids = self.client.get_job_stories()
        
        paginated_ids = story_ids[params.offset:params.offset + params.limit]
        
        stories_data = self.client.get_items_batch(paginated_ids)
        stories = [self._convert_to_story(item) for item in stories_data]
        
        story_list = StoryList(
            stories=stories,
            total=len(story_ids),
            offset=params.offset,
            limit=params.limit
        )
        
        return self.prepare_response(story_list, "HackerNewsStoryListCard")

    def get_item(self, params: GetItemParams) -> ApiResponse:
        item_data = self.client.get_item(params.item_id)
        
        if item_data.get('type') == 'comment':
            item = self._convert_to_comment(item_data)
            return self.prepare_response(item, "HackerNewsCommentCard")
        else:
            item = self._convert_to_story(item_data)
            return self.prepare_response(item, "HackerNewsStoryCard")

    def get_user(self, params: GetUserParams) -> ApiResponse:
        user_data = self.client.get_user(params.username)
        user = self._convert_to_user(user_data)
        return self.prepare_response(user, "HackerNewsUserCard")

    def get_comments(self, params: GetCommentsParams) -> ApiResponse:
        story_data = self.client.get_item(params.story_id)
        comment_ids = story_data.get('kids', [])
        
        paginated_ids = comment_ids[params.offset:params.offset + params.limit]
        
        comments_data = self.client.get_items_batch(paginated_ids)
        comments = [self._convert_to_comment(item) for item in comments_data]
        
        comment_list = CommentList(
            comments=comments,
            total=len(comment_ids),
            offset=params.offset,
            limit=params.limit,
            story_id=params.story_id
        )
        
        return self.prepare_response(comment_list, "HackerNewsCommentListCard")
