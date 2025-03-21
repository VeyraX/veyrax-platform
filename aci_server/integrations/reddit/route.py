from fastapi import APIRouter, Body, Depends, HTTPException
from starlette.requests import Request as FastAPIRequest
from typing import Dict, Any
from .schema import (
    SubredditPostsParams, CommentParams, PostParams, FlairParams,
    CommentInfoParams, DeleteParams, EditParams, SearchParams,
    GetSubredditPostsResponse, CreateCommentResponse, CreatePostResponse,
    GetSubredditFlairsResponse, GetCommentResponse, DeleteThingResponse,
    EditThingResponse, SearchResponse,
    ApiResponse,
    GetCommentsParams, GetCommentsResponse,
    DeletePostParams, DeletePostResponse,
    DeleteCommentParams, DeleteCommentResponse,
    EditPostParams, EditPostResponse,
    EditCommentParams, EditCommentResponse,
    UserInfoParams, VoteParams, SaveParams, UnsaveParams, GetSavedParams,
    GetUserInfoResponse, VoteThingResponse, SaveThingResponse, UnsaveThingResponse, 
    GetSavedItemsResponse, GetMyInfoParams, GetMyInfoResponse
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
    return service.create_comment(validated_params.thing_id, validated_params.text)

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

@router.post("/get_flairs", response_model=ApiResponse)
@schema(
    input_schema_class=FlairParams, 
    output_schema_class=GetSubredditFlairsResponse,
    examples=examples["/reddit/get_flairs"]
)
async def get_flairs(
    params: Dict[str, Any] = Body(...),
    service: RedditService = Depends(get_reddit_service)
):
    validated_params = FlairParams(**params)
    return service.get_subreddit_flairs(validated_params.subreddit)

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

@router.post("/vote", response_model=ApiResponse)
@schema(
    input_schema_class=VoteParams,
    output_schema_class=VoteThingResponse,
    examples=examples["/reddit/vote"]
)
async def vote(
    params: Dict[str, Any] = Body(...),
    service: RedditService = Depends(get_reddit_service)
):
    validated_params = VoteParams(**params)
    return service.vote(validated_params.thing_id, validated_params.direction)

@router.post("/save", response_model=ApiResponse)
@schema(
    input_schema_class=SaveParams,
    output_schema_class=SaveThingResponse,
    examples=examples["/reddit/save"]
)
async def save(
    params: Dict[str, Any] = Body(...),
    service: RedditService = Depends(get_reddit_service)
):
    validated_params = SaveParams(**params)
    return service.save_thing(validated_params.thing_id)

@router.post("/unsave", response_model=ApiResponse)
@schema(
    input_schema_class=UnsaveParams,
    output_schema_class=UnsaveThingResponse,
    examples=examples["/reddit/unsave"]
)
async def unsave(
    params: Dict[str, Any] = Body(...),
    service: RedditService = Depends(get_reddit_service)
):
    validated_params = UnsaveParams(**params)
    return service.unsave_thing(validated_params.thing_id)

@router.post("/get_saved", response_model=ApiResponse)
@schema(
    input_schema_class=GetSavedParams,
    output_schema_class=GetSavedItemsResponse,
    examples=examples["/reddit/get_saved"]
)
async def get_saved(
    params: Dict[str, Any] = Body(...),
    service: RedditService = Depends(get_reddit_service)
):
    validated_params = GetSavedParams(**params)
    return service.get_saved(validated_params.limit)

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

apply_error_handler_to_router(router)
