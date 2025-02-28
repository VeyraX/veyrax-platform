from fastapi import APIRouter, Depends, HTTPException, Request as FastAPIRequest, Body
from typing import Optional, Dict, Any
from .schema import (
    FileList, FileFilters, FolderCreate, FileMove, DropboxFile, ApiResponse,
    ListFilesParams, GetFileParams, CreateFolderParams, UploadFileParams,
    DownloadFileParams, DeleteFileParams, MoveFileParams, ReadFileParams,
    ListFilesResponse, GetFileResponse, CreateFolderResponse, UploadFileResponse,
    DownloadFileResponse, DeleteFileResponse, MoveFileResponse, ReadFileResponse
)
from .service import DropboxService
from .client import DropboxClient
import os
from pydantic import ValidationError
from ..common.input_schema_decorator import schema, input_schema, output_schema
from ..common.utils import format_validation_error
from ..common.auth import TokenService, DropboxTokenRefresher

router = APIRouter(prefix="/dropbox", tags=["dropbox"])

async def get_dropbox_service(request: FastAPIRequest) -> DropboxService:
    try:
        token_data = await TokenService.get_user_token(request, 'dropbox')
        
        if TokenService.is_token_expired(token_data):
            try:
                token_data = await DropboxTokenRefresher.refresh(request, token_data)
            except Exception as e:
                raise HTTPException(status_code=401, detail=f"Failed to refresh token: {str(e)}")
        
        return DropboxService(token_data['access_token'])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize Dropbox service: {str(e)}")

@router.post("/list_files", response_model=ApiResponse)
@schema(input_schema_class=ListFilesParams, output_schema_class=ListFilesResponse)
async def list_files(
    params: Dict[str, Any] = Body(...),
    service: DropboxService = Depends(get_dropbox_service)
):
    try:
        validated_params = ListFilesParams(**params)
        return service.list_files(validated_params.filters)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'ListFilesParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_file", response_model=ApiResponse)
@schema(input_schema_class=GetFileParams, output_schema_class=GetFileResponse)
async def get_file(
    params: Dict[str, Any] = Body(...),
    service: DropboxService = Depends(get_dropbox_service)
):
    try:
        validated_params = GetFileParams(**params)
        return service.get_file(validated_params.path)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetFileParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/create_folder", response_model=ApiResponse)
@schema(input_schema_class=CreateFolderParams, output_schema_class=CreateFolderResponse)
async def create_folder(
    params: Dict[str, Any] = Body(...),
    service: DropboxService = Depends(get_dropbox_service)
):
    try:
        validated_params = CreateFolderParams(**params)
        return service.create_folder(validated_params.folder.path)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'CreateFolderParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/upload_file", response_model=ApiResponse)
@schema(input_schema_class=UploadFileParams, output_schema_class=UploadFileResponse)
async def upload_file(
    params: Dict[str, Any] = Body(...),
    service: DropboxService = Depends(get_dropbox_service)
):
    try:
        validated_params = UploadFileParams(**params)
        return service.upload_file_b64(
            validated_params.path, 
            validated_params.file_content, 
            validated_params.mode
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'UploadFileParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/download_file")
@schema(input_schema_class=DownloadFileParams, output_schema_class=DownloadFileResponse)
async def download_file(
    params: Dict[str, Any] = Body(...),
    service: DropboxService = Depends(get_dropbox_service)
):
    try:
        validated_params = DownloadFileParams(**params)
        return service.download_file_b64(validated_params.path)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'DownloadFileParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        if hasattr(e, 'response') and e.response.status_code == 400:
            raise HTTPException(status_code=404, detail="File not found")
        raise HTTPException(status_code=500, detail=f"Download error: {str(e)}")

@router.post("/delete_file", response_model=ApiResponse)
@schema(input_schema_class=DeleteFileParams, output_schema_class=DeleteFileResponse)
async def delete_file(
    params: Dict[str, Any] = Body(...),
    service: DropboxService = Depends(get_dropbox_service)
):
    try:
        validated_params = DeleteFileParams(**params)
        return service.delete_file(validated_params.path)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'DeleteFileParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/move_file", response_model=ApiResponse)
@schema(input_schema_class=MoveFileParams, output_schema_class=MoveFileResponse)
async def move_file(
    params: Dict[str, Any] = Body(...),
    service: DropboxService = Depends(get_dropbox_service)
):
    try:
        validated_params = MoveFileParams(**params)
        return service.move_file(validated_params.from_path, validated_params.to_path)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'MoveFileParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/read_file")
@schema(input_schema_class=ReadFileParams, output_schema_class=ReadFileResponse)
async def read_file(
    params: Dict[str, Any] = Body(...),
    service: DropboxService = Depends(get_dropbox_service)
):
    try:
        validated_params = ReadFileParams(**params)
        return service.read_file_content(validated_params.path)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'ReadFileParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }