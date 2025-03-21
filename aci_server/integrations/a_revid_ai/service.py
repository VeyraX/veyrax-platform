
from typing import Optional, List, Dict, Any, Union
from .client import RevidAIClient
from .schema import (
    ApiResponse,
    CreateVideoInput
)
import os
from ..common.component_handler import load_components, prepare_components_auto

class RevidAIService:
    def __init__(self, client: RevidAIClient):
        self.client = client
        self.components_data = self._load_components()

    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
        
    def prepare_response(self, data: Any, component_name: str = None) -> ApiResponse:
        tool_name = "asana"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)
    
    def create_tiktok_video(self, params: CreateVideoInput):
        payload = {
            "webhook": params.webhook,
            "creationParams": {
                "inputText": params.input_text,
                "hasToGenerateVoice": bool(params.selected_voice),
                "selectedVoice": params.selected_voice,
                "hasToSearchMedia": True,
                "mediaType": "stockVideo",
                "generationPreset": "REALISM",
                "generationUserPrompt": params.generation_user_prompt,
                "hasEnhancedGeneration": True,
                "audioUrl": params.audio_url,
                "captionPresetName": params.caption_preset_name,
                "hasAvatar": params.has_avatar,
                "selectedAvatar": params.selected_avatar,
                "flowType": "text-to-video",
                "ratio": "9 / 16",
                "hasToGenerateVideos": False
            }
        }
        return self.client.create_video(payload)