from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union, Literal

# Input Schemas
class ListAvatarsParams(BaseModel):
    pass  # No parameters needed for this endpoint

class ListVoicesParams(BaseModel):
    pass  # No parameters needed for this endpoint

class ListAvatarGroupsParams(BaseModel):
    include_public: Optional[bool] = Field(
        False,
        description="Whether to include all public avatar groups"
    )

class ListGroupAvatarsParams(BaseModel):
    group_id: str = Field(..., description="Avatar group id")

# Response Models
class Avatar(BaseModel):
    avatar_id: str
    avatar_name: str
    gender: str
    preview_image_url: str
    preview_video_url: str
    premium: bool

class TalkingPhoto(BaseModel):
    talking_photo_id: str
    talking_photo_name: str
    preview_image_url: str

class ListAvatarsResponse(BaseModel):
    avatars: List[Avatar]
    talking_photos: List[TalkingPhoto]

class Voice(BaseModel):
    voice_id: str
    language: str
    gender: str
    name: str
    preview_audio: str
    support_pause: bool
    emotion_support: bool

class ListVoicesResponse(BaseModel):
    voices: list[Voice]

class ListVoicesResponseWrapper(BaseModel):
    data: ListVoicesResponse

class AvatarGroup(BaseModel):
    # Define fields based on actual API response
    group_id: str
    name: str

class ListAvatarGroupsResponse(BaseModel):
    groups: List[AvatarGroup]

class ListGroupAvatarsResponse(BaseModel):
    avatars: List[Avatar]

# Video Generation Models
class Dimension(BaseModel):
    width: int = Field(..., ge=1, le=3840)
    height: int = Field(..., ge=1, le=2160)

class Offset(BaseModel):
    x: float = Field(0.0, ge=-1.0, le=1.0)
    y: float = Field(0.0, ge=-1.0, le=1.0)

class AvatarSettings(BaseModel):
    type: Literal["avatar"] = "avatar"
    avatar_id: str
    scale: float = Field(1.0, ge=0.0, le=5.0)
    avatar_style: Optional[Literal["circle", "normal", "closeUp"]] = None
    offset: Optional[Offset] = None
    matting: Optional[bool] = None
    circle_background_color: Optional[str] = None

class TalkingPhotoSettings(BaseModel):
    type: Literal["talking_photo"] = "talking_photo"
    talking_photo_id: str
    scale: float = Field(1.0, ge=0.0, le=2.0)
    talking_photo_style: Optional[Literal["square", "circle"]] = None
    offset: Optional[Offset] = None
    talking_style: Literal["stable", "expressive"] = "stable"
    expression: Literal["default", "happy"] = "default"
    super_resolution: Optional[bool] = None
    matting: Optional[bool] = None
    circle_background_color: Optional[str] = None

class TextVoiceSettings(BaseModel):
    type: Literal["text"] = "text"
    voice_id: str
    input_text: str
    speed: Optional[float] = Field(1.0, ge=0.5, le=1.5)
    pitch: Optional[int] = Field(0, ge=-50, le=50)
    emotion: Optional[Literal["Excited", "Friendly", "Serious", "Soothing", "Broadcaster"]] = None
    locale: Optional[str] = None

class AudioVoiceSettings(BaseModel):
    type: Literal["audio"] = "audio"
    audio_url: Optional[str] = None
    audio_asset_id: Optional[str] = None

class SilenceVoiceSettings(BaseModel):
    type: Literal["silence"] = "silence"
    duration: float = Field(1.0, ge=1.0, le=100.0)

class ColorBackground(BaseModel):
    type: Literal["color"] = "color"
    value: str = "#f6f6fc"

class ImageBackground(BaseModel):
    type: Literal["image"] = "image"
    url: Optional[str] = None
    image_asset_id: Optional[str] = None
    fit: Optional[Literal["cover", "crop", "contain", "none"]] = "cover"

class VideoBackground(BaseModel):
    type: Literal["video"] = "video"
    url: Optional[str] = None
    video_asset_id: Optional[str] = None
    play_style: Literal["fit_to_scene", "freeze", "loop", "once"]
    fit: Optional[Literal["cover", "crop", "contain", "none"]] = "cover"

class VideoInput(BaseModel):
    character: Optional[Union[AvatarSettings, TalkingPhotoSettings]] = None
    voice: Union[TextVoiceSettings, AudioVoiceSettings, SilenceVoiceSettings]
    background: Optional[Union[ColorBackground, ImageBackground, VideoBackground]] = None

