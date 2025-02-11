from typing import Optional
from .client import GmailClient
from .schema import MessageList, Message, DraftResponse, DraftList, DraftUpdate, MessageFilters
import base64
from datetime import datetime

class GmailService:
    def __init__(self, client: GmailClient):
        self.client = client

    def get_messages(self, page_token: Optional[str] = None, filters: Optional[MessageFilters] = None) -> MessageList:
        query_parts = []
        
        if filters:
            if filters.body_keywords:
                query_parts.append(f'"{filters.body_keywords}"')
            if filters.recipient:
                query_parts.append(f'to:{filters.recipient}')
            if filters.subject_keywords:
                query_parts.append(f'subject:"{filters.subject_keywords}"')
            if filters.after_date:
                after_date = datetime.fromisoformat(filters.after_date).strftime('%Y/%m/%d')
                query_parts.append(f'after:{after_date}')
            if filters.before_date:
                before_date = datetime.fromisoformat(filters.before_date).strftime('%Y/%m/%d')
                query_parts.append(f'before:{before_date}')
        
        query = ' '.join(query_parts) if query_parts else None
        response = self.client.list_messages(page_token=page_token, query=query)
        messages = []
        
        for msg in response.get('messages', []):
            message = self.client.get_message(msg['id'])
            messages.append({
                'id': message['id'],
                'thread_id': message['threadId'],
                'snippet': message['snippet'],
                'subject': self._get_header(message, 'Subject')
            })
            
        return MessageList(
            messages=messages,
            next_page_token=response.get('nextPageToken')
        )

    def get_message(self, message_id: str) -> Message:
        message = self.client.get_message(message_id)
        return Message(
            id=message['id'],
            thread_id=message['threadId'],
            subject=self._get_header(message, 'Subject'),
            snippet=message['snippet'],
            body=self._get_body(message),
            sender=self._get_header(message, 'From'),
            recipient=self._get_header(message, 'To'),
            labels=message['labelIds']
        )

    def send_message(self, message_id: str) -> str:
        response = self.client.send_message(message_id)
        return response['id']

    def delete_message(self, message_id: str) -> None:
        self.client.delete_message(message_id)

    def create_draft(self, to: str, subject: str, body: str) -> DraftResponse:
        draft = self.client.create_draft(to, subject, body)
        return DraftResponse(
            draft_id=draft['id'],
            message_id=draft['message']['id']
        )

    def delete_draft(self, draft_id: str) -> None:
        self.client.delete_draft(draft_id)

    def get_drafts(self, page_token: Optional[str] = None) -> DraftList:
        response = self.client.list_drafts(page_token=page_token)
        drafts = []
        
        for draft in response.get('drafts', []):
            draft_full = self.client.get_draft(draft['id'])
            message = draft_full['message']
            drafts.append({
                'draft_id': draft_full['id'],
                'message_id': message['id'],
                'snippet': message['snippet'],
                'subject': self._get_header(message, 'Subject')
            })
            
        return DraftList(
            drafts=drafts,
            next_page_token=response.get('nextPageToken')
        )

    def modify_draft(self, draft_id: str, to: Optional[str] = None,
                    subject: Optional[str] = None, body: Optional[str] = None) -> Message:
        draft = self.client.modify_draft(draft_id, to, subject, body)
        return self.get_message(draft['message']['id'])

    def _get_header(self, message: dict, name: str) -> Optional[str]:
        headers = message['payload']['headers']
        header = next((h for h in headers if h['name'].lower() == name.lower()), None)
        return header['value'] if header else None

    def _get_body(self, message: dict) -> str:
        if 'parts' in message['payload']:
            for part in message['payload']['parts']:
                if part['mimeType'] == 'text/plain':
                    return base64.urlsafe_b64decode(part['body']['data']).decode()
        return base64.urlsafe_b64decode(message['payload']['body']['data']).decode()
