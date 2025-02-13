from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from .schema import (
    ChannelList, ChannelMemberList, MessageList, 
    Message, DirectMessage, ThreadMessage
)
from .service import SlackService
from .client import SlackClient
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
async def list_channels(
    cursor: Optional[str] = None,
    service: SlackService = Depends(get_slack_service)
):
    return service.list_channels(cursor)

@router.get("/channels/{channel_id}/members", response_model=ChannelMemberList)
async def list_channel_members(
    channel_id: str,
    cursor: Optional[str] = None,
    service: SlackService = Depends(get_slack_service)
):
    return service.list_channel_members(channel_id, cursor)

@router.get("/direct-messages", response_model=MessageList)
async def list_direct_messages(
    cursor: Optional[str] = None,
    service: SlackService = Depends(get_slack_service)
):
    return service.list_direct_messages(cursor)

@router.post("/channels/{channel_id}/messages", response_model=Message)
async def post_message(
    channel_id: str,
    message: ThreadMessage,
    service: SlackService = Depends(get_slack_service)
):
    return service.post_message(channel_id, message.text)

@router.post("/dm", response_model=Message)
async def send_dm(
    message: DirectMessage,
    service: SlackService = Depends(get_slack_service)
) -> Message:
    return service.send_dm(message.user_id, message.text)

@router.post("/channels/{channel_id}/threads/{thread_ts}/replies", response_model=Message)
async def reply_in_thread(
    channel_id: str,
    thread_ts: str,
    message: ThreadMessage,
    service: SlackService = Depends(get_slack_service)
):
    return service.reply_in_thread(channel_id, thread_ts, message.text)

@router.get("/channels/{channel_id}/threads/{thread_ts}/messages", response_model=MessageList)
async def list_thread_messages(
    channel_id: str,
    thread_ts: str,
    cursor: Optional[str] = None,
    service: SlackService = Depends(get_slack_service)
):
    return service.list_thread_messages(channel_id, thread_ts, cursor)

@router.get("/channels/{channel_id}/messages", response_model=MessageList)
async def list_channel_messages(
    channel_id: str,
    cursor: Optional[str] = None,
    service: SlackService = Depends(get_slack_service)
):
    return service.list_channel_messages(channel_id, cursor)

@router.get("/direct-messages/{user_id}", response_model=MessageList)
async def list_direct_messages_with_user(
    user_id: str,
    cursor: Optional[str] = None,
    service: SlackService = Depends(get_slack_service)
):
    return service.list_direct_messages_with_user(user_id, cursor)