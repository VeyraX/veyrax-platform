from fastapi import APIRouter, Depends, UploadFile, HTTPException
from typing import Optional
from .service import DropboxService
from .schema import FileList, FileFilters, FolderCreate, FileMove, DropboxFile
import os
import pickle
import requests
from fastapi.responses import Response
from pydantic import BaseModel

router = APIRouter(prefix="/dropbox", tags=["dropbox"])

async def get_service() -> DropboxService:
    if os.path.exists('credentials/dropbox_token.pickle'):
        with open('credentials/dropbox_token.pickle', 'rb') as token_file:
            creds = pickle.load(token_file)
            token_str = creds.get('access_token')
            if not token_str:
                raise HTTPException(status_code=401, detail="Access token not found in credentials")
    else:
        raise HTTPException(status_code=404, detail="Credentials file not found")
    
    return DropboxService(token_str)

@router.get("/files", response_model=FileList)
async def list_files(
    filters: FileFilters = Depends(),
    service: DropboxService = Depends(get_service)
) -> FileList:
    return service.list_files(filters)

@router.get("/files/{path:path}", response_model=DropboxFile)
async def get_file(
    path: str,
    service: DropboxService = Depends(get_service)
) -> DropboxFile:
    try:
        return service.get_file(path)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/folders", response_model=DropboxFile)
async def create_folder(
    folder: FolderCreate,
    service: DropboxService = Depends(get_service)
) -> DropboxFile:
    try:
        return service.create_folder(folder.path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/files/{path:path}", response_model=DropboxFile)
async def upload_file(
    path: str,
    file: UploadFile,
    mode: Optional[str] = "add",
    service: DropboxService = Depends(get_service)
) -> DropboxFile:
    try:
        content = await file.read()
        return service.upload_file(path, content, mode)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

class DownloadRequest(BaseModel):
    path: str

@router.post("/files/download")
async def download_file(
    download_req: DownloadRequest,
    service: DropboxService = Depends(get_service)
):
    try:
        clean_path = '/' + '/'.join(filter(None, download_req.path.split('/')))
        content, metadata = service.download_file(clean_path)
        return Response(
            content=content,
            media_type=metadata.mime_type or "application/octet-stream",
            headers={"Content-Disposition": f'attachment; filename="{metadata.name}"'}
        )
    except Exception as e:
        if isinstance(e, requests.exceptions.HTTPError) and e.response.status_code == 400:
            raise HTTPException(status_code=404, detail="File not found")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/files/{path:path}", response_model=DropboxFile)
async def delete_file(
    path: str,
    service: DropboxService = Depends(get_service)
) -> DropboxFile:
    try:
        return service.delete_file(path)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/move", response_model=DropboxFile)
async def move_file(
    move_request: FileMove,
    service: DropboxService = Depends(get_service)
) -> DropboxFile:
    try:
        from_path = move_request.from_path if move_request.from_path.startswith('/') else f"/{move_request.from_path}"
        to_path = move_request.to_path if move_request.to_path.startswith('/') else f"/{move_request.to_path}"
        
        return service.move_file(from_path, to_path)
    except Exception as e:
        print(f"Move endpoint error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))