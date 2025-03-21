from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union

class SubredditPostsParams(BaseModel):
    subreddit: str = Field(..., description="Name of the subreddit")
    limit: Optional[int] = Field(25, ge=1, le=100, description="Number of posts to fetch")
    sort: Optional[str] = Field("hot", description="Sort type: hot, new, top, rising")

class CommentParams(BaseModel):
    text: str = Field(..., description="Comment text")
    parent_id: str = Field(..., description="Full ID of parent submission or comment (use t3_ prefix for posts, t1_ prefix for comments)")

class PostParams(BaseModel):
    subreddit: str = Field(..., description="Subreddit to submit to")
    title: str = Field(..., description="Post title")
    text: Optional[str] = Field(None, description="Text for self posts")
    url: Optional[str] = Field(None, description="URL for link posts")
    flair_id: Optional[str] = Field(None, description="Flair ID for the post")

class CommentInfoParams(BaseModel):
    comment_id: str = Field(..., description="Full name of the comment")

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

class PostList(BaseModel):
    posts: List[RedditPost]

class CommentList(BaseModel):
    comments: List[RedditComment]

class ActionResponse(BaseModel):
    success: bool
    message: str

class GetSubredditPostsResponse(BaseModel):
    data: PostList
    message: Optional[str] = None

class CreateCommentResponse(BaseModel):
    data: RedditComment
    message: Optional[str] = None

class CreatePostResponse(BaseModel):
    data: RedditPost
    message: Optional[str] = None

class GetCommentResponse(BaseModel):
    data: RedditComment
    message: Optional[str] = None

class UserInfoParams(BaseModel):
    username: str = Field(..., description="Reddit username")

class VoteParams(BaseModel):
    thing_id: str = Field(..., description="Full name of post/comment to vote on")
    direction: int = Field(..., ge=-1, le=1, description="Vote direction: 1 (upvote), -1 (downvote), 0 (clear vote)")

class SaveParams(BaseModel):
    thing_id: str = Field(..., description="Full name of post/comment to save")

class UnsaveParams(BaseModel):
    thing_id: str = Field(..., description="Full name of post/comment to unsave")

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

class GetUserInfoResponse(BaseModel):
    data: RedditUser
    message: Optional[str] = None

class VotePostParams(BaseModel):
    post_id: str = Field(..., description="ID of post to vote on")
    direction: int = Field(..., ge=-1, le=1, description="Vote direction: 1 (upvote), -1 (downvote), 0 (clear vote)")

class VoteCommentParams(BaseModel):
    comment_id: str = Field(..., description="ID of comment to vote on")
    direction: int = Field(..., ge=-1, le=1, description="Vote direction: 1 (upvote), -1 (downvote), 0 (clear vote)")

class SavePostParams(BaseModel):
    post_id: str = Field(..., description="ID of post to save")

class SaveCommentParams(BaseModel):
    comment_id: str = Field(..., description="ID of comment to save")

class UnsavePostParams(BaseModel):
    post_id: str = Field(..., description="ID of post to unsave")

class UnsaveCommentParams(BaseModel):
    comment_id: str = Field(..., description="ID of comment to unsave")

class VotePostResponse(BaseModel):
    data: VoteResponse
    message: Optional[str] = None

class VoteCommentResponse(BaseModel):
    data: VoteResponse
    message: Optional[str] = None

class SavePostResponse(BaseModel):
    data: SaveResponse
    message: Optional[str] = None

class SaveCommentResponse(BaseModel):
    data: SaveResponse
    message: Optional[str] = None

class UnsavePostResponse(BaseModel):
    data: SaveResponse
    message: Optional[str] = None

class UnsaveCommentResponse(BaseModel):
    data: SaveResponse
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

class Subreddit(BaseModel):
    id: str
    display_name: str
    name: str
    title: str
    description: Optional[str]
    subscribers: int
    created_utc: float
    url: str
    over18: bool
    community_icon: Optional[str]
    banner_img: Optional[str]
    header_img: Optional[str]
    icon_img: Optional[str]

class SubredditList(BaseModel):
    subreddits: List[Subreddit]

class GetMySubredditsParams(BaseModel):
    limit: Optional[int] = Field(100, ge=1, le=250, description="Number of subreddits to fetch")

class GetMySubredditsResponse(BaseModel):
    data: SubredditList
    message: Optional[str] = None

class GetMyInfoParams(BaseModel):
    pass 

class GetMyInfoResponse(BaseModel):
    data: RedditUser
    message: Optional[str] = None

class ApiResponse(BaseModel):
    data: Union[
        PostList, CommentList, 
        RedditPost, RedditComment, ActionResponse,
        GetSubredditPostsResponse, CreateCommentResponse,
        CreatePostResponse, 
        GetCommentResponse, 
        SearchResponse,
        GetCommentsResponse, DeletePostResponse,
        DeleteCommentResponse, EditPostResponse,
        EditCommentResponse,
        GetUserInfoResponse, 
        RedditUser, VoteResponse, SaveResponse,
        GetMyInfoResponse,
        VotePostResponse, VoteCommentResponse,
        SavePostResponse, SaveCommentResponse,
        UnsavePostResponse, UnsaveCommentResponse,
        SubredditList,
        GetMySubredditsResponse
    ]
    component: Optional[Dict[str, Any]] = None
