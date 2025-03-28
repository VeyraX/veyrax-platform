from fastapi import APIRouter, Body, Depends, HTTPException
from starlette.requests import Request as FastAPIRequest
from typing import Dict, Any
from .schema import (
    # Input schemas
    ListAvatarsParams,
    ListVoicesParams,
    ListAvatarGroupsParams,
    ListGroupAvatarsParams,
    GenerateVideoParams,
    VideoStatusParams,
    DeleteVideoParams,
    GenerateWebMParams,
    VideoListParams,
    ShareVideoParams,
    GenerateFromTemplateParams,
    TemplateDetailsParams,
    TranslateVideoParams,
    TranslationStatusParams,
    TranslateCaptionParams,
    GeneratePhotoAvatarParams,
    GenerationStatusParams,
    PhotoAvatarActionParams,
    PhotoAvatarDetailsParams,
    
    # Response schemas
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
    
    # Base response
    ApiResponse,
    UserInfoResponse,
    RemainingQuotaResponse,
    UploadAssetParams,
    AssetResponse,
    ListFoldersParams,
    ListFoldersResponse,
    CreateFolderParams,
    CreateFolderResponse
)
from .service import HeygenService
from .client import HeygenClient
from ..common.auth import validate_provider_api_key
from ..common.input_schema_decorator import schema
from ..common.utils import apply_error_handler_to_service, apply_error_handler_to_router
from ..common.examples_handler import ExamplesLoader

router = APIRouter(prefix="/heygen", tags=["heygen"])
examples = ExamplesLoader()

async def get_heygen_service(request: FastAPIRequest):
    try:
        api_key = await validate_provider_api_key(request, "heygen")
        client = HeygenClient(api_key)
        service = HeygenService(client)
        apply_error_handler_to_service(service)
        return service
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Failed to initialize Heygen service: {str(e)}"
        )

@router.post("/list_avatars", response_model=ApiResponse)
@schema(
    input_schema_class=ListAvatarsParams,
    output_schema_class=ListAvatarsResponse,
    examples=examples["/heygen/list_avatars"]
)
async def list_avatars(
    params: Dict[str, Any] = Body(...),
    service: HeygenService = Depends(get_heygen_service)
):
    validated_params = ListAvatarsParams(**params)
    return service.list_avatars(validated_params)

@router.post("/list_voices", response_model=ApiResponse)
@schema(
    input_schema_class=ListVoicesParams,
    output_schema_class=ListVoicesResponse,
    examples=examples["/heygen/list_voices"]
)
async def list_voices(
    params: Dict[str, Any] = Body(...),
    service: HeygenService = Depends(get_heygen_service)
):
    validated_params = ListVoicesParams(**params)
    return service.list_voices(validated_params)

@router.post("/list_avatar_groups", response_model=ApiResponse)
@schema(
    input_schema_class=ListAvatarGroupsParams,
    output_schema_class=ListAvatarGroupsResponse,
    examples=examples["/heygen/list_avatar_groups"]
)
async def list_avatar_groups(
    params: Dict[str, Any] = Body(...),
    service: HeygenService = Depends(get_heygen_service)
):
    validated_params = ListAvatarGroupsParams(**params)
    return service.list_avatar_groups(validated_params)

@router.post("/list_group_avatars", response_model=ApiResponse)
@schema(
    input_schema_class=ListGroupAvatarsParams,
    output_schema_class=ListGroupAvatarsResponse,
    examples=examples["/heygen/list_group_avatars"]
)
async def list_group_avatars(
    params: Dict[str, Any] = Body(...),
    service: HeygenService = Depends(get_heygen_service)
):
    validated_params = ListGroupAvatarsParams(**params)
    return service.list_group_avatars(validated_params)

@router.post("/validate_key")
async def validate_key(params: Dict[str, Any] = Body(...)):
    try:
        api_key = params.get("api_key")
        if not api_key:
            return {"valid": False, "message": "API key is required"}
        
        client = HeygenClient(api_key)
        client.list_avatars()  # Test API key with a simple request
        return {"valid": True, "message": "API key is valid"}
    except Exception as e:
        return {"valid": False, "message": "Invalid API key"}

@router.post("/generate_video", response_model=ApiResponse)
@schema(
    input_schema_class=GenerateVideoParams,
    output_schema_class=VideoResponse,
    examples=examples["/heygen/generate_video"]
)
async def generate_video(
    params: Dict[str, Any] = Body(...),
    service: HeygenService = Depends(get_heygen_service)
):
    validated_params = GenerateVideoParams(**params)
    return service.generate_video(validated_params)

@router.post("/video_status", response_model=ApiResponse)
@schema(
    input_schema_class=VideoStatusParams,
    output_schema_class=VideoStatus,
    examples=examples["/heygen/video_status"]
)
async def get_video_status(
    params: Dict[str, Any] = Body(...),
    service: HeygenService = Depends(get_heygen_service)
):
    validated_params = VideoStatusParams(**params)
    return service.get_video_status(validated_params)

