from typing import Dict, Any, Union, List, Optional, Tuple
from .client import WhatsAppClient
from .schema import (
    MessageModel, ChatModel, ContactModel, SessionModel,
    MessageListResponse, ChatListResponse, ContactListResponse, SessionListResponse,
    SendMessageResponse, ApiResponse, AuthenticateResponse, SendMessageResponseSchema,
    GetChatsResponse, GetMessagesResponse, SearchContactsResponse, GetChatResponse,
    GetRecentMessagesResponse, CheckStatusResponse, ListUsersResponse
)
import os
from ..common.component_handler import load_components, prepare_components_auto
from datetime import datetime

class WhatsAppService:
    def __init__(self, client: WhatsAppClient):
        self.client = client
        self.components_data = self._load_components()
        
    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
        
    def prepare_response(self, data: Any, component_name: str = None) -> ApiResponse:
        tool_name = "whatsapp"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)
    
    def _convert_datetime_to_str(self, dt):
        if dt:
            return dt.isoformat()
        return None
        
    def _convert_message(self, message) -> MessageModel:
        return MessageModel(
            id=message.id,
            timestamp=self._convert_datetime_to_str(message.timestamp),
            sender=message.sender,
            content=message.content,
            is_from_me=message.is_from_me,
            chat_jid=message.chat_jid,
            chat_name=message.chat_name
        )
        
    def _convert_chat(self, chat) -> ChatModel:
        return ChatModel(
            jid=chat.jid,
            name=chat.name,
            last_message_time=self._convert_datetime_to_str(chat.last_message_time),
            last_message=chat.last_message,
            last_sender=chat.last_sender,
            last_is_from_me=chat.last_is_from_me,
            is_group=chat.is_group
        )
        
    def _convert_contact(self, contact) -> ContactModel:
        return ContactModel(
            phone_number=contact.phone_number,
            name=contact.name,
            jid=contact.jid
        )
        
    def _convert_session(self, session) -> SessionModel:
        return SessionModel(
            user_id=session.user_id,
            is_logged_in=session.is_logged_in,
            qr_data=session.qr_data,
            qr_image_base64=session.qr_image_base64,
            phone=session.phone,
            error=session.error
        )
        
    def authenticate(self) -> AuthenticateResponse:
        session = self.client.authenticate()
        session_model = self._convert_session(session)
        return self.prepare_response(session_model, "WhatsAppQRCodeView")
        
    def check_status(self) -> CheckStatusResponse:
        session = self.client.check_status()
        session_model = self._convert_session(session)
        return self.prepare_response(session_model, "WhatsAppStatusView")
        
    def send_message(self, recipient: str, message: str) -> SendMessageResponseSchema:
        success, message_str = self.client.send_message(recipient, message)
        response = SendMessageResponse(success=success, message=message_str)
        return self.prepare_response(response)
        
    def list_users(self) -> ListUsersResponse:
        users = self.client.list_users()
        user_models = [self._convert_session(user) for user in users]
        response = SessionListResponse(items=user_models)
        return self.prepare_response(response, "WhatsAppUsersView")
        
    def get_chats(self, query: Optional[str] = None, limit: int = 20, 
                  page: int = 0, include_last_message: bool = True, 
                  sort_by: str = "last_active") -> GetChatsResponse:
        chats = self.client.get_chats(
            query=query,
            limit=limit,
            page=page,
            include_last_message=include_last_message,
            sort_by=sort_by
        )
        print('[WhatsAppService] get_chats', chats)
        chat_models = [self._convert_chat(chat) for chat in chats]
        response = ChatListResponse(items=chat_models)
        return self.prepare_response(response, "WhatsAppChatsView")
        
    def get_messages(self, chat_jid: Optional[str] = None, 
                    query: Optional[str] = None, limit: int = 20, 
                    page: int = 0, include_context: bool = True,
                    sender_phone_number: Optional[str] = None,
                    start_date: Optional[str] = None,
                    end_date: Optional[str] = None) -> GetMessagesResponse:
        
        date_range = None
        if start_date and end_date:
            start_dt = datetime.fromisoformat(start_date)
            end_dt = datetime.fromisoformat(end_date)
            date_range = (start_dt, end_dt)
            
        messages = self.client.get_messages(
            chat_jid=chat_jid,
            query=query,
            limit=limit,
            page=page,
            include_context=include_context,
            sender_phone_number=sender_phone_number,
            date_range=date_range
        )
        message_models = [self._convert_message(message) for message in messages]
        response = MessageListResponse(items=message_models)
        return self.prepare_response(response, "WhatsAppMessagesView")
        
    def search_contacts(self, query: str) -> SearchContactsResponse:
        contacts = self.client.get_contacts(query)
        contact_models = [self._convert_contact(contact) for contact in contacts]
        response = ContactListResponse(items=contact_models)
        return self.prepare_response(response, "WhatsAppContactsView")
        
    def get_chat(self, chat_jid: str, include_last_message: bool = True) -> GetChatResponse:
        chat = self.client.get_chat(chat_jid, include_last_message)
        if not chat:
            return self.prepare_response(None)
        chat_model = self._convert_chat(chat)
        return self.prepare_response(chat_model, "WhatsAppChatView")
        
    def get_recent_messages(self, limit: int = 10) -> GetRecentMessagesResponse:
        messages = self.client.get_recent_messages(limit)
        message_models = [self._convert_message(message) for message in messages]
        response = MessageListResponse(items=message_models)
        return self.prepare_response(response, "WhatsAppMessagesView") 