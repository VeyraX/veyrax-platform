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
        
        # Get authentication from request
        username = auth_params.get("username")
        password = auth_params.get("password")
        service = auth_params.get("service", "").lower()

        # Validate username and password - required for all services
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
        
        # List of known services
        known_services = ["gmail", "outlook", "yahoo", "zoho", "aol", "protonmail", "gmx"]
        
        # If a known service is specified, apply its default settings
        if service in known_services:
            # Get the default settings for this service
            default_settings_response = await get_default_settings({"service": service})
            service_defaults = default_settings_response.get("settings", {})
            
            # Apply the service defaults if not specified in auth_params
            smtp_host = auth_params.get("smtp_host") or service_defaults.get("smtp_host")
            smtp_port = auth_params.get("smtp_port") or service_defaults.get("smtp_port")
            imap_host = auth_params.get("imap_host") or service_defaults.get("imap_host")
            imap_port = auth_params.get("imap_port") or service_defaults.get("imap_port")
            
            # For SSL and TLS settings, use auth_params if specified, otherwise use service defaults
            use_ssl = auth_params.get("use_ssl") if auth_params.get("use_ssl") is not None else service_defaults.get("use_ssl", False)
            use_tls = auth_params.get("use_tls") if auth_params.get("use_tls") is not None else service_defaults.get("use_tls", True)
        else:
            # For custom or unspecified service, check all required parameters
            smtp_host = auth_params.get("smtp_host")
            smtp_port = auth_params.get("smtp_port")
            imap_host = auth_params.get("imap_host")
            imap_port = auth_params.get("imap_port")
            use_ssl = auth_params.get("use_ssl", False)
            use_tls = auth_params.get("use_tls", True)
            
            # If service-specific hosts aren't provided, try to use common ones
            if not smtp_host:
                smtp_host = auth_params.get("host")
            
            if not imap_host:
                imap_host = auth_params.get("host")
            
            if not smtp_port:
                smtp_port = auth_params.get("port")
                
            if not imap_port:
                imap_port = auth_params.get("port")
            
            # For custom services, validate that all required fields are present
            if not smtp_host:
                raise HTTPException(
                    status_code=401,
                    detail="Missing required parameter for custom service: smtp_host"
                )
                
            if not imap_host:
                raise HTTPException(
                    status_code=401,
                    detail="Missing required parameter for custom service: imap_host"
                )
        
        # Set default ports if not provided
        if not smtp_port:
            smtp_port = 587 if use_tls else (465 if use_ssl else 25)
            
        if not imap_port:
            imap_port = 993 if use_ssl else 143
        
        # For Gmail's IMAP, always use SSL
        if imap_host and "gmail" in imap_host.lower() and int(imap_port) == 993:
            use_ssl = True
            
        # Create client with proper settings
        try:
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
        except MailSMTPError as e:
            # Get specific error message from the SMTP/IMAP error
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
    """
    Validate SMTP and IMAP credentials against a mail server.
    Can automatically detect settings from email address or use a specific service.
    """
    try:
        username = params.get("username")
        password = params.get("password")
        
        # Validate required parameters
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
        
        # Get connection settings either from service or by detecting from email
        settings = {}
        if "service" in params and params["service"]:
            # Get settings for specific service
            service_response = await get_default_settings({"service": params["service"]})
            if "settings" in service_response:
                settings = service_response["settings"]
            else:
                return {
                    "valid": False,
                    "message": f"Unknown service: {params['service']}",
                    "available_services": service_response.get("available_services", [])
                }
        elif "@" in username:
            # Try to detect settings from email address
            detect_response = await detect_settings({"email": username})
            if detect_response["success"]:
                if "settings" in detect_response:
                    settings = detect_response["settings"]
                elif "possible_settings" in detect_response and detect_response["possible_settings"]:
                    settings = detect_response["possible_settings"][0]
            
        # If no settings found or provided, use manual settings or defaults (Gmail)
        if not settings:
            settings = {
                "smtp_host": params.get("smtp_host", "smtp.gmail.com"),
                "smtp_port": int(params.get("smtp_port", 587)),
                "imap_host": params.get("imap_host", "imap.gmail.com"),
                "imap_port": int(params.get("imap_port", 993)),
                "use_ssl": params.get("use_ssl", False),
                "use_tls": params.get("use_tls", True),
                "imap_use_ssl": params.get("imap_use_ssl", True)
            }
        
        # Test connections separately to provide more detailed feedback
        smtp_error = None
        imap_error = None
        
        # Test SMTP connection
        try:
            # For SMTP testing
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
        
        # Test IMAP connection and attempt to fetch emails
        try:
            # For IMAP testing
            if settings.get("imap_use_ssl", True):
                imap_client = imaplib.IMAP4_SSL(settings["imap_host"], settings["imap_port"], timeout=30)
            else:
                imap_client = imaplib.IMAP4(settings["imap_host"], settings["imap_port"], timeout=30)
                if settings.get("imap_use_tls", False):
                    imap_client.starttls()
            
            imap_client.login(username, password)
            
            # Try to actually fetch emails as an additional validation step
            try:
                # Select the INBOX folder
                result, data = imap_client.select('INBOX', readonly=True)
                if result != 'OK':
                    raise Exception(f"Failed to select INBOX: {data[0].decode() if data else 'Unknown error'}")
                
                # Try to fetch the most recent 1 message (just to verify we can access emails)
                result, data = imap_client.search(None, 'ALL')
                if result != 'OK':
                    raise Exception(f"Failed to search messages: {data[0].decode() if data else 'Unknown error'}")
                
                # Get count of messages
                message_count = len(data[0].split())
                
                # Close the mailbox and logout
                imap_client.close()
                imap_client.logout()
                
                # Include the message count in the success response
                return {
                    "valid": True,
                    "message": f"SMTP and IMAP connections successful. Found {message_count} messages in inbox.",
                    "settings_used": settings,
                    "message_count": message_count
                }
                
            except Exception as fetch_error:
                # If we can connect but can't fetch emails, report this issue
                imap_client.logout()
                return {
                    "valid": False,
                    "message": f"Connected to mail server but couldn't fetch emails: {str(fetch_error)}",
                    "settings_used": settings
                }
                
        except Exception as e:
            imap_error = str(e)
        
        # Check for errors and return appropriate response
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
        
        # Shouldn't reach here since we return earlier after successful email fetch
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
    
    # Common domain to service mappings
    domain_mappings = {
        "gmail.com": "gmail",
        "googlemail.com": "gmail",
        "outlook.com": "outlook",
        "hotmail.com": "outlook",
        "live.com": "outlook",
        "msn.com": "outlook",
        "yahoo.com": "yahoo",
        "ymail.com": "yahoo",
        "zoho.com": "zoho",
        "aol.com": "aol",
        "aim.com": "aol",
        "protonmail.com": "protonmail",
        "protonmail.ch": "protonmail",
        "pm.me": "protonmail",
        "gmx.com": "gmx",
        "gmx.net": "gmx",
        "gmx.de": "gmx",
        "icloud.com": {
            "smtp_host": "smtp.mail.me.com",
            "smtp_port": 587,
            "imap_host": "imap.mail.me.com",
            "imap_port": 993,
            "use_ssl": False,
            "use_tls": True,
            "imap_use_ssl": True,
            "notes": "For iCloud accounts with 2FA, you need to generate an app-specific password."
        },
        "mail.ru": {
            "smtp_host": "smtp.mail.ru",
            "smtp_port": 465,
            "imap_host": "imap.mail.ru",
            "imap_port": 993,
            "use_ssl": True,
            "use_tls": False,
            "imap_use_ssl": True,
            "notes": "Use your full email address as the username."
        }
    }
    
    # Get the default settings
    default_settings_response = await get_default_settings({"service": ""})
    all_settings = default_settings_response.get("settings", {})
    
    if domain in domain_mappings:
        service_or_settings = domain_mappings[domain]
        
        # Check if direct settings or reference to another service
        if isinstance(service_or_settings, str) and service_or_settings in all_settings:
            return {
                "email": email,
                "detected_service": service_or_settings,
                "settings": all_settings[service_or_settings],
                "success": True
            }
        elif isinstance(service_or_settings, dict):
            return {
                "email": email,
                "detected_service": "custom",
                "settings": service_or_settings,
                "success": True
            }
    
    # Try to guess based on common email providers
    if domain.endswith(".edu"):
        return {
            "email": email,
            "detected_service": "unknown_educational",
            "possible_settings": [
                {
                    "smtp_host": f"smtp.{domain}",
                    "smtp_port": 587,
                    "imap_host": f"imap.{domain}",
                    "imap_port": 993,
                    "use_ssl": False,
                    "use_tls": True,
                    "imap_use_ssl": True,
                    "notes": "These are guessed settings. You might need to contact your institution's IT department."
                }
            ],
            "success": True
        }
    elif any(domain.endswith(f".{tld}") for tld in ["com", "org", "net", "io"]):
        # Best guess for corporate emails
        return {
            "email": email,
            "detected_service": "unknown_corporate",
            "possible_settings": [
                {
                    "smtp_host": f"smtp.{domain}",
                    "smtp_port": 587,
                    "imap_host": f"imap.{domain}",
                    "imap_port": 993,
                    "use_ssl": False,
                    "use_tls": True,
                    "imap_use_ssl": True,
                    "notes": "These are guessed settings. Check with your email provider for accurate information."
                },
                {
                    "smtp_host": f"mail.{domain}",
                    "smtp_port": 587,
                    "imap_host": f"mail.{domain}",
                    "imap_port": 993,
                    "use_ssl": False,
                    "use_tls": True,
                    "imap_use_ssl": True,
                    "notes": "Alternative settings to try if the first option doesn't work."
                }
            ],
            "success": True
        }
    
    return {
        "email": email,
        "detected_service": "unknown",
        "available_services": list(all_settings.keys()),
        "success": False,
        "message": "Could not detect settings automatically. Please select a service from the list or enter settings manually."
    }

apply_error_handler_to_router(router) 