from fastapi import APIRouter, Body, Depends, HTTPException
from starlette.requests import Request as FastAPIRequest
from typing import Dict, Any
from .schema import (
    SubredditPostsParams, CommentParams, PostParams, 
    CommentInfoParams, SearchParams,
    GetSubredditPostsResponse, CreateCommentResponse, CreatePostResponse,
    GetCommentResponse,
    SearchResponse,
    ApiResponse,
    GetCommentsParams, GetCommentsResponse,
    DeletePostParams, DeletePostResponse,
    DeleteCommentParams, DeleteCommentResponse,
    EditPostParams, EditPostResponse,
    EditCommentParams, EditCommentResponse,
    UserInfoParams,
    GetUserInfoResponse, GetMyInfoParams, GetMyInfoResponse,
    VotePostParams, VotePostResponse, VoteCommentParams, VoteCommentResponse,
    SavePostParams, SavePostResponse, SaveCommentParams, SaveCommentResponse,
    UnsavePostParams, UnsavePostResponse, UnsaveCommentParams, UnsaveCommentResponse,
    GetMySubredditsParams, GetMySubredditsResponse
)
from .service import RedditService
from .client import RedditClient
from ..common.auth import TokenService, RedditTokenRefresher
from ..common.input_schema_decorator import schema
from ..common.utils import apply_error_handler_to_service, apply_error_handler_to_router, apply_error_handler_to_client
from ..common.examples_handler import ExamplesLoader
import base64
import aiohttp
import pickle
import os

router = APIRouter(prefix="/reddit", tags=["reddit"])
examples = ExamplesLoader()

async def get_reddit_service(request: FastAPIRequest):
    try:
        token_data = await TokenService.get_user_token(request, 'reddit')
        
        if TokenService.is_token_expired(token_data):
            try:
                token_data = await RedditTokenRefresher.refresh(request, token_data)
            except Exception as e:
                raise HTTPException(status_code=401, detail="Failed to refresh token")
        
        client = RedditClient(token_data['access_token'])
        apply_error_handler_to_client(client)
        service = RedditService(client)
        
        apply_error_handler_to_service(service)
        
        return service
    except Exception as e:
        raise HTTPException(
            status_code=401, 
            detail=f"Failed to initialize Reddit service: {str(e)}"
        )

@router.post("/get_posts", response_model=ApiResponse)
@schema(
    input_schema_class=SubredditPostsParams, 
    output_schema_class=GetSubredditPostsResponse,
    examples=examples["/reddit/get_posts"]
)
async def get_posts(
    params: Dict[str, Any] = Body(...),
    service: RedditService = Depends(get_reddit_service)
):
    validated_params = SubredditPostsParams(**params)
    return service.get_subreddit_posts(
        validated_params.subreddit,
        validated_params.limit,
        validated_params.sort
    )

@router.post("/submit_comment", response_model=ApiResponse)
@schema(
    input_schema_class=CommentParams, 
    output_schema_class=CreateCommentResponse,
    examples=examples["/reddit/submit_comment"]
)
async def submit_comment(
    params: Dict[str, Any] = Body(...),
    service: RedditService = Depends(get_reddit_service)
):
    validated_params = CommentParams(**params)
    return service.create_comment(validated_params.parent_id, validated_params.text)

@router.post("/submit_post", response_model=ApiResponse)
@schema(
    input_schema_class=PostParams, 
    output_schema_class=CreatePostResponse,
    examples=examples["/reddit/submit_post"]
)
async def submit_post(
    params: Dict[str, Any] = Body(...),
    service: RedditService = Depends(get_reddit_service)
):
    validated_params = PostParams(**params)
    return service.create_post(
        validated_params.subreddit,
        validated_params.title,
        validated_params.text,
        validated_params.url,
        validated_params.flair_id
    )

@router.post("/get_comment", response_model=ApiResponse)
@schema(
    input_schema_class=CommentInfoParams, 
    output_schema_class=GetCommentResponse,
    examples=examples["/reddit/get_comment"]
)
async def get_comment(
    params: Dict[str, Any] = Body(...),
    service: RedditService = Depends(get_reddit_service)
):
    validated_params = CommentInfoParams(**params)
    return service.get_comment(validated_params.comment_id)

@router.post("/get_comments", response_model=ApiResponse)
@schema(
    input_schema_class=GetCommentsParams, 
    output_schema_class=GetCommentsResponse,
    examples=examples["/reddit/get_comments"]
)
async def get_comments(
    params: Dict[str, Any] = Body(...),
    service: RedditService = Depends(get_reddit_service)
):
    validated_params = GetCommentsParams(**params)
    return service.get_comments(
        validated_params.post_id,
        validated_params.limit,
        validated_params.sort
    )

@router.post("/delete_post", response_model=ApiResponse)
@schema(
    input_schema_class=DeletePostParams, 
    output_schema_class=DeletePostResponse,
    examples=examples["/reddit/delete_post"]
)
async def delete_post(
    params: Dict[str, Any] = Body(...),
    service: RedditService = Depends(get_reddit_service)
):
    validated_params = DeletePostParams(**params)
    return service.delete_post(validated_params.post_id)

@router.post("/delete_comment", response_model=ApiResponse)
@schema(
    input_schema_class=DeleteCommentParams, 
    output_schema_class=DeleteCommentResponse,
    examples=examples["/reddit/delete_comment"]
)
async def delete_comment(
    params: Dict[str, Any] = Body(...),
    service: RedditService = Depends(get_reddit_service)
):
    validated_params = DeleteCommentParams(**params)
    return service.delete_comment(validated_params.comment_id)

