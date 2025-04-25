from fastapi import APIRouter, Depends, HTTPException, Request, Body
from typing import Dict, Any
import asyncio
from .schema import *
from .service import WhatsAppService
from .client import WhatsAppClient
from ..common.input_schema_decorator import schema
from ..common.auth import get_user_from_request
from ..common.utils import apply_error_handler_to_service, apply_error_handler_to_router
from ..common.examples_handler import ExamplesLoader

router = APIRouter(prefix="/whatsapp", tags=["whatsapp"])

examples = ExamplesLoader()

async def get_whatsapp_service(request: Request):
    try:
        user_id = await get_user_from_request(request)
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Authentication required")
            
        client = WhatsAppClient(user_id)
        service = WhatsAppService(client)
        apply_error_handler_to_service(service)
        return service
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize WhatsApp service: {str(e)}")

async def verify_whatsapp_connection(
    request: Request,
    service: WhatsAppService = Depends(get_whatsapp_service)
):
    
    if request.url.path.endswith("/authenticate") or request.url.path.endswith("/check_status"):
        return service
    
    try:
        # Add a 15-second timeout for the verify operation
        async with asyncio.timeout(30):
            status = service.client.check_status()
            if not status.is_logged_in:
                # Try to authenticate if not logged in (useful after server restart)
                auth_response = service.authenticate()
                # Check if authentication was successful
                if not getattr(auth_response.data, "is_logged_in", False):
                    # If authentication wasn't successful, still throw the error
                    error_message = "WhatsApp connection is not active"
                    if status.error:
                        error_message = f"WhatsApp connection error: {status.error}"
                    raise HTTPException(status_code=403, detail=error_message)
    except asyncio.TimeoutError:
        # If the operation times out, return a service unavailable error
        raise HTTPException(status_code=503, detail="WhatsApp service unavailable: operation timed out after 15 seconds")
    except Exception as e:
        # For other errors, return a more specific error if possible
        raise HTTPException(status_code=503, detail=f"WhatsApp service error: {str(e)}")
    
    return service

@router.post("/authenticate", response_model=ApiResponse)
@schema(input_schema_class=AuthenticateRequest, output_schema_class=AuthenticateResponse, examples=examples["/whatsapp/authenticate"])
async def authenticate(
    params: Dict[str, Any] = Body(...),
    service: WhatsAppService = Depends(get_whatsapp_service)
):
    validated_params = AuthenticateRequest(**params)
    return service.authenticate(validated_params.include_qr_base64, validated_params.include_qr_ascii, validated_params.include_component)

@router.post("/check_status", response_model=ApiResponse)
@schema(input_schema_class=CheckStatusRequest, output_schema_class=CheckStatusResponse, examples=examples["/whatsapp/check_status"])
async def check_status(
    request: Request,
    service: WhatsAppService = Depends(get_whatsapp_service)
):
    return service.check_status()

@router.post("/send_message", response_model=ApiResponse)
@schema(input_schema_class=SendMessageRequest, output_schema_class=SendMessageResponseSchema, examples=examples["/whatsapp/send_message"])
async def send_message(
    params: Dict[str, Any] = Body(...),
    request: Request = None,
    service: WhatsAppService = Depends(verify_whatsapp_connection)
):
    validated_params = SendMessageRequest(**params)
    return service.send_message(validated_params.recipient, validated_params.message)


# SYSTEM TOOL, DON'T DELETE
# @router.post("/list_users", response_model=ApiResponse)
# @schema(input_schema_class=ListUsersRequest, output_schema_class=ListUsersResponse, examples=examples["/whatsapp/list_users"])
# async def list_users(
#     request: Request,
#     service: WhatsAppService = Depends(verify_whatsapp_connection)
# ):
#     return service.list_users()

@router.post("/get_chats", response_model=ApiResponse)
@schema(input_schema_class=GetChatsRequest, output_schema_class=GetChatsResponse, examples=examples["/whatsapp/get_chats"])
async def get_chats(
    params: Dict[str, Any] = Body(...),
    request: Request = None,
    service: WhatsAppService = Depends(verify_whatsapp_connection)
):
    validated_params = GetChatsRequest(**params)
    return service.get_chats(
        query=validated_params.query,
        limit=validated_params.limit,
        page=validated_params.page,
        include_last_message=validated_params.include_last_message,
        sort_by=validated_params.sort_by
    )

@router.post("/get_messages", response_model=ApiResponse)
@schema(input_schema_class=GetMessagesRequest, output_schema_class=GetMessagesResponse, examples=examples["/whatsapp/get_messages"])
async def get_messages(
    params: Dict[str, Any] = Body(...),
    request: Request = None,
    service: WhatsAppService = Depends(verify_whatsapp_connection)
):
    validated_params = GetMessagesRequest(**params)
    return service.get_messages(
        chat_jid=validated_params.chat_jid,
        query=validated_params.query,
        limit=validated_params.limit,
        page=validated_params.page,
        include_context=validated_params.include_context,
        sender_phone_number=validated_params.sender_phone_number,
        start_date=validated_params.start_date,
        end_date=validated_params.end_date
    )

@router.post("/search_contacts", response_model=ApiResponse)
@schema(input_schema_class=SearchContactsRequest, output_schema_class=SearchContactsResponse, examples=examples["/whatsapp/search_contacts"])
async def search_contacts(
    params: Dict[str, Any] = Body(...),
    request: Request = None,
    service: WhatsAppService = Depends(verify_whatsapp_connection)
):
    validated_params = SearchContactsRequest(**params)
    return service.search_contacts(validated_params.query)

@router.post("/get_chat", response_model=ApiResponse)
@schema(input_schema_class=GetChatRequest, output_schema_class=GetChatResponse, examples=examples["/whatsapp/get_chat"])
async def get_chat(
    params: Dict[str, Any] = Body(...),
    request: Request = None,
    service: WhatsAppService = Depends(verify_whatsapp_connection)
):
    validated_params = GetChatRequest(**params)
    return service.get_chat(
        validated_params.chat_jid,
        validated_params.include_last_message
    )

@router.post("/get_recent_messages", response_model=ApiResponse)
@schema(input_schema_class=GetRecentMessagesRequest, output_schema_class=GetRecentMessagesResponse, examples=examples["/whatsapp/get_recent_messages"])
async def get_recent_messages(
    params: Dict[str, Any] = Body(...),
    request: Request = None,
    service: WhatsAppService = Depends(verify_whatsapp_connection)
):
    validated_params = GetRecentMessagesRequest(**params)
    return service.get_recent_messages(validated_params.limit)

@router.post("/validate_user")
async def validate_user(request: Request):
    try:
        user_id = await get_user_from_request(request)
        if not user_id:
            return {"valid": False, "message": "Authentication required"}
        
        client = WhatsAppClient(user_id)
        status = client.check_status()
        
        if status.is_logged_in:
            return {"valid": True, "message": "User is logged in"}
        elif status.error:
            return {"valid": False, "message": f"Error: {status.error}"}
        else:
            return {"valid": False, "message": "User is not logged in"}
    except Exception as e:
        return {"valid": False, "message": f"Error validating user: {str(e)}"}

@router.post("/disconnect", response_model=ApiResponse)
@schema(input_schema_class=DisconnectRequest, output_schema_class=DisconnectResponse, examples=examples["/whatsapp/disconnect"])
async def disconnect(
    request: Request,
    service: WhatsAppService = Depends(get_whatsapp_service)
):
    """Disconnect a user from WhatsApp and delete all their data."""
    return service.disconnect()

apply_error_handler_to_router(router) 