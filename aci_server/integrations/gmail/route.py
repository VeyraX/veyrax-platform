from fastapi import APIRouter, Depends, HTTPException, Request as FastAPIRequest, Body
from typing import Dict, Any
from .schema import (
 ApiResponse, GetMessagesParams, GetMessageParams,
    DeleteMessageParams, SendMessageParams, GetDraftsParams, 
    CreateDraftParams, DeleteDraftParams, ModifyDraftParams,
    GetMessagesResponse, GetMessageResponse, DeleteMessageResponse,
    SendMessageResponse, GetDraftsResponse, CreateDraftResponse,
    DeleteDraftResponse, ModifyDraftResponse
)
from .service import GmailService
from .client import GmailClient
import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GoogleRequest
from ..common.auth import TokenService, GoogleTokenRefresher
from ..common.input_schema_decorator import schema
from pydantic import ValidationError
from ..common.utils import format_validation_error
from ..common.examples_handler import ExamplesLoader

router = APIRouter(prefix="/gmail", tags=["gmail"])

examples = ExamplesLoader()

async def get_gmail_service(request: FastAPIRequest):
    token_data = await TokenService.get_user_token(request, 'gmail')
    
    if TokenService.is_token_expired(token_data):
        print('refreshing token')
        try:
            token_data = await GoogleTokenRefresher.refresh(request, token_data)
            print(f"new token data: {token_data}")
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
@schema(input_schema_class=GetMessagesParams, output_schema_class=GetMessagesResponse, examples=examples["/gmail/get_messages"])
async def get_messages(
    params: Dict[str, Any] = Body(...),
    service: GmailService = Depends(get_gmail_service)
):
    try:
        validated_params = GetMessagesParams(**params)
        filters = validated_params.filters
        return service.get_messages(validated_params.pageToken, filters)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, GetMessagesParams))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_message", response_model=ApiResponse)
@schema(input_schema_class=GetMessageParams, output_schema_class=GetMessageResponse, examples=examples["/gmail/get_message"])
async def get_message(
    params: Dict[str, Any] = Body(...),
    service: GmailService = Depends(get_gmail_service)
):
    try:
        validated_params = GetMessageParams(**params)
        return service.get_message(validated_params.message_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetMessageParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/delete_message")
@schema(input_schema_class=DeleteMessageParams, output_schema_class=DeleteMessageResponse, examples=examples["/gmail/delete_message"])
async def delete_message(
    params: Dict[str, Any] = Body(...),
    service: GmailService = Depends(get_gmail_service)
):
    try:
        validated_params = DeleteMessageParams(**params)
        service.delete_message(validated_params.message_id)
        return {"status": "success"}
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'DeleteMessageParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/send_message", response_model=ApiResponse)
@schema(input_schema_class=SendMessageParams, output_schema_class=SendMessageResponse, examples=examples["/gmail/send_message"])
async def send_message(
    params: Dict[str, Any] = Body(...),
    service: GmailService = Depends(get_gmail_service)
):
    try:
        validated_params = SendMessageParams(**params)
        return service.send_message(validated_params.message_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'SendMessageParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_drafts", response_model=ApiResponse)
@schema(input_schema_class=GetDraftsParams, output_schema_class=GetDraftsResponse, examples=examples["/gmail/get_drafts"])
async def get_drafts(
    params: Dict[str, Any] = Body(...),
    service: GmailService = Depends(get_gmail_service)
):
    try:
        validated_params = GetDraftsParams(**params)
        return service.get_drafts(validated_params.pageToken)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetDraftsParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create_draft", response_model=ApiResponse)
@schema(input_schema_class=CreateDraftParams, output_schema_class=CreateDraftResponse, examples=examples["/gmail/create_draft"])
async def create_draft(
    params: Dict[str, Any] = Body(...),
    service: GmailService = Depends(get_gmail_service)
):
    try:
        validated_params = CreateDraftParams(**params)
        return service.create_draft(validated_params.draft_args)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'CreateDraftParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/delete_draft")
@schema(input_schema_class=DeleteDraftParams, output_schema_class=DeleteDraftResponse, examples=examples["/gmail/delete_draft"])
async def delete_draft(
    params: Dict[str, Any] = Body(...),
    service: GmailService = Depends(get_gmail_service)
):
    try:
        validated_params = DeleteDraftParams(**params)
        service.delete_draft(validated_params.draft_id)
        return {"status": "success"}
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'DeleteDraftParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/modify_draft", response_model=ApiResponse)
@schema(input_schema_class=ModifyDraftParams, output_schema_class=ModifyDraftResponse, examples=examples["/gmail/modify_draft"])
async def modify_draft(
    params: Dict[str, Any] = Body(...),
    service: GmailService = Depends(get_gmail_service)
):
    try:
        validated_params = ModifyDraftParams(**params)
        return service.modify_draft(validated_params.draft_id, validated_params.update_args)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'ModifyDraftParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))