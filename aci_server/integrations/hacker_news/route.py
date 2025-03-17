from fastapi import APIRouter, Depends, Body, HTTPException, Request
from typing import Dict, Any, List
from .schema import (
    GetStoriesParams,
    GetItemParams,
    GetUserParams,
    GetCommentsParams,
    SearchStoriesParams,
    ApiResponse
)
from .service import HackerNewsService
from .client import HackerNewsClient
from ..common.input_schema_decorator import schema
from ..common.utils import apply_error_handler_to_service, apply_error_handler_to_router
from ..common.examples_handler import ExamplesLoader

router = APIRouter(prefix="/hacker-news", tags=["hacker-news"])
examples = ExamplesLoader()

async def get_hacker_news_service(request: Request = None):
    try:
        client = HackerNewsClient()
        service = HackerNewsService(client)
        apply_error_handler_to_service(service)
        return service
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hacker News service initialization failed: {str(e)}")

@router.post("/top_stories", response_model=ApiResponse)
@schema(
    input_schema_class=GetStoriesParams,
    output_schema_class=ApiResponse,
    examples=["/hacker-news/top_stories"]
)
async def get_top_stories(
    params: Dict[str, Any] = Body(...),
    service: HackerNewsService = Depends(get_hacker_news_service),
):
    validated_params = GetStoriesParams(**params)
    return service.get_top_stories(validated_params)

@router.post("/new_stories", response_model=ApiResponse)
@schema(
    input_schema_class=GetStoriesParams,
    output_schema_class=ApiResponse,
    examples=["/hacker-news/new_stories"]
)
async def get_new_stories(
    params: Dict[str, Any] = Body(...),
    service: HackerNewsService = Depends(get_hacker_news_service),
):
    validated_params = GetStoriesParams(**params)
    return service.get_new_stories(validated_params)

@router.post("/best_stories", response_model=ApiResponse)
@schema(
    input_schema_class=GetStoriesParams,
    output_schema_class=ApiResponse,
    examples=["/hacker-news/best_stories"]
)
async def get_best_stories(
    params: Dict[str, Any] = Body(...),
    service: HackerNewsService = Depends(get_hacker_news_service),
):
    validated_params = GetStoriesParams(**params)
    return service.get_best_stories(validated_params)

@router.post("/ask_stories", response_model=ApiResponse)
@schema(
    input_schema_class=GetStoriesParams,
    output_schema_class=ApiResponse,
    examples=["/hacker-news/ask_stories"]
)
async def get_ask_stories(
    params: Dict[str, Any] = Body(...),
    service: HackerNewsService = Depends(get_hacker_news_service),
):
    validated_params = GetStoriesParams(**params)
    return service.get_ask_stories(validated_params)

@router.post("/show_stories", response_model=ApiResponse)
@schema(
    input_schema_class=GetStoriesParams,
    output_schema_class=ApiResponse,
    examples=["/hacker-news/show_stories"]
)
async def get_show_stories(
    params: Dict[str, Any] = Body(...),
    service: HackerNewsService = Depends(get_hacker_news_service),
):
    validated_params = GetStoriesParams(**params)
    return service.get_show_stories(validated_params)

@router.post("/job_stories", response_model=ApiResponse)
@schema(
    input_schema_class=GetStoriesParams,
    output_schema_class=ApiResponse,
    examples=["/hacker-news/job_stories"]
)
async def get_job_stories(
    params: Dict[str, Any] = Body(...),
    service: HackerNewsService = Depends(get_hacker_news_service),
):
    validated_params = GetStoriesParams(**params)
    return service.get_job_stories(validated_params)

@router.post("/item", response_model=ApiResponse)
@schema(
    input_schema_class=GetItemParams,
    output_schema_class=ApiResponse,
    examples=["/hacker-news/item"]
)
async def get_item(
    params: Dict[str, Any] = Body(...),
    service: HackerNewsService = Depends(get_hacker_news_service),
):
    validated_params = GetItemParams(**params)
    return service.get_item(validated_params)

@router.post("/user", response_model=ApiResponse)
@schema(
    input_schema_class=GetUserParams,
    output_schema_class=ApiResponse,
    examples=["/hacker-news/user"]
)
async def get_user(
    params: Dict[str, Any] = Body(...),
    service: HackerNewsService = Depends(get_hacker_news_service),
):
    validated_params = GetUserParams(**params)
    return service.get_user(validated_params)

@router.post("/comments", response_model=ApiResponse)
@schema(
    input_schema_class=GetCommentsParams,
    output_schema_class=ApiResponse,
    examples=["/hacker-news/comments"]
)
async def get_comments(
    params: Dict[str, Any] = Body(...),
    service: HackerNewsService = Depends(get_hacker_news_service),
):
    validated_params = GetCommentsParams(**params)
    return service.get_comments(validated_params)

apply_error_handler_to_router(router)
