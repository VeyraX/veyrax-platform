from slack_sdk import WebClient
from typing import Dict, Any

class SlackClient:
    def __init__(self, token: str):
        self.client = WebClient(token=token)

    def list_channels(self, **kwargs) -> Dict[str, Any]:
        return self.client.conversations_list(**kwargs)

    def list_channel_members(self, channel_id: str, **kwargs) -> Dict[str, Any]:
        return self.client.conversations_members(channel=channel_id, **kwargs)

    def list_direct_messages(self, **kwargs) -> Dict[str, Any]:
        return self.client.conversations_list(types="im", **kwargs)

    def post_message(self, channel: str, text: str, **kwargs) -> Dict[str, Any]:
        return self.client.chat_postMessage(
            channel=channel,
            text=text,
            as_user=True,
            **kwargs
        )

    def send_dm(self, user_id: str, text: str, **kwargs) -> Dict[str, Any]:
        response = self.client.conversations_open(users=[user_id])
        channel_id = response["channel"]["id"]
        return self.client.chat_postMessage(
            channel=channel_id,
            text=text,
            as_user=True,
            **kwargs
        )

    def reply_in_thread(self, channel: str, thread_ts: str, text: str, **kwargs) -> Dict[str, Any]:
        return self.client.chat_postMessage(
            channel=channel,
            thread_ts=thread_ts,
            text=text,
            as_user=True,
            **kwargs
        )

    def list_thread_messages(self, channel: str, thread_ts: str, **kwargs) -> Dict[str, Any]:
        return self.client.conversations_replies(
            channel=channel,
            ts=thread_ts,
            **kwargs
        )

    def list_channel_messages(self, channel: str, **kwargs) -> Dict[str, Any]:
        return self.client.conversations_history(
            channel=channel,
            **kwargs
        )

    def users_info(self, user_id: str) -> Dict[str, Any]:
        return self.client.users_info(user=user_id)

    def list_direct_messages_with_user(self, channel_id: str, **kwargs) -> Dict[str, Any]:
        return self.client.conversations_history(
            channel=channel_id,
            **kwargs
        )

    def open_dm_channel(self, user_id: str) -> Dict[str, Any]:
        return self.client.conversations_open(users=[user_id])

    def join_channel(self, channel: str) -> Dict[str, Any]:
        return self.client.conversations_join(channel=channel)