from fastapi import APIRouter, Depends, HTTPException, Request as FastAPIRequest
from typing import Optional
from .schema import MessageList, Message, DraftMessage, DraftResponse, DraftList, MessageFilters
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

@router.get("/messages", response_model=MessageList)
async def get_messages(
    pageToken: Optional[str] = None,
    filters: MessageFilters = Depends(),
    service: GmailService = Depends(get_gmail_service)
):
    return service.get_messages(pageToken, filters)

@router.get("/messages/{message_id}", response_model=Message)
async def get_message(
    message_id: str,
    service: GmailService = Depends(get_gmail_service)
):
    return service.get_message(message_id)

@router.delete("/messages/{message_id}")
async def delete_message(
    message_id: str,
    service: GmailService = Depends(get_gmail_service)
):
    service.delete_message(message_id)
    return {"status": "success"}

@router.post("/messages/{message_id}/send")
async def send_message(
    message_id: str,
    service: GmailService = Depends(get_gmail_service)
):
    message_id = service.send_message(message_id)
    return {"message_id": message_id}

@router.get("/drafts", response_model=DraftList)
async def get_drafts(
    pageToken: Optional[str] = None,
    service: GmailService = Depends(get_gmail_service)
):
    return service.get_drafts(pageToken)

@router.post("/drafts", response_model=DraftResponse)
async def create_draft(
    draft_args: DraftMessage,
    service: GmailService = Depends(get_gmail_service)
):
    return service.create_draft(draft_args)

@router.delete("/drafts/{draft_id}")
async def delete_draft(
    draft_id: str,
    service: GmailService = Depends(get_gmail_service)
):
    service.delete_draft(draft_id)
    return {"status": "success"}

@router.patch("/drafts/{draft_id}", response_model=Message)
async def modify_draft(
    draft_id: str,
    update_args: DraftMessage,
    service: GmailService = Depends(get_gmail_service)
):
    return service.modify_draft(
        draft_id,
        to=update_args.recipient,
        subject=update_args.subject,
        body=update_args.body
    )



