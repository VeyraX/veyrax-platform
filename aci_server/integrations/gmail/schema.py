from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
from datetime import datetime

class MessageBase(BaseModel):
    id: str  # Это основной идентификатор сообщения
    thread_id: str
    subject: Optional[str]
    snippet: str
    body: str
    recipient: Optional[str]
    sender: Optional[str]
    date: datetime
    html_link: str

class Message(MessageBase):
    # Убираем дублирование полей из MessageBase
    # id и thread_id уже определены в родительском классе
    message_id: Optional[str] = None  # Опциональное поле для совместимости
    subject: Optional[str] = None
    snippet: Optional[str] = None
    body: Optional[str] = None
    sender: Optional[str] = None
    recipient: Optional[str] = None
    date: Optional[datetime] = None
    html_link: Optional[str] = None
    labels: Optional[List[str]] = None
    draft_id: Optional[str] = None  # ID черновика, если сообщение является черновиком

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

class ApiResponse(BaseModel):
    data: Union[Message, MessageList, DraftList, DraftResponse]
    component: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None
