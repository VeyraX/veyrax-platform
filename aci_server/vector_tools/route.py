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
from integrations.common.auth import GoogleTokenRefresher

from integrations.common.auth import get_user_from_request
from vector_tools.schema import SearchParams, SearchRequest
from .service import VectorSearchService
from google.oauth2.credentials import Credentials
import os
from integrations.google_drive.client import DriveClient
from fastapi import Request

router = APIRouter(prefix="/vector", tags=["vector"])

@router.post("/process-google-drive")
async def process_google_drive_documents(
    request: Request,
    drive_service: DriveService = Depends(get_drive_service)
) -> Dict[str, Any]:
    try:
        token_data = await TokenService.get_user_token(request, 'google-drive')
        
        if TokenService.is_token_expired(token_data):
            token_data = await GoogleTokenRefresher.refresh(request, token_data)
        
        service_credentials = {
            'access_token': token_data['access_token'],
            'refresh_token': token_data['refresh_token'],
            'scopes': token_data['scopes']
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
        auth_token = await TokenService.get_user_token(request, 'notion')
            
        task = process_notion_documents_task.delay(auth_token)
        
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

@router.post("/search")
async def search_documents(
    request: Request,
    search_request: SearchRequest,
) -> Dict[str, Any]:
    try:
        user_id = await get_user_from_request(request)
        
        search_request.search_params.query.user_id = user_id
        
        search_service = VectorSearchService()
        
        results = search_service.search_documents(
            search_params=search_request.search_params,
            query_text=search_request.query_text
        )
        
        return {
            "status": "success",
            "results": results
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error searching documents: {str(e)}"
        )
