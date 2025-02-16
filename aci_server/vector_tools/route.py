from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Dict, Any
from integrations.google_drive.service import DriveService
from integrations.google_drive.route import get_drive_service
from vector_tools.vector_tools import VectorStoreActions
from vector_tools.data_sources.google_drive import GoogleDriveSource
from vector_tools.tasks import process_google_drive_documents_task, process_notion_documents_task
from integrations.notion.service import NotionService
from integrations.notion.route import get_notion_service
from integrations.common.auth import TokenService

router = APIRouter(prefix="/vector", tags=["vector"])

@router.post("/process-google-drive")
async def process_google_drive_documents(
    drive_service: DriveService = Depends(get_drive_service)
) -> Dict[str, Any]:
    try:
        creds = drive_service.client.credentials
        service_credentials = {
            'access_token': creds.token,
            'refresh_token': creds.refresh_token,
            'scopes': ' '.join(creds.scopes)
        }
        
        task = process_google_drive_documents_task.delay(service_credentials)
        
        return {
            "status": "accepted",
            "message": "Processing started",
            "task_id": task.id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error starting document processing: {str(e)}"
        )

@router.get("/task/{task_id}")
async def get_task_status(task_id: str) -> Dict[str, Any]:
    task = process_google_drive_documents_task.AsyncResult(task_id)
    
    response = {
        "task_id": task_id,
        "status": task.status,
    }
    
    if task.ready():
        response["result"] = task.get()
    
    return response

@router.post("/process-notion")
async def process_notion_documents(request: Request) -> Dict[str, Any]:
    try:
        token_path = "credentials/token.notion"
        with open(token_path, "r") as f:
            auth_token = f.read().strip()
            
        if auth_token.startswith("NOTION_API_KEY="):
            auth_token = auth_token.replace("NOTION_API_KEY=", "")
            
        if not auth_token:
            raise HTTPException(
                status_code=500,
                detail="Notion token not found in credentials file"
            )
            
        task = process_notion_documents_task.delay(auth_token)
        
        return {
            "status": "accepted",
            "message": "Processing started",
            "task_id": task.id
        }
        
    except FileNotFoundError:
        raise HTTPException(
            status_code=500,
            detail="Notion credentials file not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error starting document processing: {str(e)}"
        )
