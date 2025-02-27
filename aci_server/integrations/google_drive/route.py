from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request as FastAPIRequest, Body
from typing import Optional, Dict, Any
from .schema import FileList, DriveFile, FileFilters, FolderCreate, FileMove, ApiResponse, ListFilesParams, GetFileParams, CreateFolderParams, UploadFileParams, DownloadFileParams, DeleteFileParams, MoveFileParams, ListFoldersParams, ReadFileParams
from .service import DriveService
from .client import DriveClient
import pickle
import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from fastapi.responses import StreamingResponse
from ..common.auth import TokenService, GoogleTokenRefresher
from ..common.file_reader import read_file_content
from ..common.input_schema_decorator import input_schema


router = APIRouter(prefix="/google-drive", tags=["google-drive"])

async def get_drive_service(request: FastAPIRequest):
    token_data = await TokenService.get_user_token(request, 'google-drive')
    if TokenService.is_token_expired(token_data):
        token_data = await GoogleTokenRefresher.refresh(request, token_data)
        
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

@router.post("/list_files", response_model=ApiResponse)
@input_schema(schema_class=ListFilesParams)
async def list_files(
    params: Dict[str, Any] = Body(...),
    service: DriveService = Depends(get_drive_service)
):
    try:
        filters_data = params.get('filters', {})
        page_token = params.get('pageToken')
        
        filters = FileFilters(**filters_data)
        return service.list_files(page_token, filters)
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
        file_id = params.get('file_id')
        if not file_id:
            raise HTTPException(status_code=400, detail="file_id is required")
            
        return service.get_file(file_id)
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
        folder_data = params.get('folder', params)
        folder = FolderCreate(**folder_data)
        return service.create_folder(folder.name, folder.parent_id)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload_file", response_model=ApiResponse)
@input_schema(schema_class=UploadFileParams)
async def upload_file(
    file: UploadFile = File(...),
    parent_id: Optional[str] = None,
    service: DriveService = Depends(get_drive_service)
):
    try:
        return service.upload_file(file.filename, file.file, file.content_type, parent_id)
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
        file_id = params.get('file_id')
        if not file_id:
            raise HTTPException(status_code=400, detail="file_id is required")
            
        file_content, mime_type = service.download_file(file_id)
        file_info = service.get_file(file_id)
        
        file_content.seek(0)
        
        extension = {
            'application/pdf': '.pdf',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
        }.get(mime_type, '')
        
        filename = f"{file_info.name}{extension}"
        
        return {
            "status": "success",
            "file_content": file_content.read(),
            "mime_type": mime_type,
            "filename": filename
        }
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
        file_id = params.get('file_id')
        if not file_id:
            raise HTTPException(status_code=400, detail="file_id is required")
            
        service.delete_file(file_id)
        return {"status": "success"}
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
        file_id = params.get('file_id')
        new_parent_id = params.get('new_parent_id')
        
        if not file_id or not new_parent_id:
            raise HTTPException(status_code=400, detail="file_id and new_parent_id are required")
            
        return service.move_file(file_id, new_parent_id)
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
        filters_data = params.get('filters', {})
        page_token = params.get('pageToken')
        
        filters_data['folders_only'] = True
        filters = FileFilters(**filters_data)
        return service.list_files(page_token, filters)
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
        file_id = params.get('file_id')
        if not file_id:
            raise HTTPException(status_code=400, detail="file_id is required")
            
        file_content, mime_type = service.download_file(file_id)
        file_info = service.get_file(file_id)
        
        if any(x in mime_type for x in ['spreadsheet', 'excel', 'csv']):
            return {
                "success": False,
                "error": "Spreadsheet files are not supported for text reading",
                "file": file_info.dict()
            }
            
        text_content, success = read_file_content(file_content, mime_type)
        
        return {
            "success": success,
            "content": text_content,
            "file": file_info.dict(),
            "mime_type": mime_type
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }