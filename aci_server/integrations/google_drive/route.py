from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request as FastAPIRequest
from typing import Optional
from .schema import FileList, DriveFile, FileFilters, FolderCreate, FileMove
from .service import DriveService
from .client import DriveClient
import pickle
import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from fastapi.responses import StreamingResponse
from ..common.auth import TokenService, GoogleTokenRefresher
from ..common.file_reader import read_file_content


router = APIRouter(prefix="/google_drive", tags=["google_drive"])

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
        scopes=token_data['scopes'].split()
    )
    
    client = DriveClient(creds)
    return DriveService(client)

@router.get("/files", response_model=FileList)
async def list_files(
    page_token: Optional[str] = None,
    filters: FileFilters = Depends(),
    service: DriveService = Depends(get_drive_service)
):
    return service.list_files(page_token, filters)

@router.get("/files/{file_id}", response_model=DriveFile)
async def get_file(
    file_id: str,
    service: DriveService = Depends(get_drive_service)
):
    return service.get_file(file_id)

@router.post("/files", response_model=DriveFile)
async def upload_file(
    file: UploadFile = File(...),
    parent_id: Optional[str] = None,
    service: DriveService = Depends(get_drive_service)
):
    return service.upload_file(file.filename, file.file, file.content_type, parent_id)

@router.get("/files/{file_id}/download")
async def download_file(
    file_id: str,
    service: DriveService = Depends(get_drive_service)
):
    file_content, mime_type = service.download_file(file_id)
    file_info = service.get_file(file_id)
    
    file_content.seek(0)
    
    extension = {
        'application/pdf': '.pdf',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
    }.get(mime_type, '')
    
    filename = f"{file_info.name}{extension}"
    
    return StreamingResponse(
        iter([file_content.read()]),
        media_type=mime_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.delete("/files/{file_id}")
async def delete_file(
    file_id: str,
    service: DriveService = Depends(get_drive_service)
):
    service.delete_file(file_id)
    return {"status": "success"}

@router.post("/folders", response_model=DriveFile)
async def create_folder(
    folder: FolderCreate,
    service: DriveService = Depends(get_drive_service)
):
    return service.create_folder(folder.name, folder.parent_id)

@router.patch("/files/{file_id}/move", response_model=DriveFile)
async def move_file(
    file_id: str,
    move: FileMove,
    service: DriveService = Depends(get_drive_service)
):
    return service.move_file(file_id, move.new_parent_id)

@router.get("/folders", response_model=FileList)
async def list_folders(
    page_token: Optional[str] = None,
    name_contains: Optional[str] = None,
    parent_id: Optional[str] = None,
    service: DriveService = Depends(get_drive_service)
):
    filters = FileFilters(
        name_contains=name_contains,
        parent_id=parent_id,
        folders_only=True
    )
    return service.list_files(page_token, filters)

@router.get("/files/{file_id}/read")
async def read_file(
    file_id: str,
    service: DriveService = Depends(get_drive_service)
):
    try:
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