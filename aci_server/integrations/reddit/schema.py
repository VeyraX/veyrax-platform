from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union

# Input Schemas
class SubredditPostsParams(BaseModel):
    subreddit: str = Field(..., description="Name of the subreddit")
    limit: Optional[int] = Field(25, ge=1, le=100, description="Number of posts to fetch")
    sort: Optional[str] = Field("hot", description="Sort type: hot, new, top, rising")

class CommentParams(BaseModel):
    text: str = Field(..., description="Comment text")
    thing_id: str = Field(..., description="Full name of parent submission or comment")

class PostParams(BaseModel):
    subreddit: str = Field(..., description="Subreddit to submit to")
    title: str = Field(..., description="Post title")
    text: Optional[str] = Field(None, description="Text for self posts")
    url: Optional[str] = Field(None, description="URL for link posts")
    flair_id: Optional[str] = Field(None, description="Flair ID for the post")

class FlairParams(BaseModel):
    subreddit: str = Field(..., description="Subreddit to get flairs from")

class CommentInfoParams(BaseModel):
    comment_id: str = Field(..., description="Full name of the comment")

class DeleteParams(BaseModel):
    thing_id: str = Field(..., description="Full name of comment/post to delete")

class EditParams(BaseModel):
    thing_id: str = Field(..., description="Full name of comment/post to edit")
    text: str = Field(..., description="New text content")

class SearchParams(BaseModel):
    query: str = Field(..., description="Search query")
    subreddit: Optional[str] = Field(None, description="Limit search to subreddit")
    limit: Optional[int] = Field(25, ge=1, le=100, description="Number of results")

class GetCommentsParams(BaseModel):
    post_id: str = Field(..., description="ID of the post to get comments from")
    limit: Optional[int] = Field(25, ge=1, le=100, description="Number of comments to fetch")
    sort: Optional[str] = Field("top", description="Sort type: top, new, controversial, old")

class DeletePostParams(BaseModel):
    post_id: str = Field(..., description="ID of the post to delete")

class DeleteCommentParams(BaseModel):
    comment_id: str = Field(..., description="ID of the comment to delete")

class EditPostParams(BaseModel):
    post_id: str = Field(..., description="ID of the post to edit")
    text: str = Field(..., description="New text content for the post")

class EditCommentParams(BaseModel):
    comment_id: str = Field(..., description="ID of the comment to edit")
    text: str = Field(..., description="New text content for the comment")

# Response Models
class RedditPost(BaseModel):
    id: str
    title: str
    author: str
    subreddit: str
    score: int
    url: str
    created_utc: float
    num_comments: int
    is_self: bool
    selftext: Optional[str]
    permalink: str

class RedditComment(BaseModel):
    id: str
    author: str
    body: str
    score: int
    created_utc: float
    permalink: str
    parent_id: str

class SubredditFlair(BaseModel):
    id: str
    text: str
    type: str
    text_color: str
    background_color: str

class PostList(BaseModel):
    posts: List[RedditPost]

class CommentList(BaseModel):
    comments: List[RedditComment]

class FlairList(BaseModel):
    flairs: List[SubredditFlair]

class ActionResponse(BaseModel):
    success: bool
    message: str

# Response Schemas
class GetSubredditPostsResponse(BaseModel):
    data: PostList
    message: Optional[str] = None

class CreateCommentResponse(BaseModel):
    data: RedditComment
    message: Optional[str] = None

class CreatePostResponse(BaseModel):
    data: RedditPost
    message: Optional[str] = None

class GetSubredditFlairsResponse(BaseModel):
    data: FlairList
    message: Optional[str] = None

class GetCommentResponse(BaseModel):
    data: RedditComment
    message: Optional[str] = None

class DeleteThingResponse(BaseModel):
    data: ActionResponse
    message: Optional[str] = None

class EditThingResponse(BaseModel):
    data: Union[RedditComment, RedditPost]
    message: Optional[str] = None

class SearchResponse(BaseModel):
    data: PostList
    message: Optional[str] = None

class GetCommentsResponse(BaseModel):
    data: CommentList
    message: Optional[str] = None

class DeletePostResponse(BaseModel):
    data: ActionResponse
    message: Optional[str] = None

class DeleteCommentResponse(BaseModel):
    data: ActionResponse
    message: Optional[str] = None

class EditPostResponse(BaseModel):
    data: RedditPost
    message: Optional[str] = None

class EditCommentResponse(BaseModel):
    data: RedditComment
    message: Optional[str] = None

# Новые входные схемы
class UserInfoParams(BaseModel):
    username: str = Field(..., description="Reddit username")

class VoteParams(BaseModel):
    thing_id: str = Field(..., description="Full name of post/comment to vote on")
    direction: int = Field(..., ge=-1, le=1, description="Vote direction: 1 (upvote), -1 (downvote), 0 (clear vote)")

class SaveParams(BaseModel):
    thing_id: str = Field(..., description="Full name of post/comment to save")

class UnsaveParams(BaseModel):
    thing_id: str = Field(..., description="Full name of post/comment to unsave")

class GetSavedParams(BaseModel):
    limit: Optional[int] = Field(25, ge=1, le=100, description="Number of saved items to fetch")

# Новые модели ответов
class RedditUser(BaseModel):
    id: str
    name: str
    created_utc: float
    comment_karma: int
    link_karma: int
    is_gold: bool
    is_mod: bool
    has_verified_email: bool

class VoteResponse(BaseModel):
    success: bool
    thing_id: str
    direction: int
    message: str

class SaveResponse(BaseModel):
    success: bool
    thing_id: str
    message: str

class SavedItemsList(BaseModel):
    items: List[Union[RedditPost, RedditComment]]

# Новые схемы ответов
class GetUserInfoResponse(BaseModel):
    data: RedditUser
    message: Optional[str] = None

class VoteThingResponse(BaseModel):
    data: VoteResponse
    message: Optional[str] = None

class SaveThingResponse(BaseModel):
    data: SaveResponse
    message: Optional[str] = None

class UnsaveThingResponse(BaseModel):
    data: SaveResponse
    message: Optional[str] = None

class GetSavedItemsResponse(BaseModel):
    data: SavedItemsList
    message: Optional[str] = None

# Новая входная схема для /get_my_info
class GetMyInfoParams(BaseModel):
    # Пустая схема, так как эндпоинт не требует параметров
    pass

# Новая схема ответа
class GetMyInfoResponse(BaseModel):
    data: RedditUser
    message: Optional[str] = None

# API Response
class ApiResponse(BaseModel):
    data: Union[
        PostList, CommentList, FlairList, 
        RedditPost, RedditComment, ActionResponse,
        GetSubredditPostsResponse, CreateCommentResponse,
        CreatePostResponse, GetSubredditFlairsResponse,
        GetCommentResponse, DeleteThingResponse,
        EditThingResponse, SearchResponse,
        GetCommentsResponse, DeletePostResponse,
        DeleteCommentResponse, EditPostResponse,
        EditCommentResponse,
        GetUserInfoResponse, VoteThingResponse,
        SaveThingResponse, UnsaveThingResponse,
        GetSavedItemsResponse,
        RedditUser, VoteResponse, SaveResponse, SavedItemsList,
        GetMyInfoResponse
    ]
    component: Optional[Dict[str, Any]] = None
