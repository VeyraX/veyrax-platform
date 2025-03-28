from typing import Dict, Any, List, Optional, Union
import os
import logging
from .client import MailSMTPClient, MailSMTPError
from .schema import (
    GetMessagesParams,
    GetMessageParams,
    SendMessageParams,
    CreateFolderParams,
    DeleteMessageParams,
    GetFoldersParams,
    MoveMessageParams,
    EmailMessage,
    EmailMessageList,
    FolderList,
    SendMessageResponse,
    GenericResponse,
    ErrorResponse,
    ApiResponse
)
from ..common.component_handler import load_components, prepare_components_auto

# Configure logging
logger = logging.getLogger(__name__)

class MailSMTPService:
    def __init__(self, client: MailSMTPClient):
        self.client = client
        self.components_data = self._load_components()
    
    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
    
    def prepare_response(self, data: Any, component_name: str = None) -> ApiResponse:
        tool_name = "mail_smtp"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)
    
    def prepare_error_response(self, error: Union[MailSMTPError, Exception]) -> ApiResponse:
        if isinstance(error, MailSMTPError):
            error_msg = error.message
            error_details = error.errors if hasattr(error, "errors") else None
        else:
            error_msg = str(error)
            error_details = None
        
        logger.error(f"Mail SMTP Error: {error_msg}")
        if error_details:
            logger.error(f"Error details: {error_details}")
        
        error_response = ErrorResponse(
            success=False,
            error=error_msg,
            error_details=error_details
        )
        return self.prepare_response(error_response, "MailSMTPErrorResult")
    
    def test_connection(self) -> ApiResponse:
        """Test SMTP and IMAP connections and report status."""
        try:
            # Test SMTP connection
            smtp_conn = self.client._get_smtp_connection()
            smtp_conn.quit()
            
            # Test IMAP connection
            imap_conn = self.client._get_imap_connection()
            imap_conn.logout()
            
            response = GenericResponse(
                success=True,
                message="Successfully connected to SMTP and IMAP servers"
            )
            return self.prepare_response(response, "MailSMTPGenericResult")
        except MailSMTPError as e:
            return self.prepare_error_response(e)
        except Exception as e:
            return self.prepare_error_response(e)
    
    def get_messages(self, params: GetMessagesParams) -> ApiResponse:
        try:
            # Filter out authentication parameters
            processed_params = {
                k: v for k, v in params.model_dump(exclude_none=True).items()
                if k not in ['host', 'port', 'username', 'password', 'use_ssl', 'use_tls']
            }
            response = self.client.get_messages(**processed_params)
            
            validated_response = EmailMessageList(
                messages=[EmailMessage(**msg) for msg in response["messages"]],
                total=response["total"],
                offset=response["offset"],
                limit=response["limit"]
            )
            
            return self.prepare_response(validated_response, "MailSMTPMessageList")
        except MailSMTPError as e:
            return self.prepare_error_response(e)
        except Exception as e:
            error = MailSMTPError(str(e))
            return self.prepare_error_response(error)
    
    def get_message(self, params: GetMessageParams) -> ApiResponse:
        try:
            # Filter out authentication parameters
            processed_params = {
                k: v for k, v in params.model_dump(exclude_none=True).items()
                if k not in ['host', 'port', 'username', 'password', 'use_ssl', 'use_tls']
            }
            response = self.client.get_message(**processed_params)
            
            validated_response = EmailMessage(**response)
            return self.prepare_response(validated_response, "MailSMTPMessageDetail")
        except MailSMTPError as e:
            return self.prepare_error_response(e)
        except Exception as e:
            error = MailSMTPError(str(e))
            return self.prepare_error_response(error)
    
    def send_message(self, params: SendMessageParams) -> ApiResponse:
        try:
            # Filter out authentication parameters and prepare message data
            message_data = {
                k: v for k, v in params.model_dump(exclude_none=True).items()
                if k not in ['host', 'port', 'username', 'password', 'use_ssl', 'use_tls']
            }
            response = self.client.send_message(message_data)
            
            validated_response = SendMessageResponse(**response)
            return self.prepare_response(validated_response, "MailSMTPSendResult")
        except MailSMTPError as e:
            return self.prepare_error_response(e)
        except Exception as e:
            error = MailSMTPError(str(e))
            return self.prepare_error_response(error)
    
    def get_folders(self, params: GetFoldersParams) -> ApiResponse:
        try:
            # Filter out authentication parameters
            processed_params = {
                k: v for k, v in params.model_dump(exclude_none=True).items()
                if k not in ['host', 'port', 'username', 'password', 'use_ssl', 'use_tls']
            }
            response = self.client.get_folders(**processed_params)
            
            validated_response = FolderList(
                folders=[EmailFolder(**folder) for folder in response["folders"]]
            )
            
            return self.prepare_response(validated_response, "MailSMTPFolderList")
        except MailSMTPError as e:
            return self.prepare_error_response(e)
        except Exception as e:
            error = MailSMTPError(str(e))
            return self.prepare_error_response(error)
    
    def create_folder(self, params: CreateFolderParams) -> ApiResponse:
        try:
            # Extract just the folder_name
            folder_name = params.folder_name
            response = self.client.create_folder(folder_name)
            
            validated_response = GenericResponse(**response)
            return self.prepare_response(validated_response, "MailSMTPGenericResult")
        except MailSMTPError as e:
            return self.prepare_error_response(e)
        except Exception as e:
            error = MailSMTPError(str(e))
            return self.prepare_error_response(error)
    
    def delete_message(self, params: DeleteMessageParams) -> ApiResponse:
        try:
            # Extract parameters
            message_id = params.message_id
            folder = params.folder if hasattr(params, 'folder') else 'INBOX'
            
            response = self.client.delete_message(message_id, folder)
            
            validated_response = GenericResponse(**response)
            return self.prepare_response(validated_response, "MailSMTPGenericResult")
        except MailSMTPError as e:
            return self.prepare_error_response(e)
        except Exception as e:
            error = MailSMTPError(str(e))
            return self.prepare_error_response(error)
    
    def move_message(self, params: MoveMessageParams) -> ApiResponse:
        try:
            # Extract the required parameters
            message_id = params.message_id
            source_folder = params.source_folder if hasattr(params, 'source_folder') else 'INBOX'
            target_folder = params.destination_folder
            
            response = self.client.move_message(message_id, source_folder, target_folder)
            
            validated_response = GenericResponse(**response)
            return self.prepare_response(validated_response, "MailSMTPGenericResult")
        except MailSMTPError as e:
            return self.prepare_error_response(e)
        except Exception as e:
            error = MailSMTPError(str(e))
            return self.prepare_error_response(error) 