@router.post("/edit_post", response_model=ApiResponse)
@schema(
    input_schema_class=EditPostParams, 
    output_schema_class=EditPostResponse,
    examples=examples["/reddit/edit_post"]
)
async def edit_post(
    params: Dict[str, Any] = Body(...),
    service: RedditService = Depends(get_reddit_service)
):
    validated_params = EditPostParams(**params)
    return service.edit_post(validated_params.post_id, validated_params.text)

@router.post("/edit_comment", response_model=ApiResponse)
@schema(
    input_schema_class=EditCommentParams, 
    output_schema_class=EditCommentResponse,
    examples=examples["/reddit/edit_comment"]
)
async def edit_comment(
    params: Dict[str, Any] = Body(...),
    service: RedditService = Depends(get_reddit_service)
):
    validated_params = EditCommentParams(**params)
    return service.edit_comment(validated_params.comment_id, validated_params.text)

@router.post("/search", response_model=ApiResponse)
@schema(
    input_schema_class=SearchParams, 
    output_schema_class=SearchResponse,
    examples=examples["/reddit/search"]
)
async def search(
    params: Dict[str, Any] = Body(...),
    service: RedditService = Depends(get_reddit_service)
):
    validated_params = SearchParams(**params)
    return service.search(
        validated_params.query,
        validated_params.subreddit,
        validated_params.limit
    )

@router.post("/get_user_info", response_model=ApiResponse)
@schema(
    input_schema_class=UserInfoParams,
    output_schema_class=GetUserInfoResponse,
    examples=examples["/reddit/get_user_info"]
)
async def get_user_info(
    params: Dict[str, Any] = Body(...),
    service: RedditService = Depends(get_reddit_service)
):
    validated_params = UserInfoParams(**params)
    return service.get_user_info(validated_params.username)

@router.post("/get_my_info", response_model=ApiResponse)
@schema(
    input_schema_class=GetMyInfoParams,
    output_schema_class=GetMyInfoResponse,
    examples=examples["/reddit/get_my_info"]
)
async def get_my_info(
    params: Dict[str, Any] = Body(...),
    service: RedditService = Depends(get_reddit_service)
):
    return service.get_my_info()

@router.post("/vote_post", response_model=ApiResponse)
@schema(
    input_schema_class=VotePostParams,
    output_schema_class=VotePostResponse,
    examples=examples["/reddit/vote_post"]
)
async def vote_post(
    params: Dict[str, Any] = Body(...),
    service: RedditService = Depends(get_reddit_service)
):
    validated_params = VotePostParams(**params)
    return service.vote_post(validated_params.post_id, validated_params.direction)

@router.post("/vote_comment", response_model=ApiResponse)
@schema(
    input_schema_class=VoteCommentParams,
    output_schema_class=VoteCommentResponse,
    examples=examples["/reddit/vote_comment"]
)
async def vote_comment(
    params: Dict[str, Any] = Body(...),
    service: RedditService = Depends(get_reddit_service)
):
    validated_params = VoteCommentParams(**params)
    return service.vote_comment(validated_params.comment_id, validated_params.direction)

@router.post("/save_post", response_model=ApiResponse)
@schema(
    input_schema_class=SavePostParams,
    output_schema_class=SavePostResponse,
    examples=examples["/reddit/save_post"]
)
async def save_post(
    params: Dict[str, Any] = Body(...),
    service: RedditService = Depends(get_reddit_service)
):
    validated_params = SavePostParams(**params)
    return service.save_post(validated_params.post_id)

@router.post("/save_comment", response_model=ApiResponse)
@schema(
    input_schema_class=SaveCommentParams,
    output_schema_class=SaveCommentResponse,
    examples=examples["/reddit/save_comment"]
)
async def save_comment(
    params: Dict[str, Any] = Body(...),
    service: RedditService = Depends(get_reddit_service)
):
    validated_params = SaveCommentParams(**params)
    return service.save_comment(validated_params.comment_id)

@router.post("/unsave_post", response_model=ApiResponse)
@schema(
    input_schema_class=UnsavePostParams,
    output_schema_class=UnsavePostResponse,
    examples=examples["/reddit/unsave_post"]
)
async def unsave_post(
    params: Dict[str, Any] = Body(...),
    service: RedditService = Depends(get_reddit_service)
):
    validated_params = UnsavePostParams(**params)
    return service.unsave_post(validated_params.post_id)

@router.post("/unsave_comment", response_model=ApiResponse)
@schema(
    input_schema_class=UnsaveCommentParams,
    output_schema_class=UnsaveCommentResponse,
    examples=examples["/reddit/unsave_comment"]
)
async def unsave_comment(
    params: Dict[str, Any] = Body(...),
    service: RedditService = Depends(get_reddit_service)
):
    validated_params = UnsaveCommentParams(**params)
    return service.unsave_comment(validated_params.comment_id)

@router.post("/get_my_subreddits", response_model=ApiResponse)
@schema(
    input_schema_class=GetMySubredditsParams,
    output_schema_class=GetMySubredditsResponse,
    examples=examples["/reddit/get_my_subreddits"]
)
async def get_my_subreddits(
    params: Dict[str, Any] = Body(...),
    service: RedditService = Depends(get_reddit_service)
):
    validated_params = GetMySubredditsParams(**params)
    return service.get_my_subreddits(validated_params.limit)

apply_error_handler_to_router(router)
