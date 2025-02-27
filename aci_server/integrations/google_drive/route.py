from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request as FastAPIRequest, Body
from typing import Optional, Dict, Any
from .schema import (
    FileList, DriveFile, FileFilters, FolderCreate, FileMove, ApiResponse,
    ListFilesParams, GetFileParams, CreateFolderParams, UploadFileParams, 
    DownloadFileParams, DeleteFileParams, MoveFileParams, ListFoldersParams, 
    ReadFileParams
)
from .service import DriveService
from .client import DriveClient
import os
from google.oauth2.credentials import Credentials
from ..common.auth import TokenService, GoogleTokenRefresher
from ..common.input_schema_decorator import input_schema
from pydantic import ValidationError

router = APIRouter(prefix="/google-drive", tags=["google-drive"])

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
        return DriveService(client)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize Drive service: {str(e)}")

@router.post("/list_files", response_model=ApiResponse)
@input_schema(schema_class=ListFilesParams)
async def list_files(
    params: Dict[str, Any] = Body(...),
    service: DriveService = Depends(get_drive_service)
):
    try:
        validated_params = ListFilesParams(**params)
        return service.list_files(validated_params.pageToken, validated_params.filters)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_file", response_model=ApiResponse)
@input_schema(schema_class=GetFileParams)
async def get_file(
    params: Dict[str, Any] = Body(...),
    service: DriveService = Depends(get_drive_service)
):
    try:
        validated_params = GetFileParams(**params)
        return service.get_file(validated_params.file_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create_folder", response_model=ApiResponse)
@input_schema(schema_class=CreateFolderParams)
async def create_folder(
    params: Dict[str, Any] = Body(...),
    service: DriveService = Depends(get_drive_service)
):
    try:
        validated_params = CreateFolderParams(**params)
        return service.create_folder(
            validated_params.folder.name, 
            validated_params.folder.parent_id
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload_file", response_model=ApiResponse)
@input_schema(schema_class=UploadFileParams)
async def upload_file(
    params: Dict[str, Any] = Body(...),
    service: DriveService = Depends(get_drive_service)
):
    try:
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
            
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/download_file")
@input_schema(schema_class=DownloadFileParams)
async def download_file(
    params: Dict[str, Any] = Body(...),
    service: DriveService = Depends(get_drive_service)
):
    try:
        validated_params = DownloadFileParams(**params)
        return service.download_file_with_metadata(validated_params.file_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/delete_file")
@input_schema(schema_class=DeleteFileParams)
async def delete_file(
    params: Dict[str, Any] = Body(...),
    service: DriveService = Depends(get_drive_service)
):
    try:
        validated_params = DeleteFileParams(**params)
        service.delete_file(validated_params.file_id)
        return {"status": "success"}
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/move_file", response_model=ApiResponse)
@input_schema(schema_class=MoveFileParams)
async def move_file(
    params: Dict[str, Any] = Body(...),
    service: DriveService = Depends(get_drive_service)
):
    try:
        validated_params = MoveFileParams(**params)
        return service.move_file(
            validated_params.file_id, 
            validated_params.new_parent_id
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/list_folders", response_model=ApiResponse)
@input_schema(schema_class=ListFoldersParams)
async def list_folders(
    params: Dict[str, Any] = Body(...),
    service: DriveService = Depends(get_drive_service)
):
    try:
        validated_params = ListFoldersParams(**params)
        filters = validated_params.filters or FileFilters()
        filters_dict = filters.dict()
        filters_dict['folders_only'] = True
        
        modified_filters = FileFilters(**filters_dict)
        return service.list_files(validated_params.pageToken, modified_filters)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/read_file")
@input_schema(schema_class=ReadFileParams)
async def read_file(
    params: Dict[str, Any] = Body(...),
    service: DriveService = Depends(get_drive_service)
):
    try:
        validated_params = ReadFileParams(**params)
        return service.read_file_content(validated_params.file_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }