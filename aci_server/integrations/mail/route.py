from fastapi import APIRouter, Body, Depends, HTTPException
from starlette.requests import Request as FastAPIRequest
from typing import Dict, Any
from .schema import *
from .service import MailSMTPService
from .client import MailSMTPClient, MailSMTPError
from ..common.auth import get_provider_custom_auth
from ..common.input_schema_decorator import schema
from ..common.utils import apply_error_handler_to_service, apply_error_handler_to_router, apply_error_handler_to_client
from ..common.examples_handler import ExamplesLoader
import os
import smtplib
import imaplib

router = APIRouter(prefix="/mail", tags=["mail"])
examples = ExamplesLoader()


async def get_mail_smtp_service(request: FastAPIRequest):
    try:
        auth_params = await get_provider_custom_auth(request, "mail")
        
        username = auth_params.get("username")
        password = auth_params.get("password")

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
        
        # Always use Gmail settings regardless of provided parameters
        smtp_host = "smtp.gmail.com"
        smtp_port = 587
        imap_host = "imap.gmail.com"
        imap_port = 993
        use_ssl = False
        use_tls = True
        imap_use_ssl = True
            
        try:
            client = MailSMTPClient(
                smtp_host=smtp_host,
                smtp_port=int(smtp_port),
                imap_host=imap_host,
                imap_port=int(imap_port),
                username=username,
                password=password,
                use_ssl=use_ssl,
                use_tls=use_tls,
                imap_use_ssl=imap_use_ssl
            )
            apply_error_handler_to_client(client)
            
            service = MailSMTPService(client)
            apply_error_handler_to_service(service)
            
            return service
        except MailSMTPError as e:
            raise HTTPException(
                status_code=401,
                detail=f"Mail connection error: {e.message}"
            )
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
    output_schema_class=EmailMessageList,
    examples=examples["/mail/get_messages"]
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
    output_schema_class=EmailMessage,
    examples=examples["/mail/get_message"]
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
    output_schema_class=SendMessageResponse,
    examples=examples["/mail/send_message"]
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
    output_schema_class=FolderList,
    examples=examples["/mail/get_folders"]
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
    output_schema_class=GenericResponse,
    examples=examples["/mail/create_folder"]
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
    output_schema_class=GenericResponse,
    examples=examples["/mail/delete_message"]
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
    output_schema_class=GenericResponse,
    examples=examples["/mail/move_message"]
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
        username = params.get("username")
        password = params.get("password")
        
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
        

        settings = {
            "smtp_host": "smtp.gmail.com",
            "smtp_port": 587,
            "imap_host": "imap.gmail.com", 
            "imap_port": 993,
            "use_ssl": False,
            "use_tls": True,
            "imap_use_ssl": True
        }
        
        smtp_error = None
        imap_error = None
        
        try:
            if settings.get("use_ssl", False):
                smtp_client = smtplib.SMTP_SSL(settings["smtp_host"], settings["smtp_port"], timeout=30)
            else:
                smtp_client = smtplib.SMTP(settings["smtp_host"], settings["smtp_port"], timeout=30)
                if settings.get("use_tls", True):
                    smtp_client.starttls()
            
            smtp_client.login(username, password)
            smtp_client.quit()
        except Exception as e:
            smtp_error = str(e)
        
        try:
            if settings.get("imap_use_ssl", True):
                imap_client = imaplib.IMAP4_SSL(settings["imap_host"], settings["imap_port"], timeout=30)
            else:
                imap_client = imaplib.IMAP4(settings["imap_host"], settings["imap_port"], timeout=30)
                if settings.get("imap_use_tls", False):
                    imap_client.starttls()
            
            imap_client.login(username, password)
            
            try:
                result, data = imap_client.select('INBOX', readonly=True)
                if result != 'OK':
                    raise Exception(f"Failed to select INBOX: {data[0].decode() if data else 'Unknown error'}")
                
                result, data = imap_client.search(None, 'ALL')
                if result != 'OK':
                    raise Exception(f"Failed to search messages: {data[0].decode() if data else 'Unknown error'}")
                
                message_count = len(data[0].split())
                
                imap_client.close()
                try:
                    imap_client.logout()
                except Exception as logout_error:
                    # Ignore logout errors as the connection was already established successfully
                    pass
                
                return {
                    "valid": True,
                    "message": f"SMTP and IMAP connections successful. Found {message_count} messages in inbox.",
                    "settings_used": settings,
                    "message_count": message_count
                }
                
            except Exception as fetch_error:
                try:
                    imap_client.logout()
                except Exception:
                    # Ignore logout errors
                    pass
                return {
                    "valid": False,
                    "message": f"Connected to mail server but couldn't fetch emails: {str(fetch_error)}",
                    "settings_used": settings
                }
                
        except Exception as e:
            imap_error = str(e)
        
        if smtp_error and imap_error:
            return {
                "valid": False,
                "message": f"SMTP Error: {smtp_error}, IMAP Error: {imap_error}",
                "settings_used": settings
            }
        elif smtp_error:
            return {
                "valid": False,
                "message": f"SMTP Error: {smtp_error}",
                "settings_used": settings
            }
        elif imap_error:
            return {
                "valid": False,
                "message": f"IMAP Error: {imap_error}",
                "settings_used": settings
            }
        
        return {
            "valid": True,
            "message": "SMTP and IMAP connections successful",
            "settings_used": settings
        }
    except Exception as e:
        return {
            "valid": False,
            "message": f"Connection validation failed: {str(e)}"
        }