class GenerateVideoParams(BaseModel):
    caption: Optional[bool] = False
    title: Optional[str] = None
    callback_id: Optional[str] = None
    video_inputs: List[VideoInput] = Field(..., min_items=1, max_items=50)
    dimension: Dimension
    folder_id: Optional[str] = None
    callback_url: Optional[str] = None

class VideoStatusParams(BaseModel):
    video_id: str

class DeleteVideoParams(BaseModel):
    video_id: str

class VideoResponse(BaseModel):
    video_id: str

class VideoStatus(BaseModel):
    id: str
    status: str
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    gif_url: Optional[str] = None
    error: Optional[Dict[str, Any]] = None

class DeleteVideoResponse(BaseModel):
    success: bool
    message: str

class GenerateWebMParams(BaseModel):
    avatar_pose_id: str = Field(
        "Vanessa-invest-20220722",
        description="The ID of the avatar's pose"
    )
    avatar_style: Literal["circle", "closeUp", "normal", "voiceOnly"] = Field(
        "normal",
        description="The style of the avatar"
    )
    input_text: Optional[str] = Field(
        "This is a WebM video generated by HeyGen API",
        description="The text that the avatar will speak"
    )
    voice_id: Optional[str] = Field(
        "1bd001e7e50f421d891986aad5158bc8",
        description="The ID of the voice to use"
    )
    input_audio: Optional[str] = Field(
        None,
        description="Input audio URL. Specify either input_text/voice_id or input_audio"
    )
    dimension: Dimension

class WebMVideoResponse(BaseModel):
    code: int
    data: Dict[str, str]
    msg: Optional[str] = None
    message: Optional[str] = None

# Video List Models
class VideoListParams(BaseModel):
    limit: Optional[int] = Field(None, ge=0, le=100)
    folder_id: Optional[str] = None
    title: Optional[str] = None
    token: Optional[str] = None

class VideoInfo(BaseModel):
    video_id: str
    status: str
    created_at: int
    type: Literal["GENERATED", "TRANSLATED"]
    folder_id: str

class VideoListResponse(BaseModel):
    code: int
    data: Dict[str, Any]  # Contains token, total, and videos list
    message: Optional[str] = None

# Share URL Models
class ShareVideoParams(BaseModel):
    video_id: str

class ShareVideoResponse(BaseModel):
    url: str

# Template Models
class Template(BaseModel):
    template_id: str
    name: str
    thumbnail_image_url: str
    aspect_ratio: Literal["portrait", "landscape"]

class ListTemplatesResponse(BaseModel):
    templates: List[Template]

class VariableProperty(BaseModel):
    content: Optional[str] = None
    url: Optional[str] = None
    asset_id: Optional[str] = None
    fit: Optional[str] = None
    play_style: Optional[str] = None
    character_id: Optional[str] = None
    type: Optional[str] = None
    voice_id: Optional[str] = None

class Variable(BaseModel):
    name: str
    type: str
    properties: VariableProperty

class TemplateDetailsResponse(BaseModel):
    variables: Dict[str, Variable]

class GenerateFromTemplateParams(BaseModel):
    template_id: str = Field(..., description="ID of the template to use")
    caption: bool = False
    callback_id: Optional[str] = None
    title: str = "Untitled Video"
    dimension: Optional[Dimension] = None
    include_gif: bool = False
    enable_sharing: bool = False
    folder_id: Optional[str] = None
    brand_voice_id: Optional[str] = None
    variables: Dict[str, Variable]

# Translation Models
class SupportedLanguagesResponse(BaseModel):
    languages: List[str]

class TranslateVideoParams(BaseModel):
    video_url: str = Field(..., description="URL of the video file to be translated")
    title: Optional[str] = None
    output_language: str = Field(..., description="Target language for translation")
    translate_audio_only: Optional[bool] = Field(False, description="Translate only audio")
    speaker_num: Optional[int] = None
    callback_id: Optional[str] = None
    enable_dynamic_duration: Optional[bool] = None
    brand_voice_id: Optional[str] = None
    callback_url: Optional[str] = None

class TranslateVideoResponse(BaseModel):
    video_translate_id: str

class TranslationStatusParams(BaseModel):
    video_translate_id: str

class TranslationStatus(BaseModel):
    video_translate_id: str
    title: str
    status: Literal["running", "success", "failed", "pending"]
    url: Optional[str] = None
    message: Optional[str] = None

class TranslateCaptionParams(BaseModel):
    video_translate_id: str
    caption_type: Literal["vtt"] = "vtt"

class TranslateCaptionResponse(BaseModel):
    caption_url: str

