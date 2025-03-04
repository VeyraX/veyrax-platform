from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
from datetime import datetime

class MessageBase(BaseModel):
    id: str
    thread_id: str
    subject: Optional[str]
    snippet: str
    body: str
    recipient: Optional[str]
    sender: Optional[str]
    date: datetime
    html_link: str

class Message(MessageBase):
    subject: Optional[str] = None
    snippet: Optional[str] = None
    body: Optional[str] = None
    sender: Optional[str] = None
    recipient: Optional[str] = None
    date: Optional[datetime] = None
    html_link: Optional[str] = None
    labels: Optional[List[str]] = None
    draft_id: Optional[str] = None 

class DraftBase(BaseModel):
    draft_id: str
    message_id: str
    subject: Optional[str]
    snippet: str

class DraftMessage(BaseModel):
    recipient: str
    subject: str
    body: str
    
class DraftResponse(BaseModel):
    draft_id: str
    message_id: str

class MessageList(BaseModel):
    messages: List[MessageBase]
    pageToken: Optional[str]

class DraftList(BaseModel):
    drafts: List[DraftBase]
    pageToken: Optional[str]

class MessageFilters(BaseModel):
    body_keywords: Optional[str] = None
    recipient: Optional[str] = None
    subject_keywords: Optional[str] = None
    after_date: Optional[str] = None  
    before_date: Optional[str] = None
    max_results: Optional[int] = 20
    from_email: Optional[str] = None
    has_attachments: Optional[bool] = None


class ApiResponse(BaseModel):
    data: Union[Message, MessageList, DraftList, DraftResponse]
    component: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None

class GetMessagesParams(BaseModel):
    pageToken: Optional[str] = None
    filters: Optional[MessageFilters] = None

# New schema classes for other routes
class GetMessageParams(BaseModel):
    message_id: str

class DeleteMessageParams(BaseModel):
    message_id: str
    
class SendMessageParams(BaseModel):
    message_id: str
    
class GetDraftsParams(BaseModel):
    pageToken: Optional[str] = None
    
class CreateDraftParams(BaseModel):
    draft_args: DraftMessage
    
class DeleteDraftParams(BaseModel):
    draft_id: str
    
class ModifyDraftParams(BaseModel):
    draft_id: str
    update_args: Optional[DraftMessage] = None

# Response schema classes
class GetMessagesResponse(BaseModel):
    data: MessageList
    message: Optional[str] = None

class GetMessageResponse(BaseModel):
    data: Message
    message: Optional[str] = None

class DeleteMessageResponse(BaseModel):
    status: str
    message: Optional[str] = None

class SendMessageResponse(BaseModel):
    data: Message
    message: Optional[str] = None

class GetDraftsResponse(BaseModel):
    data: MessageList
    message: Optional[str] = None

class CreateDraftResponse(BaseModel):
    data: Message
    message: Optional[str] = None

class DeleteDraftResponse(BaseModel):
    status: str
    message: Optional[str] = None

class ModifyDraftResponse(BaseModel):
    data: Message
    message: Optional[str] = None