@router.post("/test_connection", response_model=ApiResponse)
async def test_connection(
    service: MailSMTPService = Depends(get_mail_smtp_service)
):
    """Test connection to SMTP and IMAP servers without sending emails."""
    return service.test_connection()

@router.post("/get_default_settings")
async def get_default_settings(
    params: Dict[str, Any] = Body(...),
):
    """
    Get default settings for popular email services.
    Expects a service name in the params, or returns all supported services if no service specified.
    """
    # Define default settings for popular email services
    default_settings = {
        "gmail": {
            "smtp_host": "smtp.gmail.com",
            "smtp_port": 587,
            "imap_host": "imap.gmail.com", 
            "imap_port": 993,
            "use_ssl": False,  # For SMTP
            "use_tls": True,   # For SMTP
            "imap_use_ssl": True,  # For IMAP
            "notes": "For Gmail accounts with 2FA enabled, you need to use an App Password instead of your regular password."
        },
        "outlook": {
            "smtp_host": "smtp-mail.outlook.com",
            "smtp_port": 587,
            "imap_host": "outlook.office365.com",
            "imap_port": 993,
            "use_ssl": False,
            "use_tls": True,
            "imap_use_ssl": True,
            "notes": "Use your full email address as the username."
        },
        "yahoo": {
            "smtp_host": "smtp.mail.yahoo.com",
            "smtp_port": 587,
            "imap_host": "imap.mail.yahoo.com",
            "imap_port": 993,
            "use_ssl": False,
            "use_tls": True,
            "imap_use_ssl": True,
            "notes": "For Yahoo accounts with 2FA enabled, you need to generate an app password."
        },
        "zoho": {
            "smtp_host": "smtp.zoho.com",
            "smtp_port": 587,
            "imap_host": "imap.zoho.com",
            "imap_port": 993,
            "use_ssl": False,
            "use_tls": True,
            "imap_use_ssl": True,
            "notes": "Use your full email address as the username."
        },
        "aol": {
            "smtp_host": "smtp.aol.com",
            "smtp_port": 587,
            "imap_host": "imap.aol.com",
            "imap_port": 993,
            "use_ssl": False,
            "use_tls": True,
            "imap_use_ssl": True,
            "notes": "For AOL accounts with 2FA enabled, you need to generate an app password."
        },
        "protonmail": {
            "smtp_host": "smtp.protonmail.ch",
            "smtp_port": 587,
            "imap_host": "imap.protonmail.ch",
            "imap_port": 993,
            "use_ssl": False,
            "use_tls": True,
            "imap_use_ssl": True,
            "notes": "You need to set up ProtonMail Bridge and use the bridge password, not your regular password."
        },
        "gmx": {
            "smtp_host": "mail.gmx.com",
            "smtp_port": 587,
            "imap_host": "imap.gmx.com",
            "imap_port": 993,
            "use_ssl": False,
            "use_tls": True,
            "imap_use_ssl": True,
            "notes": "Use your full email address as the username."
        }
    }
    
    # Check if a specific service was requested
    service = params.get("service", "").lower()
    if service and service in default_settings:
        return {
            "service": service,
            "settings": default_settings[service]
        }
    elif service:
        return {
            "error": f"Service '{service}' not found",
            "available_services": list(default_settings.keys())
        }
    else:
        # Return all available services
        return {
            "available_services": list(default_settings.keys()),
            "settings": default_settings
        }

@router.get("/list_services")
async def list_services():
    """List all supported email services for quick reference."""
    services = [
        {"id": "gmail", "name": "Gmail", "domain": "gmail.com"},
        {"id": "outlook", "name": "Outlook / Office 365", "domain": "outlook.com"},
        {"id": "yahoo", "name": "Yahoo Mail", "domain": "yahoo.com"},
        {"id": "zoho", "name": "Zoho Mail", "domain": "zoho.com"},
        {"id": "aol", "name": "AOL Mail", "domain": "aol.com"},
        {"id": "protonmail", "name": "ProtonMail", "domain": "protonmail.com"},
        {"id": "gmx", "name": "GMX Mail", "domain": "gmx.com"}
    ]
    
    return {
        "services": services
    }

@router.post("/detect_settings")
async def detect_settings(
    params: Dict[str, Any] = Body(...),
):
    """
    Auto-detect mail settings based on an email address domain.
    Provide an email address in the params and get recommended settings.
    """
    email = params.get("email", "")
    if not email or "@" not in email:
        return {
            "error": "Valid email address is required",
            "success": False
        }
    
    # Extract domain from email
    domain = email.split("@")[-1].lower()
    
    # Always use Gmail settings regardless of domain
    gmail_settings = {
        "smtp_host": "smtp.gmail.com",
        "smtp_port": 587,
        "imap_host": "imap.gmail.com", 
        "imap_port": 993,
        "use_ssl": False,
        "use_tls": True,
        "imap_use_ssl": True,
        "notes": "Using Gmail settings for all domains. For accounts with 2FA enabled, you need to use an App Password instead of your regular password."
    }
    
    return {
        "email": email,
        "detected_service": "gmail",
        "settings": gmail_settings,
        "success": True
    }

apply_error_handler_to_router(router) 