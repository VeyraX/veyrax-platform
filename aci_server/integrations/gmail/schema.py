from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class MessageBase(BaseModel):
    id: str
    thread_id: str
    subject: Optional[str]
    snippet: str
    body: str
    recipient: str
    sender: str
    date: datetime

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
