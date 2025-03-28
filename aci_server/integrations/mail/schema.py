from pydantic import BaseModel, Field, EmailStr
from typing import List, Dict, Any, Optional, Union, Literal

class CommonParams(BaseModel):
    host: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    use_ssl: Optional[bool] = True
    use_tls: Optional[bool] = False


class EmailAddress(BaseModel):
    email: str
    name: Optional[str] = None


class EmailAttachment(BaseModel):
    filename: str
    content: str
    content_type: Optional[str] = None


class GetMessagesParams(BaseModel):
    folder: Optional[str] = Field("INBOX", description="Folder to fetch messages from")
    limit: Optional[int] = Field(20, description="Maximum number of messages to fetch", ge=1, le=100)
    offset: Optional[int] = Field(0, description="Number of messages to skip", ge=0)
    search_query: Optional[str] = Field(None, description="Search query for message content or sender")
    mark_as_read: Optional[bool] = Field(False, description="Mark fetched messages as read")


class GetMessageParams(BaseModel):
    message_id: str = Field(..., description="Unique ID of the message to fetch")
    mark_as_read: Optional[bool] = Field(False, description="Mark the message as read")


class SendMessageParams(BaseModel):
    from_email: EmailAddress = Field(..., description="Sender email address")
    to: List[EmailAddress] = Field(..., description="Recipient email addresses")
    cc: Optional[List[EmailAddress]] = Field(None, description="CC recipient email addresses")
    bcc: Optional[List[EmailAddress]] = Field(None, description="BCC recipient email addresses")
    subject: str = Field(..., description="Email subject")
    body_text: Optional[str] = Field(None, description="Plain text email body")
    body_html: Optional[str] = Field(None, description="HTML email body")
    attachments: Optional[List[EmailAttachment]] = Field(None, description="Email attachments")
    reply_to: Optional[List[EmailAddress]] = Field(None, description="Reply-to email addresses")
    priority: Optional[str] = Field(None, description="Email priority (high, normal, low)")


class CreateFolderParams(BaseModel):
    folder_name: str = Field(..., description="Name of the folder to create")


class DeleteMessageParams(BaseModel):
    message_id: str = Field(..., description="Unique ID of the message to delete")
    folder: Optional[str] = Field("INBOX", description="Folder containing the message")
    permanently: Optional[bool] = Field(False, description="Permanently delete the message")


class GetFoldersParams(BaseModel):
    include_counts: Optional[bool] = Field(False, description="Include message counts for each folder")


class MoveMessageParams(BaseModel):
    message_id: str = Field(..., description="Unique ID of the message to move")
    source_folder: Optional[str] = Field("INBOX", description="Folder containing the message")
    destination_folder: str = Field(..., description="Folder to move the message to")


# Response models
class EmailHeader(BaseModel):
    name: str
    value: str


class EmailBody(BaseModel):
    text: Optional[str] = None
    html: Optional[str] = None


class EmailMessage(BaseModel):
    id: str
    subject: Optional[str] = None
    from_email: Optional[EmailAddress] = None
    to: List[EmailAddress] = []
    cc: List[EmailAddress] = []
    bcc: List[EmailAddress] = []
    reply_to: Optional[List[EmailAddress]] = None
    date: Optional[str] = None
    body: EmailBody
    attachments: List[EmailAttachment] = []
    headers: List[EmailHeader] = []
    folder: Optional[str] = None
    is_read: Optional[bool] = None
    size: Optional[int] = None


class EmailFolder(BaseModel):
    name: str
    full_name: str
    delimiter: Optional[str] = None
    attributes: Optional[List[str]] = None
    has_children: Optional[bool] = None
    message_count: Optional[int] = None
    unread_count: Optional[int] = None


class EmailMessageList(BaseModel):
    messages: List[EmailMessage]
    total: int
    offset: int
    limit: int


class FolderList(BaseModel):
    folders: List[EmailFolder]


class SendMessageResponse(BaseModel):
    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None


class GenericResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    error: Optional[str] = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    error_details: Optional[Dict[str, Any]] = None


# Union response type for ApiResponse
class ApiResponse(BaseModel):
    data: Union[EmailMessage, EmailMessageList, FolderList, SendMessageResponse, GenericResponse, ErrorResponse]
    component: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None 