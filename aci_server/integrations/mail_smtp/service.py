from typing import Dict, Any, List, Optional, Union
import os
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
    
    def prepare_error_response(self, error: MailSMTPError) -> ApiResponse:
        error_response = ErrorResponse(
            success=False,
            error=error.message,
            error_details=error.errors if hasattr(error, "errors") else None
        )
        return self.prepare_response(error_response, "MailSMTPErrorResult")
    
    def get_messages(self, params: GetMessagesParams) -> ApiResponse:
        try:
            processed_params = params.model_dump(exclude_none=True)
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
            processed_params = params.model_dump(exclude_none=True)
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
            processed_params = params.model_dump(exclude_none=True)
            response = self.client.send_message(processed_params)
            
            validated_response = SendMessageResponse(**response)
            return self.prepare_response(validated_response, "MailSMTPSendResult")
        except MailSMTPError as e:
            return self.prepare_error_response(e)
        except Exception as e:
            error = MailSMTPError(str(e))
            return self.prepare_error_response(error)
    
    def get_folders(self, params: GetFoldersParams) -> ApiResponse:
        try:
            processed_params = params.model_dump(exclude_none=True)
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
            processed_params = params.model_dump(exclude_none=True)
            response = self.client.create_folder(**processed_params)
            
            validated_response = GenericResponse(**response)
            return self.prepare_response(validated_response, "MailSMTPGenericResult")
        except MailSMTPError as e:
            return self.prepare_error_response(e)
        except Exception as e:
            error = MailSMTPError(str(e))
            return self.prepare_error_response(error)
    
    def delete_message(self, params: DeleteMessageParams) -> ApiResponse:
        try:
            processed_params = params.model_dump(exclude_none=True)
            response = self.client.delete_message(**processed_params)
            
            validated_response = GenericResponse(**response)
            return self.prepare_response(validated_response, "MailSMTPGenericResult")
        except MailSMTPError as e:
            return self.prepare_error_response(e)
        except Exception as e:
            error = MailSMTPError(str(e))
            return self.prepare_error_response(error)
    
    def move_message(self, params: MoveMessageParams) -> ApiResponse:
        try:
            processed_params = params.model_dump(exclude_none=True)
            response = self.client.move_message(**processed_params)
            
            validated_response = GenericResponse(**response)
            return self.prepare_response(validated_response, "MailSMTPGenericResult")
        except MailSMTPError as e:
            return self.prepare_error_response(e)
        except Exception as e:
            error = MailSMTPError(str(e))
            return self.prepare_error_response(error) 