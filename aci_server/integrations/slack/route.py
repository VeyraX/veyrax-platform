from fastapi import APIRouter, Depends, HTTPException, Body
from typing import Optional, Dict, Any
from .schema import (
    ChannelList, ChannelMemberList, MessageList, 
    Message, DirectMessage, ThreadMessage,
    ListChannelsParams, ListChannelMembersParams, ListDirectMessagesParams,
    PostMessageParams, SendDmParams, ReplyInThreadParams, ListThreadMessagesParams,
    ListChannelMessagesParams, ListDirectMessagesWithUserParams
)
from .service import SlackService
from .client import SlackClient
from ..common.input_schema_decorator import input_schema
import os
import pickle

router = APIRouter(prefix="/slack", tags=["slack"])

async def get_slack_service():
    if os.path.exists('credentials/slack_user_token.pickle'):
        with open('credentials/slack_user_token.pickle', 'rb') as token_file:
            creds = pickle.load(token_file)
            token_str = creds.get('access_token')
            if not token_str:
                raise HTTPException(status_code=401, detail="Access token not found in credentials")
    else:
        raise HTTPException(status_code=404, detail="Credentials file not found")
    
    client = SlackClient(token_str)
    return SlackService(client)

@router.get("/channels", response_model=ChannelList)
@input_schema(schema_class=ListChannelsParams)
async def list_channels(
    cursor: Optional[str] = None,
    service: SlackService = Depends(get_slack_service)
):
    return service.list_channels(cursor)

@router.get("/channels/{channel_id}/members", response_model=ChannelMemberList)
@input_schema(schema_class=ListChannelMembersParams)
async def list_channel_members(
    channel_id: str,
    cursor: Optional[str] = None,
    service: SlackService = Depends(get_slack_service)
):
    return service.list_channel_members(channel_id, cursor)

@router.get("/direct-messages", response_model=MessageList)
@input_schema(schema_class=ListDirectMessagesParams)
async def list_direct_messages(
    cursor: Optional[str] = None,
    service: SlackService = Depends(get_slack_service)
):
    return service.list_direct_messages(cursor)

@router.post("/channels/{channel_id}/messages", response_model=Message)
@input_schema(schema_class=PostMessageParams)
async def post_message(
    channel_id: str,
    message: ThreadMessage,
    service: SlackService = Depends(get_slack_service)
):
    return service.post_message(channel_id, message.text)

@router.post("/dm", response_model=Message)
@input_schema(schema_class=SendDmParams)
async def send_dm(
    message: DirectMessage,
    service: SlackService = Depends(get_slack_service)
) -> Message:
    return service.send_dm(message.user_id, message.text)

@router.post("/channels/{channel_id}/threads/{thread_ts}/replies", response_model=Message)
@input_schema(schema_class=ReplyInThreadParams)
async def reply_in_thread(
    channel_id: str,
    thread_ts: str,
    message: ThreadMessage,
    service: SlackService = Depends(get_slack_service)
):
    return service.reply_in_thread(channel_id, thread_ts, message.text)

@router.get("/channels/{channel_id}/threads/{thread_ts}/messages", response_model=MessageList)
@input_schema(schema_class=ListThreadMessagesParams)
async def list_thread_messages(
    channel_id: str,
    thread_ts: str,
    cursor: Optional[str] = None,
    service: SlackService = Depends(get_slack_service)
):
    return service.list_thread_messages(channel_id, thread_ts, cursor)

@router.get("/channels/{channel_id}/messages", response_model=MessageList)
@input_schema(schema_class=ListChannelMessagesParams)
async def list_channel_messages(
    channel_id: str,
    cursor: Optional[str] = None,
    service: SlackService = Depends(get_slack_service)
):
    return service.list_channel_messages(channel_id, cursor)

@router.get("/direct-messages/{user_id}", response_model=MessageList)
@input_schema(schema_class=ListDirectMessagesWithUserParams)
async def list_direct_messages_with_user(
    user_id: str,
    cursor: Optional[str] = None,
    service: SlackService = Depends(get_slack_service)
):
    return service.list_direct_messages_with_user(user_id, cursor)