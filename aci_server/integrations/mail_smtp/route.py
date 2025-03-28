from fastapi import APIRouter, Body, Depends, HTTPException
from starlette.requests import Request as FastAPIRequest
from typing import Dict, Any
from .schema import (
    GetMessagesParams,
    GetMessageParams,
    SendMessageParams,
    CreateFolderParams,
    DeleteMessageParams,
    GetFoldersParams,
    MoveMessageParams,
    ApiResponse
)
from .service import MailSMTPService
from .client import MailSMTPClient, MailSMTPError
from ..common.auth import get_provider_custom_auth
from ..common.input_schema_decorator import schema
from ..common.utils import apply_error_handler_to_service, apply_error_handler_to_router, apply_error_handler_to_client
from ..common.examples_handler import ExamplesLoader

router = APIRouter(prefix="/mail_smtp", tags=["mail_smtp"])
examples = ExamplesLoader()

async def get_mail_smtp_service(request: FastAPIRequest):
    try:
        auth_params = await get_provider_custom_auth(request, "mail_smtp")
        
        # Hardcoded Google settings for testing
        smtp_host = "smtp.gmail.com"
        smtp_port = 587
        imap_host = "imap.gmail.com"
        imap_port = 993
        use_ssl = True
        use_tls = True
        
        # Get authentication from request
        username = auth_params.get("username")
        password = auth_params.get("password")
        
        # Original dynamic configuration (commented out)
        # smtp_host = auth_params.get("smtp_host")
        # smtp_port = auth_params.get("smtp_port")
        # imap_host = auth_params.get("imap_host")
        # imap_port = auth_params.get("imap_port")
        # use_ssl = auth_params.get("use_ssl", True)
        # use_tls = auth_params.get("use_tls", False)
        
        # # If service-specific hosts aren't provided, try to use common ones
        # if not smtp_host:
        #     smtp_host = auth_params.get("host")
        # 
        # if not imap_host:
        #     imap_host = auth_params.get("host")
        # 
        # if not smtp_port:
        #     smtp_port = auth_params.get("port")
        #     
        # if not imap_port:
        #     imap_port = auth_params.get("port")
        # 
        # # Set default ports if not provided
        # if not smtp_port:
        #     smtp_port = 587 if use_tls else (465 if use_ssl else 25)
        #     
        # if not imap_port:
        #     imap_port = 993 if use_ssl else 143
        
        # Keep validation for username and password
        if not username:
            raise HTTPException(
                status_code=401, 
                detail="Missing required parameter: username"
            )
        
        if not password:
            raise HTTPException(
                status_code=401, 
                detail="Missing required parameter: password"
            )
        
        # Create separate clients for SMTP and IMAP
        client = MailSMTPClient(
            smtp_host=smtp_host,
            smtp_port=int(smtp_port),
            imap_host=imap_host,
            imap_port=int(imap_port),
            username=username,
            password=password,
            use_ssl=use_ssl,
            use_tls=use_tls
        )
        apply_error_handler_to_client(client)
        
        service = MailSMTPService(client)
        apply_error_handler_to_service(service)
        
        return service
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Failed to initialize Mail SMTP/IMAP service: {str(e)}"
        )

@router.post("/get_messages", response_model=ApiResponse)
@schema(
    input_schema_class=GetMessagesParams,
    output_schema_class=ApiResponse,
    examples=examples["/mail_smtp/get_messages"]
)
async def get_messages(
    params: Dict[str, Any] = Body(...),
    service: MailSMTPService = Depends(get_mail_smtp_service)
):
    validated_params = GetMessagesParams(**params)
    return service.get_messages(validated_params)

@router.post("/get_message", response_model=ApiResponse)
@schema(
    input_schema_class=GetMessageParams,
    output_schema_class=ApiResponse,
    examples=examples["/mail_smtp/get_message"]
)
async def get_message(
    params: Dict[str, Any] = Body(...),
    service: MailSMTPService = Depends(get_mail_smtp_service)
):
    validated_params = GetMessageParams(**params)
    return service.get_message(validated_params)

@router.post("/send_message", response_model=ApiResponse)
@schema(
    input_schema_class=SendMessageParams,
    output_schema_class=ApiResponse,
    examples=examples["/mail_smtp/send_message"]
)
async def send_message(
    params: Dict[str, Any] = Body(...),
    service: MailSMTPService = Depends(get_mail_smtp_service)
):
    validated_params = SendMessageParams(**params)
    return service.send_message(validated_params)

