from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime

class AuthenticateRequest(BaseModel):
    include_qr_base64: Optional[bool] = Field(True, description="Whether to include the QR image in the response")
    include_qr_ascii: Optional[bool] = Field(True, description="Whether to include the QR image in the response")
    include_component: Optional[bool] = Field(True, description="Whether to include the component in the response")

class CheckStatusRequest(BaseModel):
    pass

class SendMessageRequest(BaseModel):
    recipient: str = Field(description="The recipient - phone number or JID (e.g., '123456789@s.whatsapp.net')")
    message: str = Field(description="The message text to send")

class GetChatsRequest(BaseModel):
    query: Optional[str] = Field(None, description="Optional search query for chats")
    limit: Optional[int] = Field(20, description="Maximum number of chats to return")
    page: Optional[int] = Field(0, description="Page number for pagination")
    include_last_message: Optional[bool] = Field(True, description="Whether to include the last message in each chat")
    sort_by: Optional[str] = Field("last_active", description="Sort by field (last_active or name)")

class GetMessagesRequest(BaseModel):
    chat_jid: Optional[str] = Field(None, description="Filter by chat JID")
    query: Optional[str] = Field(None, description="Search query for message content")
    limit: Optional[int] = Field(20, description="Maximum number of messages to return")
    page: Optional[int] = Field(0, description="Page number for pagination")
    include_context: Optional[bool] = Field(True, description="Whether to include context around messages")
    sender_phone_number: Optional[str] = Field(None, description="Filter by sender phone number")
    start_date: Optional[str] = Field(None, description="Start date for filtering (ISO format)")
    end_date: Optional[str] = Field(None, description="End date for filtering (ISO format)")

class SearchContactsRequest(BaseModel):
    query: str = Field(description="Search query for contact name or phone number")

class GetChatRequest(BaseModel):
    chat_jid: str = Field(description="The JID of the chat to get")
    include_last_message: Optional[bool] = Field(True, description="Whether to include the last message")

class ValidateKeyRequest(BaseModel):
    pass

class GetRecentMessagesRequest(BaseModel):
    limit: Optional[int] = Field(10, description="Maximum number of recent messages to return")

class CheckStatusRequest(BaseModel):
    pass

# Response models
class MessageModel(BaseModel):
    id: str
    timestamp: str
    sender: str
    content: str
    is_from_me: bool
    chat_jid: str
    chat_name: Optional[str] = None

class ChatModel(BaseModel):
    jid: str
    name: Optional[str]
    last_message_time: Optional[str] = None
    last_message: Optional[str] = None
    last_sender: Optional[str] = None
    last_is_from_me: Optional[bool] = None
    is_group: bool

class ContactModel(BaseModel):
    phone_number: str
    name: Optional[str]
    jid: str

class SessionModel(BaseModel):
    user_id: str
    is_logged_in: bool
    qr_data: Optional[str] = None
    qr_image_base64: Optional[str] = None
    qr_image_ascii: Optional[str] = None
    phone: Optional[str] = None
    error: Optional[str] = None

class MessageListResponse(BaseModel):
    items: List[MessageModel]

class ChatListResponse(BaseModel):
    items: List[ChatModel]

class ContactListResponse(BaseModel):
    items: List[ContactModel]

class SessionListResponse(BaseModel):
    items: List[SessionModel]

class SendMessageResponse(BaseModel):
    success: bool
    message: str

# Generic API response
class ApiResponse(BaseModel):
    data: Any
    component: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None

# Specific response schemas for endpoints
class AuthenticateResponse(BaseModel):
    data: SessionModel
    message: Optional[str] = None

class SendMessageResponseSchema(BaseModel):
    data: SendMessageResponse
    message: Optional[str] = None

class GetChatsResponse(BaseModel):
    data: ChatListResponse
    message: Optional[str] = None

class GetMessagesResponse(BaseModel):
    data: MessageListResponse
    message: Optional[str] = None

class SearchContactsResponse(BaseModel):
    data: ContactListResponse
    message: Optional[str] = None

class GetChatResponse(BaseModel):
    data: ChatModel
    message: Optional[str] = None

class GetRecentMessagesResponse(BaseModel):
    data: MessageListResponse
    message: Optional[str] = None

class CheckStatusResponse(BaseModel):
    data: SessionModel
    message: Optional[str] = None

class ListUsersResponse(BaseModel):
    data: SessionListResponse
    message: Optional[str] = None

class DisconnectRequest(BaseModel):
    pass    

class DisconnectResponse(BaseModel):
    success: bool
    message: str 