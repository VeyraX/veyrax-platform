from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
from datetime import datetime

class VideoBase(BaseModel):
    id: str
    title: str
    description: str
    thumbnail_url: str
    published_at: datetime
    channel_title: str
    channel_id: str

class Video(VideoBase):
    view_count: Optional[int] = None
    like_count: Optional[int] = None
    comment_count: Optional[int] = None
    duration: Optional[str] = None
    html_link: Optional[str] = None

class VideoList(BaseModel):
    videos: List[VideoBase]
    next_page_token: Optional[str] = None
    total_results: Optional[int] = None

class Caption(BaseModel):
    id: str
    language: str
    name: str
    is_auto: bool

class CaptionList(BaseModel):
    captions: List[Caption]
    video_id: str

class Transcription(BaseModel):
    video_id: str
    caption_id: str
    text: str
    language: str

class SearchFilters(BaseModel):
    query: str
    max_results: Optional[int] = 25
    published_after: Optional[str] = None
    published_before: Optional[str] = None
    channel_id: Optional[str] = None
    order: Optional[str] = "relevance"

class ApiResponse(BaseModel):
    data: Union[Video, VideoList, CaptionList, Transcription]
    component: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None

# Input schema classes
class SearchVideosParams(BaseModel):
    filters: SearchFilters
    page_token: Optional[str] = None

class GetVideoParams(BaseModel):
    video_id: str

class GetCaptionsParams(BaseModel):
    video_id: str

class GetTranscriptionParams(BaseModel):
    video_id: str
    caption_id: Optional[str] = None
    language: Optional[str] = None

# Output schema classes
class SearchVideosResponse(BaseModel):
    data: VideoList
    message: Optional[str] = None

class GetVideoResponse(BaseModel):
    data: Video
    message: Optional[str] = None

class GetCaptionsResponse(BaseModel):
    data: CaptionList
    message: Optional[str] = None

class GetTranscriptionResponse(BaseModel):
    data: Transcription
    message: Optional[str] = None