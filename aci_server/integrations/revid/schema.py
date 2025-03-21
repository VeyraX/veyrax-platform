from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from pydantic import validator

# Base models
class CreateVideoInput(BaseModel):
    input_text: str
    webhook: Optional[str] = Field(None)
    selected_voice: Optional[str] = Field('CwhRBWXzGAHq8TQ4Fs17', description='voice id')
    generation_user_prompt: Optional[str] = None
    audio_url: Optional[str] = Field("https://cdn.tfrv.xyz/audio/cartoon-music-1.mp3", description='audio in mp3 format')
    caption_preset_name: Optional[str] = "Wrap 2"
    has_avatar: Optional[bool] = False
    selected_avatar: Optional[str] = None
    media_type: Optional[str] = Field("movingImage", description="Type of media: stockVideo, movingImage, or aiVideo")
    generation_preset: Optional[str] = Field("REALISM", description="AI generation preset style")
    ratio: Optional[str] = Field("9 / 16", description="Video aspect ratio")
    
class VideoStatusInput(BaseModel):
    project_id: str
    
class ProjectsListInput(BaseModel):
    limit: Optional[int] = 10
    
class QueueInput(BaseModel):
    video_url: str
    channel_name: str
    tiktok: Optional[Dict[str, Any]] = None
    youtube: Optional[Dict[str, Any]] = None
    instagram: Optional[Dict[str, Any]] = None
    
class PublishInput(BaseModel):
    video_url: str
    channel_name: str
    tiktok: Optional[Dict[str, Any]] = None
    youtube: Optional[Dict[str, Any]] = None
    instagram: Optional[Dict[str, Any]] = None

class CreateVideoOutput(BaseModel):
    project_id: Optional[str] = None
    status: Optional[str] = None
    message: Optional[str] = None
    
class VideoStatusOutput(BaseModel):
    project_id: Optional[str] = None
    status: Optional[str] = None
    video_url: Optional[str] = None
    error: Optional[str] = None
    
class ProjectListOutput(BaseModel):
    projects: List[Dict[str, Any]] = []
    
class QueueOutput(BaseModel):
    success: Optional[bool] = None
    message: Optional[str] = None
    
class PublishOutput(BaseModel):
    success: Optional[bool] = None
    message: Optional[str] = None
    
class ApiResponse(BaseModel):
    data: Union[
        CreateVideoOutput,
        VideoStatusOutput,
        ProjectListOutput,
        QueueOutput,
        PublishOutput,
        Dict[str, Any]
    ]
    component: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None