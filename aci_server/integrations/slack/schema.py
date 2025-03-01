from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union

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
    is_bot: Optional[bool] = False

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

# New parameter classes for routes
class ListChannelsParams(BaseModel):
    cursor: Optional[str] = None

class ListChannelMembersParams(BaseModel):
    channel_id: str
    cursor: Optional[str] = None

class ListDirectMessagesParams(BaseModel):
    cursor: Optional[str] = None

class PostMessageParams(BaseModel):
    channel_id: str
    message: ThreadMessage

class SendDmParams(BaseModel):
    message: DirectMessage

class ReplyInThreadParams(BaseModel):
    channel_id: str
    thread_ts: str
    message: ThreadMessage

class ListThreadMessagesParams(BaseModel):
    channel_id: str
    thread_ts: str
    cursor: Optional[str] = None

class ListChannelMessagesParams(BaseModel):
    channel_id: str
    cursor: Optional[str] = None

class ListDirectMessagesWithUserParams(BaseModel):
    user_id: str
    cursor: Optional[str] = None

# API Response class
class ApiResponse(BaseModel):
    data: Union[Channel, ChannelList, ChannelMember, ChannelMemberList, Message, MessageList]
    component: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None

# Response schema classes
class ListChannelsResponse(BaseModel):
    data: ChannelList
    message: Optional[str] = None

class ListChannelMembersResponse(BaseModel):
    data: ChannelMemberList
    message: Optional[str] = None

class ListDirectMessagesResponse(BaseModel):
    data: MessageList
    message: Optional[str] = None

class PostMessageResponse(BaseModel):
    data: Message
    message: Optional[str] = None

class SendDmResponse(BaseModel):
    data: Message
    message: Optional[str] = None

class ReplyInThreadResponse(BaseModel):
    data: Message
    message: Optional[str] = None

class ListThreadMessagesResponse(BaseModel):
    data: MessageList
    message: Optional[str] = None

class ListChannelMessagesResponse(BaseModel):
    data: MessageList
    message: Optional[str] = None

class ListDirectMessagesWithUserResponse(BaseModel):
    data: MessageList
    message: Optional[str] = None