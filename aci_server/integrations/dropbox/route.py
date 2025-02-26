from fastapi import APIRouter, Depends, UploadFile, HTTPException, Body, Request as FastAPIRequest
from typing import Optional, Dict, Any
from .service import DropboxService
from .schema import (
    FileList, FileFilters, FolderCreate, FileMove, DropboxFile, ApiResponse,
    ListFilesParams, GetFileParams, CreateFolderParams, UploadFileParams,
    DownloadFileParams, DeleteFileParams, MoveFileParams, ReadFileParams
)
from ..common.input_schema_decorator import input_schema
import os
import pickle
import requests
from fastapi.responses import Response
from pydantic import BaseModel
import base64

router = APIRouter(prefix="/dropbox", tags=["dropbox"])

async def get_service(request: FastAPIRequest) -> DropboxService:
    if os.path.exists('credentials/dropbox_token.pickle'):
        with open('credentials/dropbox_token.pickle', 'rb') as token_file:
            creds = pickle.load(token_file)
            token_str = creds.get('access_token')
            if not token_str:
                raise HTTPException(status_code=401, detail="Access token not found in credentials")
    else:
        raise HTTPException(status_code=404, detail="Credentials file not found")
    
    return DropboxService(token_str)

@router.post("/list_files", response_model=ApiResponse)
@input_schema(schema_class=ListFilesParams)
async def list_files(
    params: Dict[str, Any] = Body(...),
    service: DropboxService = Depends(get_service)
) -> ApiResponse:
    try:
        filters_data = params.get('filters', {})
        filters = FileFilters(**filters_data)
        return service.list_files(filters)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_file", response_model=ApiResponse)
@input_schema(schema_class=GetFileParams)
async def get_file(
    params: Dict[str, Any] = Body(...),
    service: DropboxService = Depends(get_service)
) -> ApiResponse:
    try:
        path = params.get('path')
        if not path:
            raise HTTPException(status_code=400, detail="path is required")
            
        return service.get_file(path)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/create_folder", response_model=ApiResponse)
@input_schema(schema_class=CreateFolderParams)
async def create_folder(
    params: Dict[str, Any] = Body(...),
    service: DropboxService = Depends(get_service)
) -> ApiResponse:
    try:
        folder_data = params.get('folder', params)
        folder = FolderCreate(**folder_data)
        return service.create_folder(folder.path)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/upload_file", response_model=ApiResponse)
@input_schema(schema_class=UploadFileParams)
async def upload_file(
    params: Dict[str, Any] = Body(...),
    service: DropboxService = Depends(get_service)
) -> ApiResponse:
    try:
        path = params.get('path')
        file_content_b64 = params.get('file_content')
        mode = params.get('mode', 'add')
        
        if not path or not file_content_b64:
            raise HTTPException(status_code=400, detail="path and file_content are required")
        
        file_content = base64.b64decode(file_content_b64)
        return service.upload_file(path, file_content, mode)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/download_file")
@input_schema(schema_class=DownloadFileParams)
async def download_file(
    params: Dict[str, Any] = Body(...),
    service: DropboxService = Depends(get_service)
):
    try:
        path = params.get('path')
        if not path:
            raise HTTPException(status_code=400, detail="path is required")
            
        clean_path = '/' + '/'.join(filter(None, path.split('/')))
        content, metadata = service.download_file(clean_path)
        
        filename = metadata.name if hasattr(metadata, 'name') else "download"
        mime_type = metadata.mime_type if hasattr(metadata, 'mime_type') else "application/octet-stream"
        
        content_b64 = base64.b64encode(content).decode('utf-8')
        
        return {
            "status": "success",
            "data": {
                "file_content": content_b64,
                "mime_type": mime_type,
                "filename": filename,
                "file_info": metadata.dict()
            }
        }
    except Exception as e:
        if isinstance(e, requests.exceptions.HTTPError) and hasattr(e, 'response') and e.response.status_code == 400:
            raise HTTPException(status_code=404, detail="File not found")
        raise HTTPException(status_code=500, detail=f"Download error: {str(e)}")

@router.post("/delete_file", response_model=ApiResponse)
@input_schema(schema_class=DeleteFileParams)
async def delete_file(
    params: Dict[str, Any] = Body(...),
    service: DropboxService = Depends(get_service)
) -> ApiResponse:
    try:
        path = params.get('path')
        if not path:
            raise HTTPException(status_code=400, detail="path is required")
            
        return service.delete_file(path)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/move_file", response_model=ApiResponse)
@input_schema(schema_class=MoveFileParams)
async def move_file(
    params: Dict[str, Any] = Body(...),
    service: DropboxService = Depends(get_service)
) -> ApiResponse:
    try:
        from_path = params.get('from_path')
        to_path = params.get('to_path')
        
        if not from_path or not to_path:
            raise HTTPException(status_code=400, detail="from_path and to_path are required")
            
        from_path = from_path if from_path.startswith('/') else f"/{from_path}"
        to_path = to_path if to_path.startswith('/') else f"/{to_path}"
        
        return service.move_file(from_path, to_path)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/read_file")
@input_schema(schema_class=ReadFileParams)
async def read_file(
    params: Dict[str, Any] = Body(...),
    service: DropboxService = Depends(get_service)
):
    try:
        path = params.get('path')
        if not path:
            raise HTTPException(status_code=400, detail="path is required")
            
        content, file_info = service.download_file(path)
        mime_type = file_info.mime_type
        
        if any(x in (mime_type or "") for x in ['spreadsheet', 'excel', 'csv']):
            return {
                "success": False,
                "error": "Spreadsheet files are not supported for text reading",
                "data": {
                    "file": file_info.dict()
                }
            }
            
        from ..common.file_reader import read_file_content
        text_content, success = read_file_content(content, mime_type)
        
        return {
            "success": success,
            "data": {
                "content": text_content,
                "file": file_info.dict(),
                "mime_type": mime_type
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }