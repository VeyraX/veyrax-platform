from fastapi import APIRouter, Depends, HTTPException, Request as FastAPIRequest, Body
from typing import Optional, Dict, Any
from .schema import (
    MessageList, Message, DraftMessage, DraftResponse, DraftList, 
    MessageFilters, ApiResponse, GetMessagesParams, GetMessageParams,
    DeleteMessageParams, SendMessageParams, GetDraftsParams, 
    CreateDraftParams, DeleteDraftParams, ModifyDraftParams
)
from .service import GmailService
from .client import GmailClient
import pickle
import os
from ..common.utils import get_router_tools
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GoogleRequest
from ..common.auth import TokenService, GoogleTokenRefresher
from ..common.input_schema_decorator import input_schema
from pydantic import ValidationError

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
@input_schema(schema_class=GetMessagesParams)
async def get_messages(
    params: Dict[str, Any] = Body(...),
    service: GmailService = Depends(get_gmail_service)
):
    try:
        validated_params = GetMessagesParams(**params)
        filters = validated_params.filters
        return service.get_messages(validated_params.pageToken, filters)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_message", response_model=ApiResponse)
@input_schema(schema_class=GetMessageParams)
async def get_message(
    params: Dict[str, Any] = Body(...),
    service: GmailService = Depends(get_gmail_service)
):
    try:
        validated_params = GetMessageParams(**params)
        return service.get_message(validated_params.message_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/delete_message")
@input_schema(schema_class=DeleteMessageParams)
async def delete_message(
    params: Dict[str, Any] = Body(...),
    service: GmailService = Depends(get_gmail_service)
):
    try:
        validated_params = DeleteMessageParams(**params)
        service.delete_message(validated_params.message_id)
        return {"status": "success"}
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/send_message", response_model=ApiResponse)
@input_schema(schema_class=SendMessageParams)
async def send_message(
    params: Dict[str, Any] = Body(...),
    service: GmailService = Depends(get_gmail_service)
):
    try:
        validated_params = SendMessageParams(**params)
        return service.send_message(validated_params.message_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_drafts", response_model=ApiResponse)
@input_schema(schema_class=GetDraftsParams)
async def get_drafts(
    params: Dict[str, Any] = Body(...),
    service: GmailService = Depends(get_gmail_service)
):
    try:
        validated_params = GetDraftsParams(**params)
        return service.get_drafts(validated_params.pageToken)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create_draft", response_model=ApiResponse)
@input_schema(schema_class=CreateDraftParams)
async def create_draft(
    params: Dict[str, Any] = Body(...),
    service: GmailService = Depends(get_gmail_service)
):
    try:
        validated_params = CreateDraftParams(**params)
        return service.create_draft(validated_params.draft_args)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/delete_draft")
@input_schema(schema_class=DeleteDraftParams)
async def delete_draft(
    params: Dict[str, Any] = Body(...),
    service: GmailService = Depends(get_gmail_service)
):
    try:
        validated_params = DeleteDraftParams(**params)
        service.delete_draft(validated_params.draft_id)
        return {"status": "success"}
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/modify_draft", response_model=ApiResponse)
@input_schema(schema_class=ModifyDraftParams)
async def modify_draft(
    params: Dict[str, Any] = Body(...),
    service: GmailService = Depends(get_gmail_service)
):
    try:
        validated_params = ModifyDraftParams(**params)
        return service.modify_draft(validated_params.draft_id, validated_params.update_args)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))