@router.post("/get_folders", response_model=ApiResponse)
@schema(
    input_schema_class=GetFoldersParams,
    output_schema_class=ApiResponse,
    examples=examples["/mail_smtp/get_folders"]
)
async def get_folders(
    params: Dict[str, Any] = Body(...),
    service: MailSMTPService = Depends(get_mail_smtp_service)
):
    validated_params = GetFoldersParams(**params)
    return service.get_folders(validated_params)

@router.post("/create_folder", response_model=ApiResponse)
@schema(
    input_schema_class=CreateFolderParams,
    output_schema_class=ApiResponse,
    examples=examples["/mail_smtp/create_folder"]
)
async def create_folder(
    params: Dict[str, Any] = Body(...),
    service: MailSMTPService = Depends(get_mail_smtp_service)
):
    validated_params = CreateFolderParams(**params)
    return service.create_folder(validated_params)

@router.post("/delete_message", response_model=ApiResponse)
@schema(
    input_schema_class=DeleteMessageParams,
    output_schema_class=ApiResponse,
    examples=examples["/mail_smtp/delete_message"]
)
async def delete_message(
    params: Dict[str, Any] = Body(...),
    service: MailSMTPService = Depends(get_mail_smtp_service)
):
    validated_params = DeleteMessageParams(**params)
    return service.delete_message(validated_params)

@router.post("/move_message", response_model=ApiResponse)
@schema(
    input_schema_class=MoveMessageParams,
    output_schema_class=ApiResponse,
    examples=examples["/mail_smtp/move_message"]
)
async def move_message(
    params: Dict[str, Any] = Body(...),
    service: MailSMTPService = Depends(get_mail_smtp_service)
):
    validated_params = MoveMessageParams(**params)
    return service.move_message(validated_params)

@router.post("/validate_key")
async def validate_key(
    params: Dict[str, Any] = Body(...),
):
    try:
        # Hardcoded Google settings for testing
        smtp_host = "smtp.gmail.com"
        smtp_port = 587
        imap_host = "imap.gmail.com"
        imap_port = 993
        use_ssl = True
        use_tls = True
        
        # Get authentication from params
        username = params.get("username")
        password = params.get("password")
        
        # Original dynamic configuration (commented out)
        # smtp_host = params.get("smtp_host", params.get("host"))
        # smtp_port = params.get("smtp_port", params.get("port"))
        # imap_host = params.get("imap_host", params.get("host"))
        # imap_port = params.get("imap_port", params.get("port"))
        # use_ssl = params.get("use_ssl", True)
        # use_tls = params.get("use_tls", False)
        # 
        # # Set default ports if not provided
        # if not smtp_port:
        #     smtp_port = 587 if use_tls else (465 if use_ssl else 25)
        #     
        # if not imap_port:
        #     imap_port = 993 if use_ssl else 143
        
        # Keep validation for username and password
        if not username:
            return {
                "valid": False,
                "message": "Missing required parameter: username"
            }
        
        if not password:
            return {
                "valid": False,
                "message": "Missing required parameter: password"
            }
        
        # Try to connect to both IMAP and SMTP servers
        client = MailSMTPClient(
            smtp_host=smtp_host,
            smtp_port=int(smtp_port),
            imap_host=imap_host,
            imap_port=int(imap_port),
            username=username,
            password=password,
            use_ssl=use_ssl,
            use_tls=use_tls
        )
        
        # Test connection to IMAP server
        imap_conn = client._get_imap_connection()
        if imap_conn:
            imap_conn.logout()
        
        # Test connection to SMTP server
        smtp_conn = client._get_smtp_connection()
        if smtp_conn:
            smtp_conn.quit()
        
        return {
            "valid": True,
            "message": "SMTP and IMAP connections successful"
        }
    except MailSMTPError as e:
        return {
            "valid": False,
            "message": f"SMTP/IMAP connection failed: {e.message}"
        }
    except Exception as e:
        return {
            "valid": False,
            "message": f"SMTP/IMAP connection failed: {str(e)}"
        }

apply_error_handler_to_router(router) 