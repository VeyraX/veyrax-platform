from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from .schema import MessageList, Message, DraftMessage, DraftResponse, DraftList, DraftUpdate, MessageFilters
from .service import GmailService
from .client import GmailClient
import pickle
import os
from ..common.utils import get_router_tools


router = APIRouter(prefix="/gmail", tags=["gmail"])

async def get_gmail_service():
    if os.path.exists('credentials/token.pickle'):
        with open('credentials/token.pickle', 'rb') as token:
            creds = pickle.load(token)
    else:
        raise HTTPException(status_code=404, detail="Credentials file not found")
    
    client = GmailClient(creds)
    return GmailService(client)

@router.get("/messages", response_model=MessageList)
async def get_messages(
    pageToken: Optional[str] = None,
    body_keywords: Optional[str] = None,
    recipient: Optional[str] = None,
    subject_keywords: Optional[str] = None,
    after_date: Optional[str] = None,
    before_date: Optional[str] = None,
    service: GmailService = Depends(get_gmail_service)
):
    filters = MessageFilters(
        body_keywords=body_keywords,
        recipient=recipient,
        subject_keywords=subject_keywords,
        after_date=after_date,
        before_date=before_date
    )
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
    draft: DraftMessage,
    service: GmailService = Depends(get_gmail_service)
):
    return service.create_draft(draft.to, draft.subject, draft.body)

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
    update: DraftUpdate,
    service: GmailService = Depends(get_gmail_service)
):
    return service.modify_draft(
        draft_id,
        to=update.recipient,
        subject=update.subject,
        body=update.body
    )