# Photo Avatar Models
class GeneratePhotoAvatarParams(BaseModel):
    name: str = Field(..., description="Name of the photo avatar")
    age: str = Field(..., description="Age of the avatar")
    gender: str = Field(..., description="Gender of the avatar")
    ethnicity: str = Field(..., description="Ethnicity of the avatar")
    orientation: str = Field(..., description="Orientation of the avatar")
    pose: str = Field(..., description="Pose of the avatar")
    style: str = Field(..., description="Style of the avatar")
    appearance: str = Field(..., max_length=1000, description="Description/Prompt of the generated avatar photo")

class GeneratePhotoAvatarResponse(BaseModel):
    generation_id: str

class GenerationStatusParams(BaseModel):
    generation_id: str

class GenerationStatus(BaseModel):
    status: str
    images: Optional[List[str]] = None
    image_keys: Optional[List[str]] = None
    message: Optional[str] = None

class PhotoAvatarActionParams(BaseModel):
    id: str = Field(..., description="Photo avatar id")

class PhotoAvatarActionResponse(BaseModel):
    id: str = Field(..., description="New photo avatar id")

class PhotoAvatarDetailsParams(BaseModel):
    id: str = Field(..., description="Photo avatar id")

class PhotoAvatarDetails(BaseModel):
    id: str
    name: str
    preview_image_url: str
    # Add other fields based on actual API response
    created_at: Optional[int] = None
    has_motion: Optional[bool] = None
    has_sound_effect: Optional[bool] = None


class TemplateDetailsParams(BaseModel):
    template_id: str

class ComponentInfo(BaseModel):
    name: str

# User Info schemas
class UserInfoResponse(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str

class UserInfoResponseWrapper(BaseModel):
    data: UserInfoResponse

# Quota schemas
class QuotaDetails(BaseModel):
    video: int
    interactive: int

class RemainingQuotaResponse(BaseModel):
    remaining_quota: int
    details: QuotaDetails

class RemainingQuotaResponseWrapper(BaseModel):
    data: RemainingQuotaResponse

# Asset schemas
class UploadAssetParams(BaseModel):
    file_path: str
    content_type: str

class AssetMeta(BaseModel):
    width: Optional[int] = None
    height: Optional[int] = None

class AssetResponse(BaseModel):
    id: str
    name: str
    file_type: str
    folder_id: Optional[str] = None
    meta: Optional[AssetMeta] = None
    image_key: Optional[str] = None

class AssetResponseWrapper(BaseModel):
    data: AssetResponse

# Folder schemas
class ListFoldersParams(BaseModel):
    limit: Optional[int] = 10
    parent_id: Optional[str] = None
    is_trash: Optional[bool] = False

class Folder(BaseModel):
    id: str
    name: str
    project_type: str
    parent_id: Optional[str] = None
    created_at: Optional[int] = None
    updated_at: Optional[int] = None

class ListFoldersResponse(BaseModel):
    folders: list[Folder]
    token: Optional[str] = None

class ListFoldersResponseWrapper(BaseModel):
    data: ListFoldersResponse

class CreateFolderParams(BaseModel):
    name: str
    project_type: str
    parent_id: Optional[str] = None

class CreateFolderResponse(BaseModel):
    id: str
    name: str
    project_type: str
    parent_id: Optional[str] = None

class CreateFolderResponseWrapper(BaseModel):
    data: CreateFolderResponse

# Add this wrapper class with the other response wrappers
class ListAvatarsResponseWrapper(BaseModel):
    data: ListAvatarsResponse

class ApiResponse(BaseModel):
    data: Union[
        ListAvatarsResponse,
        ListVoicesResponse,
        ListAvatarGroupsResponse,
        ListGroupAvatarsResponse,
        VideoResponse,
        VideoStatus,
        DeleteVideoResponse,
        WebMVideoResponse,
        VideoListResponse,
        ShareVideoResponse,
        ListTemplatesResponse,
        TemplateDetailsResponse,
        SupportedLanguagesResponse,
        TranslateVideoResponse,
        TranslationStatus,
        TranslateCaptionResponse,
        GeneratePhotoAvatarResponse,
        GenerationStatus,
        PhotoAvatarActionResponse,
        PhotoAvatarDetails,
        RemainingQuotaResponseWrapper,
        AssetResponseWrapper,
        ListFoldersResponseWrapper,
        CreateFolderResponseWrapper,
        UserInfoResponseWrapper,
        ListAvatarsResponseWrapper
    ]
    component: Optional[Dict[str, Any]] = None