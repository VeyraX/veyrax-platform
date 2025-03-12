from typing import Optional, Dict, Any, Union, List
import json
import os
from .client import SlackClient
from .schema import (
    ChannelList, Channel, ChannelMemberList, 
    ChannelMember, MessageList, Message, ApiResponse
)
import logging
from ..common.component_handler import load_components, prepare_components_auto

class SlackService:
    def __init__(self, client: SlackClient):
        self.client = client
        self.components_data = self._load_components()

    def _load_components(self) -> Dict[str, Any]:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)

    def _unwrap_user_references(self, message_text: str, user_cache: Dict[str, Dict] = None) -> str:
        if not message_text:
            return message_text
            
        if user_cache is None:
            user_cache = {}
            
        import re
        user_refs = re.findall(r'<@(U[A-Z0-9]+)>', message_text)
        
        for user_id in user_refs:
            if user_id not in user_cache:
                try:
                    user_info = self.client.client.users_info(user=user_id)
                    user_cache[user_id] = user_info["user"]
                except Exception as e:
                    logging.warning(f"Failed to get user info for {user_id}: {str(e)}")
                    message_text = message_text.replace(f"<@{user_id}>", f"@{user_id}")
                    continue
                    
            user = user_cache[user_id]
            display_name = user.get("real_name") or user.get("name") or user_id
            message_text = message_text.replace(f"<@{user_id}>", f"@{display_name}")
            
        return message_text
        
    def _process_messages(self, messages: List[Dict], user_cache: Dict[str, Dict] = None) -> List[Message]:
        if user_cache is None:
            user_cache = {}
            
        processed_messages = []
        for msg in messages:
            text = self._unwrap_user_references(msg.get("text", ""), user_cache)
            
            user_id = msg.get("user", "")
            user_info = None
            
            if user_id:
                if user_id not in user_cache:
                    try:
                        user_info = self.client.client.users_info(user=user_id)["user"]
                        user_cache[user_id] = user_info
                    except Exception as e:
                        logging.warning(f"Failed to get user info for message user {user_id}: {str(e)}")
                else:
                    user_info = user_cache[user_id]
            
            processed_messages.append(
                Message(
                    id=msg.get("client_msg_id", msg.get("ts", "")),
                    text=text,
                    user=user_id,
                    user_name=user_info["name"] if user_info else "",
                    real_name=user_info.get("real_name", "") if user_info else "",
                    timestamp=msg.get("ts", ""),
                    thread_ts=msg.get("thread_ts")
                )
            )
        
        return processed_messages

    def prepare_response(self, data: Union[Channel, ChannelList, ChannelMember, ChannelMemberList, Message, MessageList], component_name: str = None) -> ApiResponse:
        tool_name = "slack"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)

    def list_channels(self, cursor: Optional[str] = None) -> ApiResponse:
        response = self.client.list_channels(cursor=cursor)
        channels = [
            Channel(
                id=channel["id"],
                name=channel["name"],
                is_private=channel["is_private"],
                topic=channel.get("topic", {}).get("value"),
                purpose=channel.get("purpose", {}).get("value")
            )
            for channel in response["channels"]
        ]
        channel_list = ChannelList(
            channels=channels,
            cursor=response.get("response_metadata", {}).get("next_cursor")
        )
        return self.prepare_response(channel_list, "SlackChannelList")

    def list_channel_members(self, channel_id: str, cursor: Optional[str] = None) -> ApiResponse:
        response = self.client.list_channel_members(channel_id=channel_id, cursor=cursor)
        member_ids = response["members"]
        members = []
        for member_id in member_ids:
            user_info = self.client.client.users_info(user=member_id)["user"]
            members.append(
                ChannelMember(
                    id=user_info["id"],
                    name=user_info["name"],
                    real_name=user_info.get("real_name"),
                    is_bot=user_info.get("is_bot", False)
                )
            )
        member_list = ChannelMemberList(
            members=members,
            cursor=response.get("response_metadata", {}).get("next_cursor")
        )
        return self.prepare_response(member_list, "SlackChannelMembers")

    def list_direct_messages(self, cursor: Optional[str] = None) -> ApiResponse:
        response = self.client.list_direct_messages(cursor=cursor)
        
        user_cache = {}
        messages = []
        for conv in response["channels"]:
            user_id = conv.get("user", "")
            if user_id not in user_cache:
                try:
                    user_info = self.client.client.users_info(user=user_id)["user"]
                    user_cache[user_id] = user_info
                except Exception:
                    user_info = {"id": user_id, "name": "", "real_name": ""}
                    user_cache[user_id] = user_info
            else:
                user_info = user_cache[user_id]
                
            latest = conv.get("latest", {})
            text = latest.get("text", "")
            
            if text:
                text = self._unwrap_user_references(text, user_cache)
                
            messages.append(
                Message(
                    id=conv["id"],
                    text=text,
                    user=user_info["id"],
                    user_name=user_info["name"],
                    real_name=user_info.get("real_name"),
                    timestamp=latest.get("ts", ""),
                    thread_ts=latest.get("thread_ts")
                )
            )
            
        message_list = MessageList(
            messages=messages,
            cursor=response.get("response_metadata", {}).get("next_cursor")
        )
        return self.prepare_response(message_list, "SlackMessageList")

    def post_message(self, channel: str, text: str) -> ApiResponse:
        
        join_result = self.client.join_channel(channel=channel)
        
        if not join_result.get("ok", True) and "not_in_channel" in str(join_result.get("error", "")):
            raise Exception(f"Cannot post message: {join_result.get('error', 'Not in channel')}")
        
        response = self.client.post_message(channel=channel, text=text)
        user_info = self.client.users_info(response["message"]["user"])["user"]
        message = Message(
            id=response["message"].get("client_msg_id", response["message"]["ts"]),
            text=response["message"]["text"],
            user=user_info["id"],
            user_name=user_info["name"],
            real_name=user_info.get("real_name"),
            timestamp=response["message"]["ts"],
            thread_ts=response["message"].get("thread_ts")
        )
        return self.prepare_response(message, "SlackMessageComposer")

    def send_dm(self, user_id: str, text: str) -> ApiResponse:
        response = self.client.send_dm(user_id=user_id, text=text)
        user_info = self.client.users_info(response["message"]["user"])["user"]
        message = Message(
            id=response["message"].get("client_msg_id", response["message"]["ts"]),
            text=response["message"]["text"],
            user=user_info["id"],
            user_name=user_info["name"],
            real_name=user_info.get("real_name"),
            timestamp=response["message"]["ts"],
            thread_ts=response["message"].get("thread_ts")
        )
        return self.prepare_response(message, "SlackMessageComposer")

    def reply_in_thread(self, channel: str, thread_ts: str, text: str) -> ApiResponse:
        
        response = self.client.reply_in_thread(
            channel=channel,
            thread_ts=thread_ts,
            text=text
        )
        user_info = self.client.users_info(response["message"]["user"])["user"]
        message = Message(
            id=response["message"].get("client_msg_id", response["message"]["ts"]),
            text=response["message"]["text"],
            user=user_info["id"],
            user_name=user_info["name"],
            real_name=user_info.get("real_name"),
            timestamp=response["message"]["ts"],
            thread_ts=response["message"]["thread_ts"]
        )
        return self.prepare_response(message, "SlackMessageComposer")

    def list_thread_messages(self, channel: str, thread_ts: str, cursor: Optional[str] = None) -> ApiResponse:
        
        response = self.client.list_thread_messages(
            channel=channel,
            thread_ts=thread_ts,
            cursor=cursor
        )
        
        user_cache = {}
        messages = self._process_messages(response["messages"], user_cache)
        
        message_list = MessageList(
            messages=messages,
            cursor=response.get("response_metadata", {}).get("next_cursor")
        )
        return self.prepare_response(message_list, "SlackMessageList")

    def list_channel_messages(self, channel: str, cursor: Optional[str] = None) -> ApiResponse:
        
        response = self.client.list_channel_messages(
            channel=channel,
            cursor=cursor
        )
        
        user_cache = {}
        messages = self._process_messages(response["messages"], user_cache)
        
        message_list = MessageList(
            messages=messages,
            cursor=response.get("response_metadata", {}).get("next_cursor")
        )
        return self.prepare_response(message_list, "SlackMessageList")

    def list_direct_messages_with_user(self, user_id: str, cursor: Optional[str] = None) -> ApiResponse:
        channel_response = self.client.open_dm_channel(user_id)
        channel_id = channel_response["channel"]["id"]
        
        response = self.client.list_direct_messages_with_user(channel_id, cursor=cursor)
        
        user_cache = {}
        messages = self._process_messages(response["messages"], user_cache)
        
        message_list = MessageList(
            messages=messages,
            cursor=response.get("response_metadata", {}).get("next_cursor")
        )
        return self.prepare_response(message_list, "SlackMessageList")