from fastapi import APIRouter, Depends, HTTPException, Request, Body
from typing import Dict, Any
from vector_tools.utils import validate_user_index
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


router = APIRouter(prefix="/vector-tools", tags=["vector-tools"])

@router.post("/index-data")
async def process_documents(
    request: Request,
) -> Dict[str, Any]:
    try:
        body = await request.json()
        collection_name = body['collection_name']
        user_id = await get_user_from_request(request)
        
        if not validate_user_index(user_id, collection_name):
            raise HTTPException(
                status_code=400,
                detail=f"User {user_id} does not have an index for {collection_name}"
            )   
        
        if collection_name == 'google-drive':
            token_data = await TokenService.get_user_token(request, 'google-drive')
            
            if TokenService.is_token_expired(token_data):
                token_data = await GoogleTokenRefresher.refresh(request, token_data)
            
            service_credentials = {
                'access_token': token_data['access_token'],
                'refresh_token': token_data['refresh_token'],
                'scopes': token_data['scopes']
            }
            
            task = process_google_drive_documents_task.delay(service_credentials, user_id)
            
        elif collection_name == 'notion':
            auth_token = await TokenService.get_user_token(request, 'notion')
            task = process_notion_documents_task.delay(auth_token, user_id)
            
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported provider: {collection_name}"
            )
        
        return {
            "status": "accepted",
            "message": f"Processing started for {collection_name}",
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

@router.post("/search")
async def search_documents(
    request: Request,
    search_request: SearchRequest,
) -> Dict[str, Any]:
    try:
        user_id = await get_user_from_request(request)
        
        search_service = VectorSearchService(user_id)
        
        results = search_service.search_documents(
            search_params=search_request.search_params,
            query_text=search_request.query_text,
        )
        
        return {
            "status": "success",
            "results": results
        }
        
    except ValueError as e:
        error_msg = f"Validation error: {str(e)}"
        print(error_msg) 
        raise HTTPException(
            status_code=400,
            detail=error_msg
        )
    except Exception as e:
        error_msg = f"Error searching documents: {str(e)}"
        print(error_msg)
        raise HTTPException(
            status_code=500,
            detail=error_msg
        )

@router.delete("/delete-index-data")
async def delete_index_data(
    request: Request,
) -> Dict[str, Any]:
    try:
        body = await request.json()
        collection_name = body.get('collection_name')
        
        if not collection_name:
            raise HTTPException(
                status_code=400,
                detail="collection_name is required"
            )
            
        user_id = await get_user_from_request(request)
        
        if not validate_user_index(user_id, collection_name):
            raise HTTPException(
                status_code=404,
                detail=f"No index found for user {user_id} and collection {collection_name}"
            )
        
        vector_store = VectorStoreActions(collection_name)
        deleted_count = vector_store.delete_user_vectors(user_id)
        
        return {
            "status": "success",
            "message": f"Successfully deleted {deleted_count} vectors for user {user_id} from collection {collection_name}"
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error in delete_index_data: {str(e)}")  # Add logging
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting vectors: {str(e)}"
        )

