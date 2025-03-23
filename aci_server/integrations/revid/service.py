from typing import Optional, List, Dict, Any, Union
from .client import RevidAIClient
from .schema import (
    ApiResponse,
    CreateVideoInput,
    CreateVideoOutput,
    VideoStatusInput,
    VideoStatusOutput,
    ProjectsListInput,
    ProjectListOutput,
    QueueInput,
    QueueOutput,
    PublishInput,
    PublishOutput,
    VoiceListInput,
    VoiceListOutput,
    VoiceInfo
)
import os
import json
from ..common.component_handler import load_components, prepare_components_auto
from fastapi import HTTPException


class RevidAIService:
    def __init__(self, client: RevidAIClient):
        self.client = client
        self.components_data = self._load_components()
        self._voices_data = self._load_voices_data()

    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
        
    def _load_voices_data(self) -> List[Dict[str, Any]]:
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            voices_file_path = os.path.join(current_dir, "utils", "voices.json")
            with open(voices_file_path, 'r') as file:
                return json.load(file)
        except Exception as e:
            return []
            
    def prepare_response(self, data: Any, component_name: str = None) -> ApiResponse:
        tool_name = "revid"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)
    
    def get_voice_list(self, params: VoiceListInput) -> ApiResponse:
        voices = []
        
        for voice_data in self._voices_data:
            if params.category and voice_data.get("category") != params.category:
                continue
                
            labels = voice_data.get("labels", {})
            if params.gender and labels.get("gender") != params.gender:
                continue
                
            voice_info = VoiceInfo(
                voice_id=voice_data.get("voice_id", ""),
                name=voice_data.get("name", ""),
                category=voice_data.get("category", ""),
                preview_url=voice_data.get("preview_url")
            )
            
            # Add label information if available
            if labels:
                voice_info.accent = labels.get("accent")
                voice_info.description = labels.get("description")
                voice_info.age = labels.get("age")
                voice_info.gender = labels.get("gender")
                voice_info.use_case = labels.get("use_case")
                
            voices.append(voice_info)
            
        output = VoiceListOutput(voices=voices)
        return self.prepare_response(output)
    
    def create_tiktok_video(self, params: CreateVideoInput) -> ApiResponse:
        payload = {
            "webhook": params.webhook,
            "creationParams": {
                "inputText": params.input_text,
                "hasToGenerateVoice": bool(params.selected_voice),
                "selectedVoice": params.selected_voice,
                "hasToSearchMedia": True,
                "mediaType": params.media_type,
                "generationPreset": params.generation_preset,
                "generationUserPrompt": params.generation_user_prompt,
                "hasEnhancedGeneration": True,
                "audioUrl": params.audio_url,
                "captionPresetName": params.caption_preset_name,
                "hasAvatar": params.has_avatar,
                "selectedAvatar": params.selected_avatar,
                "flowType": "text-to-video",
                "ratio": params.ratio,
                "hasToGenerateVideos": True
            }
        }
        
        response = self.client.create_video(payload)
        parsed_response = self._parse_create_video_response(response)
        return self.prepare_response(parsed_response)
        
    def get_video_status(self, params: VideoStatusInput) -> ApiResponse:
        response = self.client.get_status(params.project_id)
        parsed_response = self._parse_status_response(response)
        return self.prepare_response(parsed_response)
        
    def get_projects_list(self, params: ProjectsListInput) -> ApiResponse:
        response = self.client.get_projects(params.limit)
        parsed_response = self._parse_projects_response(response)
        return self.prepare_response(parsed_response)
        
    def add_to_queue(self, params: QueueInput) -> ApiResponse:
        payload = {
            "videoUrl": params.video_url,
            "channelName": params.channel_name,
            "tiktok": params.tiktok,
            "youtube": params.youtube,
            "instagram": params.instagram
        }
        response = self.client.add_to_queue(payload)
        parsed_response = self._parse_queue_response(response)
        return self.prepare_response(parsed_response)
        
    def publish_video(self, params: PublishInput) -> ApiResponse:
        payload = {
            "videoUrl": params.video_url,
            "channelName": params.channel_name,
            "tiktok": params.tiktok,
            "youtube": params.youtube,
            "instagram": params.instagram
        }
        response = self.client.publish_now(payload)
        parsed_response = self._parse_publish_response(response)
        return self.prepare_response(parsed_response)
        
    def _parse_create_video_response(self, response) -> CreateVideoOutput:
        if response.status_code != 200:
            data = response.json() if response.content else {}
            if isinstance(data, dict) and data.get('success') == 0 and data.get('error') == 'No active subscription found':
                raise HTTPException(status_code=403, detail="No active subscription found for Revid AI")
            
            error_msg = data.get('error', f"Error: {response.status_code}") if isinstance(data, dict) else f"Error: {response.status_code}"
            raise HTTPException(status_code=response.status_code, detail=error_msg)
            
        data = response.json() if response.content else {}
        return CreateVideoOutput(
            project_id=data.get("pid"),
            status=data.get("status"),
            message=data.get("message", "Video creation initiated")
        )
        
    def _parse_status_response(self, response) -> VideoStatusOutput:
        if response.status_code != 200:
            data = response.json() if response.content else {}
            error_msg = data.get('error', f"Error: {response.status_code}") if isinstance(data, dict) else f"Error: {response.status_code}"
            raise HTTPException(status_code=response.status_code, detail=error_msg)
            
        data = response.json() if response.content else {}
        return VideoStatusOutput(
            project_id=data.get("pid"),
            status=data.get("status"),
            video_url=data.get("videoUrl"),
            error=data.get("error")
        )
        
    def _parse_projects_response(self, response) -> ProjectListOutput:
        if response.status_code != 200:
            data = response.json() if response.content else {}
            error_msg = data.get('error', f"Error: {response.status_code}") if isinstance(data, dict) else f"Error: {response.status_code}"
            raise HTTPException(status_code=response.status_code, detail=error_msg)
            
        data = response.json() if response.content else {}
        return ProjectListOutput(
            projects=data.get("projects", [])
        )
        
    def _parse_queue_response(self, response) -> QueueOutput:
        if response.status_code != 200:
            data = response.json() if response.content else {}
            error_msg = data.get('error', f"Error: {response.status_code}") if isinstance(data, dict) else f"Error: {response.status_code}"
            raise HTTPException(status_code=response.status_code, detail=error_msg)
            
        data = response.json() if response.content else {}
        return QueueOutput(
            success=data.get("success", True),
            message=data.get("message", "Added to queue")
        )
        
    def _parse_publish_response(self, response) -> PublishOutput:
        if response.status_code != 200:
            data = response.json() if response.content else {}
            error_msg = data.get('error', f"Error: {response.status_code}") if isinstance(data, dict) else f"Error: {response.status_code}"
            raise HTTPException(status_code=response.status_code, detail=error_msg)
            
        data = response.json() if response.content else {}
        return PublishOutput(
            success=data.get("success", True),
            message=data.get("message", "Published successfully")
        )