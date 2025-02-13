from pydantic import BaseModel
from typing import List, Optional

class Channel(BaseModel):
    id: str
    name: str
    is_private: bool
    topic: Optional[str]
    purpose: Optional[str]

class ChannelList(BaseModel):
    channels: List[Channel]
    cursor: Optional[str]

class ChannelMember(BaseModel):
    id: str
    name: str
    real_name: Optional[str]

class ChannelMemberList(BaseModel):
    members: List[ChannelMember]
    cursor: Optional[str]

class Message(BaseModel):
    id: str
    text: str
    user: str
    user_name: Optional[str]
    real_name: Optional[str]
    timestamp: str
    thread_ts: Optional[str]

class MessageList(BaseModel):
    messages: List[Message]
    cursor: Optional[str]

class DirectMessage(BaseModel):
    user_id: str
    text: str

class ThreadMessage(BaseModel):
    text: str