from typing import Optional, Dict, Any
from .client import GmailClient
from .schema import MessageList, Message, DraftResponse, DraftList, MessageFilters, DraftMessage
import base64
from datetime import datetime
from email.mime.text import MIMEText
from dateutil import parser

class GmailService:
    def __init__(self, client: GmailClient):
        self.client = client

    def get_messages(self, pageToken: Optional[str] = None, filters: Optional[MessageFilters] = None) -> MessageList:
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
        
        q = ' '.join(query_parts) if query_parts else None
        response = self.client.list_messages(pageToken=pageToken, q=q, maxResults=20)
        messages = []
        
        for msg in response.get('messages', []):
            message = self.client.get_message(msg['id'])
            messages.append({
                'id': message['id'],
                'thread_id': message['threadId'],
                'snippet': message['snippet'],
                'subject': self._get_header(message, 'Subject'),
                'body': self._get_body(message),
                'recipient': self._get_header(message, 'To') or None,
                'sender': self._get_header(message, 'From') or None,
                'date': parser.parse(self._get_header(message, 'Date'))
            })
            
        return MessageList(
            messages=messages,
            pageToken=response.get('nextPageToken')
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
        draft = self.client.get_draft(message_id)
        message = draft['message']
        
        new_message = MIMEText(self._get_body(message))
        new_message['to'] = self._get_header(message, 'To')
        new_message['subject'] = self._get_header(message, 'Subject')
        
        raw_message = {
            'raw': base64.urlsafe_b64encode(new_message.as_bytes()).decode('utf-8')
        }
        
        response = self.client.service.users().messages().send(
            userId='me',
            body=raw_message
        ).execute()
        
        return response['id']

    def delete_message(self, message_id: str) -> None:
        self.client.delete_message(message_id)

    def _create_mime_message(self, to: str, subject: str, body: str) -> Dict[str, Any]:
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        
        return {
            'raw': base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        }

    def create_draft(self, draft_args: DraftMessage) -> DraftResponse:
        message = self._create_mime_message(draft_args.to, draft_args.subject, draft_args.body)
        draft = self.client.create_draft(message)
        return DraftResponse(
            draft_id=draft['id'],
            message_id=draft['message']['id']
        )

    def delete_draft(self, draft_id: str) -> None:
        self.client.delete_draft(draft_id)

    def get_drafts(self, pageToken: Optional[str] = None) -> DraftList:
        response = self.client.list_drafts(pageToken=pageToken, maxResults=20)
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
            pageToken=response.get('nextPageToken')
        )

    def modify_draft(self, draft_id: str, draft_args: DraftMessage) -> Message:
        current_draft = self.client.get_draft(draft_id)
        current_message = current_draft['message']
        
        new_to = draft_args.to or self._get_header(current_message, 'To')
        new_subject = draft_args.subject or self._get_header(current_message, 'Subject')
        new_body = draft_args.body or self._get_body(current_message)
        
        message = self._create_mime_message(new_to, new_subject, new_body)
        draft = self.client.update_draft(draft_id, message)
        return self.get_message(draft['message']['id'])

    def _get_header(self, message: dict, name: str) -> Optional[str]:
        headers = message['payload']['headers']
        header = next((h for h in headers if h['name'].lower() == name.lower()), None)
        return header['value'] if header else None

    def _get_body(self, message: dict) -> str:
        try:
            if 'parts' in message['payload']:
                for part in message['payload']['parts']:
                    if part['mimeType'] == 'text/plain':
                        if 'data' in part['body']:
                            return base64.urlsafe_b64decode(part['body']['data']).decode()
                        elif 'attachmentId' in part['body']:
                            continue
                for part in message['payload']['parts']:
                    if 'data' in part['body']:
                        return base64.urlsafe_b64decode(part['body']['data']).decode()
            
            if 'body' in message['payload'] and 'data' in message['payload']['body']:
                return base64.urlsafe_b64decode(message['payload']['body']['data']).decode()
            
            return ""
        except Exception as e:
            print(f"Error decoding message body: {e}")
            return ""
