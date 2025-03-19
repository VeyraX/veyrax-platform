from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request as FastAPIRequest, Body
from typing import Optional, Dict, Any
from .schema import (
    FileList, DriveFile, FileFilters, FolderCreate, FileMove, ApiResponse,
    ListFilesParams, GetFileParams, CreateFolderParams, UploadFileParams, 
    DownloadFileParams, DeleteFileParams, MoveFileParams, ListFoldersParams, 
    ReadFileParams, SetPermissionParams, ListPermissionsParams, DeletePermissionParams,
    CopyFileParams, ListFilesResponse, GetFileResponse, CreateFolderResponse,
    UploadFileResponse, DownloadFileResponse, DeleteFileResponse, MoveFileResponse,
    ListFoldersResponse, ReadFileResponse
)

from .service import DriveService
from .client import DriveClient
import os
from google.oauth2.credentials import Credentials
from ..common.auth import TokenService, GoogleTokenRefresher
from ..common.input_schema_decorator import schema, output_schema
from ..common.utils import format_validation_error, apply_error_handler_to_service, apply_error_handler_to_router, apply_error_handler_to_client
from ..common.examples_handler import ExamplesLoader


router = APIRouter(prefix="/google-drive", tags=["google-drive"])

examples = ExamplesLoader()  # Will automatically use /integrations/google_drive directory

async def get_drive_service(request: FastAPIRequest):
    try:
        token_data = await TokenService.get_user_token(request, 'google-drive')
        
        if TokenService.is_token_expired(token_data):
            try:
                token_data = await GoogleTokenRefresher.refresh(request, token_data)
            except Exception as e:
                raise HTTPException(status_code=401, detail="Failed to refresh token")
            
        creds = Credentials(
            token=token_data['access_token'],
            refresh_token=token_data['refresh_token'],
            token_uri="https://oauth2.googleapis.com/token",
            client_id=os.getenv('GOOGLE_CLIENT_ID'),
            client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
            scopes=token_data['scopes'].split(',')
        )
        
        client = DriveClient(creds)
        apply_error_handler_to_client(client)
        service = DriveService(client)
        apply_error_handler_to_service(service)
        return service
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize Drive service: {str(e)}")

@router.post("/list_files", response_model=ApiResponse)
@schema(input_schema_class=ListFilesParams, output_schema_class=ListFilesResponse, examples=examples["/google-drive/list_files"])
async def list_files(
    params: Dict[str, Any] = Body(...),
    service: DriveService = Depends(get_drive_service)
):
    validated_params = ListFilesParams(**params)
    return service.list_files(validated_params.pageToken, validated_params.filters)

@router.post("/get_file", response_model=ApiResponse)
@schema(input_schema_class=GetFileParams, output_schema_class=GetFileResponse, examples=examples["/google-drive/get_file"])
async def get_file(
    params: Dict[str, Any] = Body(...),
    service: DriveService = Depends(get_drive_service)
):
    validated_params = GetFileParams(**params)
    return service.get_file(validated_params.file_id)

@router.post("/create_folder", response_model=ApiResponse)
@schema(input_schema_class=CreateFolderParams, output_schema_class=CreateFolderResponse, examples=examples["/google-drive/create_folder"])
async def create_folder(
    params: Dict[str, Any] = Body(...),
    service: DriveService = Depends(get_drive_service)
):
    validated_params = CreateFolderParams(**params)
    return service.create_folder(
        validated_params.folder.name,
        validated_params.folder.parent_id  # Will be None if not provided
    )

@router.post("/upload_file", response_model=ApiResponse)
@schema(input_schema_class=UploadFileParams, output_schema_class=UploadFileResponse, examples=examples["/google-drive/upload_file"])
async def upload_file(
    params: Dict[str, Any] = Body(...),
    service: DriveService = Depends(get_drive_service)
):
    validated_params = UploadFileParams(**params)
    
    # Extract file reference and parent_id from validated params
    file_ref = validated_params.file
    parent_id = validated_params.parent_id
    
    # Handle file upload based on what's provided in the FileReference
    if file_ref.file_content.file_url:
        # Download from URL and upload to Drive
        return await service.upload_file_from_url(
            file_url=file_ref.file_content.file_url,
            filename=file_ref.file_name,
            parent_id=parent_id
        )
    elif file_ref.file_content.file_base64:
        # Decode base64 and upload to Drive
        return await service.upload_file_from_base64(
            filename=file_ref.file_name,
            file_base64=file_ref.file_content.file_base64,
            content_type=file_ref.content_type,
            parent_id=parent_id
        )
    else:
        raise HTTPException(status_code=400, detail="Either file_url or file_base64 must be provided")

@router.post("/download_file")
@schema(input_schema_class=DownloadFileParams, output_schema_class=DownloadFileResponse, examples=examples["/google-drive/download_file"])
async def download_file(
    params: Dict[str, Any] = Body(...),
    service: DriveService = Depends(get_drive_service)
):
    validated_params = DownloadFileParams(**params)
    return service.download_file_with_metadata(validated_params.file_id)

@router.post("/delete_file")
@schema(input_schema_class=DeleteFileParams, output_schema_class=DeleteFileResponse, examples=examples["/google-drive/delete_file"])
async def delete_file(
    params: Dict[str, Any] = Body(...),
    service: DriveService = Depends(get_drive_service)
):
    validated_params = DeleteFileParams(**params)
    service.delete_file(validated_params.file_id)
    return {"status": "success"}

@router.post("/move_file", response_model=ApiResponse)
@schema(input_schema_class=MoveFileParams, output_schema_class=MoveFileResponse, examples=examples["/google-drive/move_file"])
async def move_file(
    params: Dict[str, Any] = Body(...),
    service: DriveService = Depends(get_drive_service)
):
    validated_params = MoveFileParams(**params)
    return service.move_file(
        validated_params.file_id, 
        validated_params.new_parent_id
    )

@router.post("/list_folders", response_model=ApiResponse)
@schema(input_schema_class=ListFoldersParams, output_schema_class=ListFoldersResponse, examples=examples["/google-drive/list_folders"])
async def list_folders(
    params: Dict[str, Any] = Body(...),
    service: DriveService = Depends(get_drive_service)
):
    validated_params = ListFoldersParams(**params)
    filters = validated_params.filters or FileFilters()
    filters_dict = filters.dict()
    filters_dict['folders_only'] = True
    
    modified_filters = FileFilters(**filters_dict)
    return service.list_files(validated_params.pageToken, modified_filters)

@router.post("/read_file")
@schema(input_schema_class=ReadFileParams, output_schema_class=ReadFileResponse, examples=examples["/google-drive/read_file"])
async def read_file(
    params: Dict[str, Any] = Body(...),
    service: DriveService = Depends(get_drive_service)
):
    validated_params = ReadFileParams(**params)
    return service.read_file_content(validated_params.file_id)

@router.post("/set_permission", response_model=ApiResponse)
@schema(input_schema_class=SetPermissionParams, examples=examples["/google-drive/set_permission"])
async def set_permission(
    params: Dict[str, Any] = Body(...),
    service: DriveService = Depends(get_drive_service)
):
    validated_params = SetPermissionParams(**params)
    return service.set_permission(
        validated_params.file_id,
        validated_params.permission.dict()
    )

@router.post("/list_permissions", response_model=ApiResponse)
@schema(input_schema_class=ListPermissionsParams, examples=examples["/google-drive/list_permissions"])
async def list_permissions(
    params: Dict[str, Any] = Body(...),
    service: DriveService = Depends(get_drive_service)
):
    validated_params = ListPermissionsParams(**params)
    return service.list_permissions(validated_params.file_id)

@router.post("/delete_permission")
@schema(input_schema_class=DeletePermissionParams, examples=examples["/google-drive/delete_permission"])
async def delete_permission(
    params: Dict[str, Any] = Body(...),
    service: DriveService = Depends(get_drive_service)
):
    validated_params = DeletePermissionParams(**params)
    service.delete_permission(
        validated_params.file_id,
        validated_params.permission_id
    )
    return {"status": "success"}

@router.post("/copy_file", response_model=ApiResponse)
@schema(input_schema_class=CopyFileParams, examples=examples["/google-drive/copy_file"])
async def copy_file(
    params: Dict[str, Any] = Body(...),
    service: DriveService = Depends(get_drive_service)
):
    validated_params = CopyFileParams(**params)
    return service.copy_file(
        validated_params.file_id,
        validated_params.name,
        validated_params.parent_id
    )

apply_error_handler_to_router(router)