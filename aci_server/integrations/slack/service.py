from typing import Optional
from .client import SlackClient
from .schema import (
    ChannelList, Channel, ChannelMemberList, 
    ChannelMember, MessageList, Message
)

class SlackService:
    def __init__(self, client: SlackClient):
        self.client = client

    def list_channels(self, cursor: Optional[str] = None) -> ChannelList:
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
        return ChannelList(
            channels=channels,
            cursor=response.get("response_metadata", {}).get("next_cursor")
        )

    def list_channel_members(self, channel_id: str, cursor: Optional[str] = None) -> ChannelMemberList:
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
        return ChannelMemberList(
            members=members,
            cursor=response.get("response_metadata", {}).get("next_cursor")
        )

    def list_direct_messages(self, cursor: Optional[str] = None) -> MessageList:
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
        return MessageList(
            messages=messages,
            cursor=response.get("response_metadata", {}).get("next_cursor")
        )

    def post_message(self, channel: str, text: str) -> Message:
        response = self.client.post_message(channel=channel, text=text)
        user_info = self.client.users_info(response["message"]["user"])["user"]
        return Message(
            id=response["message"].get("client_msg_id", response["message"]["ts"]),
            text=response["message"]["text"],
            user=user_info["id"],
            user_name=user_info["name"],
            real_name=user_info.get("real_name"),
            timestamp=response["message"]["ts"],
            thread_ts=response["message"].get("thread_ts")
        )

    def send_dm(self, user_id: str, text: str) -> Message:
        response = self.client.send_dm(user_id=user_id, text=text)
        user_info = self.client.users_info(response["message"]["user"])["user"]
        return Message(
            id=response["message"].get("client_msg_id", response["message"]["ts"]),
            text=response["message"]["text"],
            user=user_info["id"],
            user_name=user_info["name"],
            real_name=user_info.get("real_name"),
            timestamp=response["message"]["ts"],
            thread_ts=response["message"].get("thread_ts")
        )

    def reply_in_thread(self, channel: str, thread_ts: str, text: str) -> Message:
        response = self.client.reply_in_thread(
            channel=channel,
            thread_ts=thread_ts,
            text=text
        )
        user_info = self.client.users_info(response["message"]["user"])["user"]
        return Message(
            id=response["message"].get("client_msg_id", response["message"]["ts"]),
            text=response["message"]["text"],
            user=user_info["id"],
            user_name=user_info["name"],
            real_name=user_info.get("real_name"),
            timestamp=response["message"]["ts"],
            thread_ts=response["message"]["thread_ts"]
        )

    def list_thread_messages(self, channel: str, thread_ts: str, cursor: Optional[str] = None) -> MessageList:
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
        return MessageList(
            messages=messages,
            cursor=response.get("response_metadata", {}).get("next_cursor")
        )

    def list_channel_messages(self, channel: str, cursor: Optional[str] = None) -> MessageList:
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
        return MessageList(
            messages=messages,
            cursor=response.get("response_metadata", {}).get("next_cursor")
        )

    def list_direct_messages_with_user(self, user_id: str, cursor: Optional[str] = None) -> MessageList:
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
        
        return MessageList(
            messages=messages,
            cursor=response.get("response_metadata", {}).get("next_cursor")
        )