from fastapi import APIRouter, Depends, HTTPException, Request as FastAPIRequest, Body
from typing import Dict, Any
from .schema import (
    ApiResponse, SearchVideosParams, GetVideoParams, 
    GetCaptionsParams, GetTranscriptionParams,
    SearchVideosResponse, GetVideoResponse, 
    GetCaptionsResponse, GetTranscriptionResponse
)
from .service import YouTubeService
from .client import YouTubeClient
from ..common.auth import validate_provider_api_key
from ..common.input_schema_decorator import schema
from pydantic import ValidationError
from ..common.utils import format_validation_error
from ..common.examples_handler import ExamplesLoader

router = APIRouter(prefix="/youtube", tags=["youtube"])

examples = ExamplesLoader()

async def get_youtube_service(request: FastAPIRequest):
    try:
        api_key = await validate_provider_api_key(request, "youtube")
        client = YouTubeClient(api_key)
        return YouTubeService(client)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to initialize service: {str(e)}")

@router.post("/search_videos", response_model=ApiResponse)
@schema(input_schema_class=SearchVideosParams, output_schema_class=SearchVideosResponse, examples=examples["/youtube/search_videos"])
async def search_videos(
    params: Dict[str, Any] = Body(...),
    service: YouTubeService = Depends(get_youtube_service)
):
    try:
        validated_params = SearchVideosParams(**params)
        return service.search_videos(validated_params.filters, validated_params.page_token)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'SearchVideosParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_video", response_model=ApiResponse)
@schema(input_schema_class=GetVideoParams, output_schema_class=GetVideoResponse, examples=examples["/youtube/get_video"])
async def get_video(
    params: Dict[str, Any] = Body(...),
    service: YouTubeService = Depends(get_youtube_service)
):
    try:
        validated_params = GetVideoParams(**params)
        return service.get_video(validated_params.video_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetVideoParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_captions", response_model=ApiResponse)
@schema(input_schema_class=GetCaptionsParams, output_schema_class=GetCaptionsResponse, examples=examples["/youtube/get_captions"])
async def get_captions(
    params: Dict[str, Any] = Body(...),
    service: YouTubeService = Depends(get_youtube_service)
):
    try:
        validated_params = GetCaptionsParams(**params)
        return service.get_captions(validated_params.video_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetCaptionsParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_transcription", response_model=ApiResponse)
@schema(input_schema_class=GetTranscriptionParams, output_schema_class=GetTranscriptionResponse, examples=examples["/youtube/get_transcription"])
async def get_transcription(
    params: Dict[str, Any] = Body(...),
    service: YouTubeService = Depends(get_youtube_service)
):
    try:
        validated_params = GetTranscriptionParams(**params)
        return service.get_transcription(
            validated_params.video_id,
            validated_params.caption_id,
            validated_params.language
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetTranscriptionParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))