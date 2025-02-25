from fastapi import APIRouter, Depends, HTTPException, Request as FastAPIRequest, Body
from typing import Optional, Dict, Any
from .schema import MessageList, Message, DraftMessage, DraftResponse, DraftList, MessageFilters, ApiResponse
from .service import GmailService
from .client import GmailClient
import pickle
import os
from ..common.utils import get_router_tools
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GoogleRequest
from ..common.auth import TokenService, GoogleTokenRefresher


router = APIRouter(prefix="/gmail", tags=["gmail"])

async def get_gmail_service(request: FastAPIRequest):
    token_data = await TokenService.get_user_token(request, 'gmail')
    
    if TokenService.is_token_expired(token_data):
        try:
            token_data = await GoogleTokenRefresher.refresh(request, token_data)
        except Exception as e:
            raise HTTPException(status_code=401, detail="Failed to refresh token")
        
    creds = Credentials(
        token=token_data['access_token'],
        refresh_token=token_data['refresh_token'],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv('GOOGLE_CLIENT_ID'),
        client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
        scopes=token_data['scopes'].split(',')
    )
    
    client = GmailClient(creds)
    return GmailService(client)

@router.post("/get_messages", response_model=ApiResponse)
async def get_messages(
    params: Dict[str, Any] = Body(...),
    service: GmailService = Depends(get_gmail_service)
):
    try:
        filters_data = params.get('filters', {})
        page_token = params.get('pageToken')
        
        filters = MessageFilters(**filters_data)
        return service.get_messages(page_token, filters)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_message", response_model=ApiResponse)
async def get_message(
    params: Dict[str, Any] = Body(...),
    service: GmailService = Depends(get_gmail_service)
):
    try:
        message_id = params.get('message_id')
        if not message_id:
            raise HTTPException(status_code=400, detail="message_id is required")
            
        return service.get_message(message_id)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/delete_message")
async def delete_message(
    params: Dict[str, Any] = Body(...),
    service: GmailService = Depends(get_gmail_service)
):
    try:
        message_id = params.get('message_id')
        if not message_id:
            raise HTTPException(status_code=400, detail="message_id is required")
            
        service.delete_message(message_id)
        return {"status": "success"}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/send_message", response_model=ApiResponse)
async def send_message(
    params: Dict[str, Any] = Body(...),
    service: GmailService = Depends(get_gmail_service)
):
    try:
        message_id = params.get('message_id')
        if not message_id:
            raise HTTPException(status_code=400, detail="message_id is required")
            
        return service.send_message(message_id)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_drafts", response_model=ApiResponse)
async def get_drafts(
    params: Dict[str, Any] = Body(...),
    service: GmailService = Depends(get_gmail_service)
):
    try:
        page_token = params.get('pageToken')
        return service.get_drafts(page_token)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create_draft", response_model=ApiResponse)
async def create_draft(
    params: Dict[str, Any] = Body(...),
    service: GmailService = Depends(get_gmail_service)
):
    try:
        draft_data = params.get('draft_args', params)
        draft_args = DraftMessage(**draft_data)
        return service.create_draft(draft_args)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/delete_draft")
async def delete_draft(
    params: Dict[str, Any] = Body(...),
    service: GmailService = Depends(get_gmail_service)
):
    try:
        draft_id = params.get('draft_id')
        if not draft_id:
            raise HTTPException(status_code=400, detail="draft_id is required")
            
        service.delete_draft(draft_id)
        return {"status": "success"}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/modify_draft", response_model=ApiResponse)
async def modify_draft(
    params: Dict[str, Any] = Body(...),
    service: GmailService = Depends(get_gmail_service)
):
    try:
        draft_id = params.get('draft_id')
        update_data = params.get('update_args', {})
        
        if not draft_id:
            raise HTTPException(status_code=400, detail="draft_id is required")
            
        update_args = DraftMessage(**update_data)
        return service.modify_draft(draft_id, update_args)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))