@router.post("/delete_video", response_model=ApiResponse)
@schema(
    input_schema_class=DeleteVideoParams,
    output_schema_class=DeleteVideoResponse,
    examples=examples["/heygen/delete_video"]
)
async def delete_video(
    params: Dict[str, Any] = Body(...),
    service: HeygenService = Depends(get_heygen_service)
):
    validated_params = DeleteVideoParams(**params)
    return service.delete_video(validated_params)

@router.post("/generate_webm", response_model=ApiResponse)
@schema(
    input_schema_class=GenerateWebMParams,
    output_schema_class=WebMVideoResponse,
    examples=examples["/heygen/generate_webm"]
)
async def generate_webm(
    params: Dict[str, Any] = Body(...),
    service: HeygenService = Depends(get_heygen_service)
):
    validated_params = GenerateWebMParams(**params)
    return service.generate_webm(validated_params)

@router.post("/list_videos", response_model=ApiResponse)
@schema(
    input_schema_class=VideoListParams,
    output_schema_class=VideoListResponse,
    examples=examples["/heygen/list_videos"]
)
async def list_videos(
    params: Dict[str, Any] = Body(...),
    service: HeygenService = Depends(get_heygen_service)
):
    validated_params = VideoListParams(**params)
    return service.list_videos(validated_params)

@router.post("/share_video", response_model=ApiResponse)
@schema(
    input_schema_class=ShareVideoParams,
    output_schema_class=ShareVideoResponse,
    examples=examples["/heygen/share_video"]
)
async def share_video(
    params: Dict[str, Any] = Body(...),
    service: HeygenService = Depends(get_heygen_service)
):
    validated_params = ShareVideoParams(**params)
    return service.share_video(validated_params)

@router.get("/templates", response_model=ApiResponse)
@schema(
    output_schema_class=ListTemplatesResponse,
    examples=examples["/heygen/list_templates"]
)
async def list_templates(
    service: HeygenService = Depends(get_heygen_service)
):
    return service.list_templates()

@router.post("/template_details", response_model=ApiResponse)
@schema(
    input_schema_class=TemplateDetailsParams,
    output_schema_class=TemplateDetailsResponse,
    examples=examples["/heygen/template_details"]
)
async def get_template_details(
    params: Dict[str, Any] = Body(...),
    service: HeygenService = Depends(get_heygen_service)
):
    validated_params = TemplateDetailsParams(**params)
    return service.get_template_details(validated_params)

@router.post("/generate_from_template", response_model=ApiResponse)
@schema(
    input_schema_class=GenerateFromTemplateParams,
    output_schema_class=VideoResponse,
    examples=examples["/heygen/generate_from_template"]
)
async def generate_from_template(
    params: Dict[str, Any] = Body(...),
    service: HeygenService = Depends(get_heygen_service)
):
    validated_params = GenerateFromTemplateParams(**params)
    return service.generate_from_template(validated_params)

@router.post("/get_translation_languages", response_model=ApiResponse)
@schema(
    output_schema_class=SupportedLanguagesResponse,
    examples=examples["/heygen/get_translation_languages"]
)
async def get_translation_languages(
    service: HeygenService = Depends(get_heygen_service)
):
    return service.get_supported_languages()

@router.post("/translate_video", response_model=ApiResponse)
@schema(
    input_schema_class=TranslateVideoParams,
    output_schema_class=TranslateVideoResponse,
    examples=examples["/heygen/translate_video"]
)
async def translate_video(
    params: Dict[str, Any] = Body(...),
    service: HeygenService = Depends(get_heygen_service)
):
    validated_params = TranslateVideoParams(**params)
    return service.translate_video(validated_params)

@router.post("/get_translation_status", response_model=ApiResponse)
@schema(
    input_schema_class=TranslationStatusParams,
    output_schema_class=TranslationStatus,
    examples=examples["/heygen/get_translation_status"]
)
async def get_translation_status(
    params: Dict[str, Any] = Body(...),
    service: HeygenService = Depends(get_heygen_service)
):
    validated_params = TranslationStatusParams(**params)
    return service.get_translation_status(validated_params)

@router.post("/get_translation_caption", response_model=ApiResponse)
@schema(
    input_schema_class=TranslateCaptionParams,
    output_schema_class=TranslateCaptionResponse,
    examples=examples["/heygen/get_translation_caption"]
)
async def get_translation_caption(
    params: Dict[str, Any] = Body(...),
    service: HeygenService = Depends(get_heygen_service)
):
    validated_params = TranslateCaptionParams(**params)
    return service.get_translation_caption(validated_params)

