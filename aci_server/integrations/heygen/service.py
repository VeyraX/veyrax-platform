from typing import Dict, Any
import os
from .client import HeygenClient
from .schema import (
    ListAvatarsParams,
    ListVoicesParams,
    ListAvatarGroupsParams,
    ListGroupAvatarsParams,
    ListAvatarsResponse,
    ListVoicesResponse,
    ListAvatarGroupsResponse,
    ListGroupAvatarsResponse,
    ApiResponse,
    VideoResponse,
    VideoStatus,
    DeleteVideoResponse,
    GenerateVideoParams,
    VideoStatusParams,
    DeleteVideoParams,
    GenerateWebMParams,
    WebMVideoResponse,
    VideoListParams,
    VideoListResponse,
    ShareVideoParams,
    ShareVideoResponse,
    ListTemplatesResponse,
    TemplateDetailsResponse,
    GenerateFromTemplateParams,
    SupportedLanguagesResponse,
    TranslateVideoParams,
    TranslateVideoResponse,
    TranslationStatusParams,
    TranslationStatus,
    TranslateCaptionParams,
    TranslateCaptionResponse,
    PhotoAvatarDetailsParams,
    PhotoAvatarDetails,
    PhotoAvatarActionParams,
    PhotoAvatarActionResponse,
    GeneratePhotoAvatarParams,
    GeneratePhotoAvatarResponse,
    GenerationStatusParams,
    GenerationStatus,
    UserInfoResponse,
    RemainingQuotaResponse,
    UploadAssetParams,
    AssetResponse,
    ListFoldersParams,
    ListFoldersResponse,
    CreateFolderParams,
    CreateFolderResponse,
    ListAvatarsResponseWrapper,
    ComponentInfo
)
from ..common.component_handler import load_components, prepare_components_auto

