from pydantic import BaseModel
from typing import List, Optional

class MessageBase(BaseModel):
    id: str
    thread_id: str
    subject: Optional[str]
    snippet: str

class Message(MessageBase):
    body: str
    sender: str
    recipient: str
    labels: List[str]

class DraftBase(BaseModel):
    draft_id: str
    message_id: str
    subject: Optional[str]
    snippet: str

class DraftMessage(BaseModel):
    to: str
    subject: str
    body: str
    
class DraftResponse(BaseModel):
    draft_id: str
    message_id: str

class MessageList(BaseModel):
    messages: List[MessageBase]
    next_page_token: Optional[str]

class DraftList(BaseModel):
    drafts: List[DraftBase]
    next_page_token: Optional[str]

class DraftUpdate(BaseModel):
    recipient: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None

class MessageFilters(BaseModel):
    body_keywords: Optional[str] = None
    recipient: Optional[str] = None
    subject_keywords: Optional[str] = None
    after_date: Optional[str] = None  
    before_date: Optional[str] = None 