@router.post("/generate_photo_avatar", response_model=ApiResponse)
@schema(
    input_schema_class=GeneratePhotoAvatarParams,
    output_schema_class=GeneratePhotoAvatarResponse,
    examples=examples["/heygen/generate_photo_avatar"]
)
async def generate_photo_avatar(
    params: Dict[str, Any] = Body(...),
    service: HeygenService = Depends(get_heygen_service)
):
    validated_params = GeneratePhotoAvatarParams(**params)
    return service.generate_photo_avatar(validated_params)

@router.post("/get_generation_status", response_model=ApiResponse)
@schema(
    input_schema_class=GenerationStatusParams,
    output_schema_class=GenerationStatus,
    examples=examples["/heygen/get_generation_status"]
)
async def get_generation_status(
    params: Dict[str, Any] = Body(...),
    service: HeygenService = Depends(get_heygen_service)
):
    validated_params = GenerationStatusParams(**params)
    return service.get_generation_status(validated_params)

@router.post("/add_motion", response_model=ApiResponse)
@schema(
    input_schema_class=PhotoAvatarActionParams,
    output_schema_class=PhotoAvatarActionResponse,
    examples=examples["/heygen/add_motion"]
)
async def add_motion(
    params: Dict[str, Any] = Body(...),
    service: HeygenService = Depends(get_heygen_service)
):
    validated_params = PhotoAvatarActionParams(**params)
    return service.add_motion(validated_params)

@router.post("/add_sound_effect", response_model=ApiResponse)
@schema(
    input_schema_class=PhotoAvatarActionParams,
    output_schema_class=PhotoAvatarActionResponse,
    examples=examples["/heygen/add_sound_effect"]
)
async def add_sound_effect(
    params: Dict[str, Any] = Body(...),
    service: HeygenService = Depends(get_heygen_service)
):
    validated_params = PhotoAvatarActionParams(**params)
    return service.add_sound_effect(validated_params)

@router.post("/get_photo_avatar_details", response_model=ApiResponse)
@schema(
    input_schema_class=PhotoAvatarDetailsParams,
    output_schema_class=PhotoAvatarDetails,
    examples=examples["/heygen/get_photo_avatar_details"]
)
async def get_photo_avatar_details(
    params: Dict[str, Any] = Body(...),
    service: HeygenService = Depends(get_heygen_service)
):
    validated_params = PhotoAvatarDetailsParams(**params)
    return service.get_photo_avatar_details(validated_params)

@router.post("/upscale_avatar", response_model=ApiResponse)
@schema(
    input_schema_class=PhotoAvatarActionParams,
    output_schema_class=PhotoAvatarActionResponse,
    examples=examples["/heygen/upscale_avatar"]
)
async def upscale_avatar(
    params: Dict[str, Any] = Body(...),
    service: HeygenService = Depends(get_heygen_service)
):
    validated_params = PhotoAvatarActionParams(**params)
    return service.upscale_avatar(validated_params)

@router.post("/get_user_info", response_model=ApiResponse)
@schema(
    output_schema_class=UserInfoResponse,
    examples=examples["/heygen/get_user_info"]
)
async def get_user_info(
    service: HeygenService = Depends(get_heygen_service)
):
    return service.get_user_info()

@router.post("/get_remaining_quota", response_model=ApiResponse)
@schema(
    output_schema_class=RemainingQuotaResponse,
    examples=examples["/heygen/get_remaining_quota"]
)
async def get_remaining_quota(
    service: HeygenService = Depends(get_heygen_service)
):
    return service.get_remaining_quota()

@router.post("/upload_asset", response_model=ApiResponse)
@schema(
    input_schema_class=UploadAssetParams,
    output_schema_class=AssetResponse,
    examples=examples["/heygen/upload_asset"]
)
async def upload_asset(
    params: Dict[str, Any] = Body(...),
    service: HeygenService = Depends(get_heygen_service)
):
    validated_params = UploadAssetParams(**params)
    return service.upload_asset(validated_params)

@router.post("/list_folders", response_model=ApiResponse)
@schema(
    input_schema_class=ListFoldersParams,
    output_schema_class=ListFoldersResponse,
    examples=examples["/heygen/list_folders"]
)
async def list_folders(
    params: Dict[str, Any] = Body(...),
    service: HeygenService = Depends(get_heygen_service)
):
    validated_params = ListFoldersParams(**params)
    return service.list_folders(validated_params)

@router.post("/create_folder", response_model=ApiResponse)
@schema(
    input_schema_class=CreateFolderParams,
    output_schema_class=CreateFolderResponse,
    examples=examples["/heygen/create_folder"]
)
async def create_folder(
    params: Dict[str, Any] = Body(...),
    service: HeygenService = Depends(get_heygen_service)
):
    validated_params = CreateFolderParams(**params)
    return service.create_folder(validated_params)

apply_error_handler_to_router(router)