class HeygenService:
    def __init__(self, client: HeygenClient):
        self.client = client
        self.components_data = self._load_components()

    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)

    def prepare_response(self, data: Any, component_name: str = None) -> ApiResponse:
        tool_name = "heygen"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)

    def list_avatars(self, params: ListAvatarsParams) -> ApiResponse:
        response = self.client.list_avatars()
        
        if "avatars" not in response:
            response["avatars"] = []
        if "talking_photos" not in response:
            response["talking_photos"] = []

        validated = ListAvatarsResponse(**response)
        return self.prepare_response(validated, "AvatarList")

    def list_voices(self, params: ListVoicesParams) -> ApiResponse:
        response = self.client.list_voices()
        validated = ListVoicesResponse(**response)
        return self.prepare_response(validated, "VoiceList")

    def list_avatar_groups(self, params: ListAvatarGroupsParams) -> ApiResponse:
        response = self.client.list_avatar_groups(params.include_public)
        validated = ListAvatarGroupsResponse(**response)
        return self.prepare_response(validated, "AvatarGroupList")

    def list_group_avatars(self, params: ListGroupAvatarsParams) -> ApiResponse:
        response = self.client.list_group_avatars(params.group_id)
        validated = ListGroupAvatarsResponse(**response)
        return self.prepare_response(validated, "GroupAvatarList")

    def generate_video(self, params: GenerateVideoParams) -> ApiResponse:
        response = self.client.generate_video(params.model_dump(exclude_none=True))
        validated = VideoResponse(**response)
        return self.prepare_response(validated, "VideoGeneration")

    def get_video_status(self, params: VideoStatusParams) -> ApiResponse:
        response = self.client.get_video_status(params.video_id)
        validated = VideoStatus(**response["data"])
        return self.prepare_response(validated, "VideoStatus")

    def delete_video(self, params: DeleteVideoParams) -> ApiResponse:
        response = self.client.delete_video(params.video_id)
        validated = DeleteVideoResponse(success=True, message="Video deleted successfully")
        return self.prepare_response(validated, "VideoDelete")

    def generate_webm(self, params: GenerateWebMParams) -> ApiResponse:
        if params.input_text and params.input_audio:
            raise ValueError("Cannot specify both input_text and input_audio")
        if not params.input_text and not params.input_audio:
            raise ValueError("Must specify either input_text or input_audio")
            
        response = self.client.generate_webm(params.model_dump(exclude_none=True))
        validated = WebMVideoResponse(**response)
        return self.prepare_response(validated, "WebMGeneration")

    def list_videos(self, params: VideoListParams) -> ApiResponse:
        response = self.client.list_videos(params.model_dump(exclude_none=True))
        validated = VideoListResponse(**response)
        return self.prepare_response(validated, "VideoList")

    def share_video(self, params: ShareVideoParams) -> ApiResponse:
        response = self.client.share_video(params.video_id)
        validated = ShareVideoResponse(**response)
        return self.prepare_response(validated, "VideoShare")

    def list_templates(self) -> ApiResponse:
        response = self.client.list_templates()
        validated = ListTemplatesResponse(**response)
        return self.prepare_response(validated, "TemplateList")

    def get_template_details(self, template_id: str) -> ApiResponse:
        response = self.client.get_template_details(template_id)
        validated = TemplateDetailsResponse(**response)
        return self.prepare_response(validated, "TemplateDetails")

    def generate_from_template(self, params: GenerateFromTemplateParams) -> ApiResponse:
        template_id = params.template_id
        request_params = params.model_dump(exclude={"template_id"}, exclude_none=True)
        response = self.client.generate_from_template(template_id, request_params)
        validated = VideoResponse(**response)
        return self.prepare_response(validated, "TemplateGeneration")

    def get_supported_languages(self) -> ApiResponse:
        response = self.client.get_supported_languages()
        validated = SupportedLanguagesResponse(**response)
        return self.prepare_response(validated, "TranslationLanguages")

    def translate_video(self, params: TranslateVideoParams) -> ApiResponse:
        response = self.client.translate_video(params.model_dump(exclude_none=True))
        validated = TranslateVideoResponse(**response)
        return self.prepare_response(validated, "VideoTranslation")

    def get_translation_status(self, params: TranslationStatusParams) -> ApiResponse:
        response = self.client.get_translation_status(params.video_translate_id)
        validated = TranslationStatus(**response["data"])
        return self.prepare_response(validated, "TranslationStatus")

    def get_translation_caption(self, params: TranslateCaptionParams) -> ApiResponse:
        response = self.client.get_translation_caption(params.model_dump())
        validated = TranslateCaptionResponse(**response["data"])
        return self.prepare_response(validated, "TranslationCaption")

    def get_photo_avatar_details(self, params: PhotoAvatarDetailsParams) -> ApiResponse:
        """Get photo avatar details"""
        response = self.client.get_photo_avatar_details(params.id)
        validated = PhotoAvatarDetails(**response)
        return self.prepare_response(validated, "PhotoAvatarDetails")

    def upscale_avatar(self, params: PhotoAvatarActionParams) -> ApiResponse:
        """Upscale a photo avatar"""
        response = self.client.upscale_avatar(params.id)
        validated = PhotoAvatarActionResponse(**response)
        return self.prepare_response(validated, "PhotoAvatarUpscale")

    def generate_photo_avatar(self, params: GeneratePhotoAvatarParams) -> ApiResponse:
        """Generate photo avatar photos"""
        response = self.client.generate_photo_avatar(params.model_dump(exclude_none=True))
        validated = GeneratePhotoAvatarResponse(**response)
        return self.prepare_response(validated, "PhotoAvatarGeneration")

    def get_generation_status(self, params: GenerationStatusParams) -> ApiResponse:
        """Check photo/look generation status"""
        response = self.client.get_generation_status(params.generation_id)
        validated = GenerationStatus(**response)
        return self.prepare_response(validated, "GenerationStatus")

    def add_motion(self, params: PhotoAvatarActionParams) -> ApiResponse:
        """Add motion to a photo avatar"""
        response = self.client.add_motion(params.id)
        validated = PhotoAvatarActionResponse(**response)
        return self.prepare_response(validated, "PhotoAvatarMotion")

    def add_sound_effect(self, params: PhotoAvatarActionParams) -> ApiResponse:
        """Add sound effect to a photo avatar"""
        response = self.client.add_sound_effect(params.id)
        validated = PhotoAvatarActionResponse(**response)
        return self.prepare_response(validated, "PhotoAvatarSoundEffect")

    def get_user_info(self) -> ApiResponse:
        """Get current user information"""
        response = self.client.get_user_info()
        validated = UserInfoResponse(**response)
        return self.prepare_response(validated, "UserInfo")

    def get_remaining_quota(self) -> ApiResponse:
        """Get remaining quota"""
        response = self.client.get_remaining_quota()
        validated = RemainingQuotaResponse(**response)
        return self.prepare_response(validated, "RemainingQuota")

    def upload_asset(self, params: UploadAssetParams) -> ApiResponse:
        """Upload an asset (image, video, audio)"""
        response = self.client.upload_asset(params.file_path, params.content_type)
        validated = AssetResponse(**response)
        return self.prepare_response(validated, "UploadedAsset")

    def list_folders(self, params: ListFoldersParams) -> ApiResponse:
        """List folders"""
        response = self.client.list_folders(params.model_dump(exclude_none=True))
        validated = ListFoldersResponse(**response)
        return self.prepare_response(validated, "FolderList")

    def create_folder(self, params: CreateFolderParams) -> ApiResponse:
        """Create a new folder"""
        response = self.client.create_folder(params.model_dump(exclude_none=True))
        validated = CreateFolderResponse(**response)
        return self.prepare_response(validated, "FolderCreated")
