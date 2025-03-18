from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any, Union, Literal

# Input schemas
class GetStoriesParams(BaseModel):
    limit: Optional[int] = Field(
        30,
        description="Maximum number of stories to return",
        ge=1,
        le=500
    )
    offset: Optional[int] = Field(
        0,
        description="Number of stories to skip",
        ge=0
    )

class GetItemParams(BaseModel):
    item_id: int = Field(
        ...,
        description="ID of the item to retrieve",
        example=8863
    )

class GetUserParams(BaseModel):
    username: str = Field(
        ...,
        description="Username of the user to retrieve",
        example="dang"
    )

class GetCommentsParams(BaseModel):
    story_id: int = Field(
        ...,
        description="ID of the story to retrieve comments for",
        example=8863
    )
    limit: Optional[int] = Field(
        30,
        description="Maximum number of comments to return",
        ge=1,
        le=500
    )
    offset: Optional[int] = Field(
        0,
        description="Number of comments to skip",
        ge=0
    )

class SearchStoriesParams(BaseModel):
    query: str = Field(
        ...,
        description="Search query",
        example="python"
    )
    tags: Optional[str] = Field(
        None,
        description="Tags to filter by (comma-separated)",
        example="story,poll"
    )
    limit: Optional[int] = Field(
        30,
        description="Maximum number of stories to return",
        ge=1,
        le=500
    )
    offset: Optional[int] = Field(
        0,
        description="Number of stories to skip",
        ge=0
    )

# Output schemas
class Story(BaseModel):
    id: int
    title: str
    url: Optional[str] = None
    text: Optional[str] = None
    by: Optional[str] = None
    score: Optional[int] = None
    time: Optional[int] = None
    descendants: Optional[int] = None
    kids: Optional[List[int]] = None
    type: Optional[str] = None

class Comment(BaseModel):
    id: int
    text: Optional[str] = None
    by: Optional[str] = None
    time: Optional[int] = None
    kids: Optional[List[int]] = None
    parent: Optional[int] = None
    type: Optional[str] = None

class User(BaseModel):
    id: str
    created: Optional[int] = None
    karma: Optional[int] = None
    about: Optional[str] = None
    submitted: Optional[List[int]] = None

class StoryList(BaseModel):
    stories: List[Story]
    total: int
    offset: int
    limit: int

class CommentList(BaseModel):
    comments: List[Comment]
    total: int
    offset: int
    limit: int
    story_id: int

# API Response
class ApiResponse(BaseModel):
    data: Union[Story, StoryList, Comment, CommentList, User]
    component: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = Field(
        None,
        description="UI components configuration for rendering results"
    )
