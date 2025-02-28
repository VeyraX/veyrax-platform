from typing import Optional, Dict, Any, Union, List
import json
import os
from .client import SlackClient
from .schema import (
    ChannelList, Channel, ChannelMemberList, 
    ChannelMember, MessageList, Message, ApiResponse
)

class SlackService:
    def __init__(self, client: SlackClient):
        self.client = client
        self.components = self._load_components()

    def _load_components(self) -> Dict[str, Any]:
        component_path = os.path.join(os.path.dirname(__file__), 'component.json')
        with open(component_path, 'r') as f:
            return json.load(f)

    def prepare_response(self, data: Union[Channel, ChannelList, ChannelMember, ChannelMemberList, Message, MessageList], component_name: str = None) -> ApiResponse:
        component = None
        if component_name:
            component = next((c for c in self.components if c["name"] == component_name), None)
        return ApiResponse(data=data, component=component)

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
                    real_name=user_info.get("real_name")
                )
            )
        member_list = ChannelMemberList(
            members=members,
            cursor=response.get("response_metadata", {}).get("next_cursor")
        )
        return self.prepare_response(member_list, "SlackChannelMembers")

    def list_direct_messages(self, cursor: Optional[str] = None) -> ApiResponse:
        response = self.client.list_direct_messages(cursor=cursor)
        messages = []
        for conv in response["channels"]:
            user_info = self.client.users_info(conv.get("user", ""))["user"]
            messages.append(
                Message(
                    id=conv["id"],
                    text=conv.get("latest", {}).get("text", ""),
                    user=user_info["id"],
                    user_name=user_info["name"],
                    real_name=user_info.get("real_name"),
                    timestamp=conv.get("latest", {}).get("ts", ""),
                    thread_ts=conv.get("latest", {}).get("thread_ts")
                )
            )
        message_list = MessageList(
            messages=messages,
            cursor=response.get("response_metadata", {}).get("next_cursor")
        )
        return self.prepare_response(message_list, "SlackMessageList")

    def post_message(self, channel: str, text: str) -> ApiResponse:
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
        messages = []
        for msg in response["messages"]:
            user_info = self.client.users_info(msg["user"])["user"]
            messages.append(
                Message(
                    id=msg.get("client_msg_id", msg["ts"]),
                    text=msg["text"],
                    user=msg["user"],
                    user_name=user_info["name"],
                    real_name=user_info.get("real_name"),
                    timestamp=msg["ts"],
                    thread_ts=msg.get("thread_ts")
                )
            )
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
        messages = []
        for msg in response["messages"]:
            user_info = self.client.users_info(msg["user"])["user"]
            messages.append(
                Message(
                    id=msg.get("client_msg_id", msg["ts"]),
                    text=msg["text"],
                    user=msg["user"],
                    user_name=user_info["name"],
                    real_name=user_info.get("real_name"),
                    timestamp=msg["ts"],
                    thread_ts=msg.get("thread_ts")
                )
            )
        message_list = MessageList(
            messages=messages,
            cursor=response.get("response_metadata", {}).get("next_cursor")
        )
        return self.prepare_response(message_list, "SlackMessageList")

    def list_direct_messages_with_user(self, user_id: str, cursor: Optional[str] = None) -> ApiResponse:
        channel_response = self.client.open_dm_channel(user_id)
        channel_id = channel_response["channel"]["id"]
        
        response = self.client.list_direct_messages_with_user(channel_id, cursor=cursor)
        
        messages = []
        for msg in response["messages"]:
            user_info = self.client.users_info(msg["user"])["user"]
            messages.append(
                Message(
                    id=msg.get("client_msg_id", msg["ts"]),
                    text=msg["text"],
                    user=msg["user"],
                    user_name=user_info["name"],
                    real_name=user_info.get("real_name"),
                    timestamp=msg["ts"],
                    thread_ts=msg.get("thread_ts")
                )
            )
        
        message_list = MessageList(
            messages=messages,
            cursor=response.get("response_metadata", {}).get("next_cursor")
        )
        return self.prepare_response(message_list, "SlackMessageList")