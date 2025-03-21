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
    has_avatar: Optional[bool] = False,
    selected_avatar: Optional[str] = None
    
    
class CreateVideoOutput(BaseModel):
    pass

    
class ApiResponse(BaseModel):
    data: Union[
        CreateVideoOutput
        Dict[str, Any]
    ]
    component: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None