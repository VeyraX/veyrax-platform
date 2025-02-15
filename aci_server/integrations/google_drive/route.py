from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import Optional
from .schema import FileList, DriveFile, FileFilters, FolderCreate, FileMove
from .service import DriveService
from .client import DriveClient
import pickle
import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from fastapi.responses import StreamingResponse


router = APIRouter(prefix="/drive", tags=["drive"])

async def get_drive_service():
    if os.path.exists('credentials/google_token.pickle'):
        with open('credentials/google_token.pickle', 'rb') as token:
            creds_dict = pickle.load(token)
            creds = Credentials(
                token=creds_dict['access_token'],
                refresh_token=creds_dict['refresh_token'],
                token_uri="https://oauth2.googleapis.com/token",
                client_id=os.getenv('GOOGLE_CLIENT_ID'),
                client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
                scopes=creds_dict['scope'].split()
            )
        
            if creds.expired:
                creds.refresh(Request())
                updated_creds_dict = {
                    'access_token': creds.token,
                    'refresh_token': creds.refresh_token,
                    'scope': ' '.join(creds.scopes),
                }
                with open('credentials/google_token.pickle', 'wb') as token:
                    pickle.dump(updated_creds_dict, token)
    else:
        raise HTTPException(status_code=404, detail="Credentials file not found")
    
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
    file_content = service.download_file(file_id)
    file_info = service.get_file(file_id)
    return StreamingResponse(
        file_content,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={file_info.name}"}
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