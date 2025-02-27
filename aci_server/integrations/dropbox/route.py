from fastapi import APIRouter, Depends, HTTPException, Request as FastAPIRequest, Body
from typing import Optional, Dict, Any
from .schema import (
    FileList, FileFilters, FolderCreate, FileMove, DropboxFile, ApiResponse,
    ListFilesParams, GetFileParams, CreateFolderParams, UploadFileParams,
    DownloadFileParams, DeleteFileParams, MoveFileParams, ReadFileParams
)
from .service import DropboxService
import os
import pickle
from pydantic import ValidationError
from ..common.input_schema_decorator import input_schema

router = APIRouter(prefix="/dropbox", tags=["dropbox"])

async def get_dropbox_service(request: FastAPIRequest) -> DropboxService:
    try:
        if os.path.exists('credentials/dropbox_token.pickle'):
            with open('credentials/dropbox_token.pickle', 'rb') as token_file:
                creds = pickle.load(token_file)
                token_str = creds.get('access_token')
                if not token_str:
                    raise HTTPException(status_code=401, detail="Access token not found in credentials")
        else:
            raise HTTPException(status_code=404, detail="Credentials file not found")
        
        return DropboxService(token_str)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize Dropbox service: {str(e)}")

@router.post("/list_files", response_model=ApiResponse)
@input_schema(schema_class=ListFilesParams)
async def list_files(
    params: Dict[str, Any] = Body(...),
    service: DropboxService = Depends(get_dropbox_service)
):
    try:
        validated_params = ListFilesParams(**params)
        return service.list_files(validated_params.filters)
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
    service: DropboxService = Depends(get_dropbox_service)
):
    try:
        validated_params = GetFileParams(**params)
        return service.get_file(validated_params.path)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/create_folder", response_model=ApiResponse)
@input_schema(schema_class=CreateFolderParams)
async def create_folder(
    params: Dict[str, Any] = Body(...),
    service: DropboxService = Depends(get_dropbox_service)
):
    try:
        validated_params = CreateFolderParams(**params)
        return service.create_folder(validated_params.folder.path)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/upload_file", response_model=ApiResponse)
@input_schema(schema_class=UploadFileParams)
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
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/download_file")
@input_schema(schema_class=DownloadFileParams)
async def download_file(
    params: Dict[str, Any] = Body(...),
    service: DropboxService = Depends(get_dropbox_service)
):
    try:
        validated_params = DownloadFileParams(**params)
        return service.download_file_b64(validated_params.path)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        if hasattr(e, 'response') and e.response.status_code == 400:
            raise HTTPException(status_code=404, detail="File not found")
        raise HTTPException(status_code=500, detail=f"Download error: {str(e)}")

@router.post("/delete_file", response_model=ApiResponse)
@input_schema(schema_class=DeleteFileParams)
async def delete_file(
    params: Dict[str, Any] = Body(...),
    service: DropboxService = Depends(get_dropbox_service)
):
    try:
        validated_params = DeleteFileParams(**params)
        return service.delete_file(validated_params.path)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/move_file", response_model=ApiResponse)
@input_schema(schema_class=MoveFileParams)
async def move_file(
    params: Dict[str, Any] = Body(...),
    service: DropboxService = Depends(get_dropbox_service)
):
    try:
        validated_params = MoveFileParams(**params)
        return service.move_file(validated_params.from_path, validated_params.to_path)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/read_file")
@input_schema(schema_class=ReadFileParams)
async def read_file(
    params: Dict[str, Any] = Body(...),
    service: DropboxService = Depends(get_dropbox_service)
):
    try:
        validated_params = ReadFileParams(**params)
        return service.read_file_content(validated_params.path)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }