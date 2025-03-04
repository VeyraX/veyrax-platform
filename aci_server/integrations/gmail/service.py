from typing import Optional, Dict, Any, Union
from .client import GmailClient
from .schema import MessageList, Message, DraftResponse, DraftList, MessageFilters, DraftMessage, ApiResponse
import base64
from datetime import datetime
from email.mime.text import MIMEText
from dateutil import parser
import os
from ..common.component_handler import load_components, prepare_components_auto
import json

class GmailService:
    def __init__(self, client: GmailClient):
        self.client = client
        self.components_data = self._load_components()

    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
        
    def prepare_response(self, data: Union[Message, MessageList, DraftList, DraftResponse], component_name: str = None) -> ApiResponse:
        tool_name = "gmail"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)

    def _generate_html_link(self, message_id: str) -> str:
        return f"https://mail.google.com/mail/u/0/#inbox/{message_id}"

    def get_messages(self, pageToken: Optional[str] = None, filters: Optional[MessageFilters] = None) -> ApiResponse:
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
            if filters.from_email:
                query_parts.append(f'from:{filters.from_email}')
            if filters.has_attachments:
                query_parts.append(f'has:attachment')
        
        q = ' '.join(query_parts) if query_parts else None
        max_results = filters.max_results if filters and filters.max_results else 5
        response = self.client.list_messages(pageToken=pageToken, q=q, maxResults=max_results)
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
                'date': parser.parse(self._get_header(message, 'Date')),
                'html_link': self._generate_html_link(message['id'])
            })
            
        message_list = MessageList(
            messages=messages,
            pageToken=response.get('nextPageToken')
        )
        
        return self.prepare_response(message_list, "GmailMessageList")

    def get_message(self, message_id: str) -> ApiResponse:
        message_data = self.client.get_message(message_id)
        message = Message(
            id=message_data['id'],
            thread_id=message_data['threadId'],
            subject=self._get_header(message_data, 'Subject'),
            snippet=message_data['snippet'],
            body=self._get_body(message_data),
            sender=self._get_header(message_data, 'From'),
            recipient=self._get_header(message_data, 'To'),
            date=parser.parse(self._get_header(message_data, 'Date')),
            labels=message_data['labelIds'],
            html_link=self._generate_html_link(message_data['id'])
        )
        
        return self.prepare_response(message, "GmailMessageCard")

    def send_message(self, message_id: str) -> ApiResponse:
        message = self.client.get_message(message_id)
        
        new_message = MIMEText(self._get_body(message))
        new_message['to'] = self._get_header(message, 'To')
        new_message['subject'] = self._get_header(message, 'Subject')
        
        raw_message = {
            'raw': base64.urlsafe_b64encode(new_message.as_bytes()).decode('utf-8')
        }
        
        sent_message = self.client.service.users().messages().send(
            userId='me',
            body=raw_message
        ).execute()
        
        message_data = self.client.service.users().messages().get(
            userId='me',
            id=sent_message['id'],
            format='full'
        ).execute()

        message_obj = Message(
            id=message_data['id'],
            thread_id=message_data['threadId'],
            subject=self._get_header(message_data, 'Subject'),
            snippet=message_data['snippet'],
            body=self._get_body(message_data),
            sender=self._get_header(message_data, 'From'),
            recipient=self._get_header(message_data, 'To'),
            date=parser.parse(self._get_header(message_data, 'Date')),
            html_link=self._generate_html_link(message_data['id']),
            labels=message_data.get('labelIds', [])
        )
        
        return self.prepare_response(message_obj, "GmailMessageCard")

    def delete_message(self, message_id: str) -> None:
        self.client.delete_message(message_id)

    def _create_mime_message(self, to: str, subject: str, body: str) -> Dict[str, Any]:
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        
        return {
            'raw': base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        }

    def create_draft(self, draft_args: DraftMessage) -> ApiResponse:
        message = self._create_mime_message(draft_args.recipient, draft_args.subject, draft_args.body)
        draft = self.client.create_draft(message)
        
        draft_id = draft['id']
        message_id = draft['message']['id']
        
        message_data = self.client.get_message(message_id)
        
        message_obj = Message(
            id=message_id,
            thread_id=message_data['threadId'],
            subject=self._get_header(message_data, 'Subject'),
            snippet=message_data['snippet'],
            body=self._get_body(message_data),
            sender=self._get_header(message_data, 'From'),
            recipient=self._get_header(message_data, 'To'),
            date=parser.parse(self._get_header(message_data, 'Date')),
            html_link=self._generate_html_link(message_id),
            labels=message_data.get('labelIds', []),
            draft_id=draft_id
        )
        
        return self.prepare_response(message_obj, "GmailMessageCard")

    def delete_draft(self, draft_id: str) -> None:
        self.client.delete_draft(draft_id)

    def get_drafts(self, pageToken: Optional[str] = None) -> ApiResponse:
        response = self.client.list_drafts(pageToken=pageToken, maxResults=20)
        messages = []
        
        for draft in response.get('drafts', []):
            draft_full = self.client.get_draft(draft['id'])
            message_data = draft_full['message']
            
            try:
                date = parser.parse(self._get_header(message_data, 'Date')) if self._get_header(message_data, 'Date') else datetime.now()
            except:
                date = datetime.now()
                
            messages.append({
                'id': message_data['id'],
                'thread_id': message_data['threadId'],
                'snippet': message_data['snippet'],
                'subject': self._get_header(message_data, 'Subject'),
                'body': self._get_body(message_data),
                'recipient': self._get_header(message_data, 'To') or None,
                'sender': self._get_header(message_data, 'From') or None,
                'date': date,
                'html_link': self._generate_html_link(message_data['id'])
            })
            
        message_list = MessageList(
            messages=messages,
            pageToken=response.get('nextPageToken')
        )
        
        return self.prepare_response(message_list, "GmailMessageList")

    def modify_draft(self, draft_id: str, update_args: DraftMessage) -> ApiResponse:
        current_draft = self.client.get_draft(draft_id)
        current_message = current_draft['message']
        
        new_to = update_args.recipient or self._get_header(current_message, 'To')
        new_subject = update_args.subject or self._get_header(current_message, 'Subject')
        new_body = update_args.body or self._get_body(current_message)
        
        message = self._create_mime_message(new_to, new_subject, new_body)
        draft = self.client.update_draft(draft_id, message)
        
        # Get the updated message
        message_data = self.client.get_message(draft['message']['id'])
        message_obj = Message(
            id=message_data['id'],
            thread_id=message_data['threadId'],
            subject=self._get_header(message_data, 'Subject'),
            snippet=message_data['snippet'],
            body=self._get_body(message_data),
            sender=self._get_header(message_data, 'From'),
            recipient=self._get_header(message_data, 'To'),
            date=parser.parse(self._get_header(message_data, 'Date')),
            html_link=self._generate_html_link(message_data['id']),
            labels=message_data.get('labelIds', [])
        )
        
        return self.prepare_response(message_obj, "GmailMessageCard")

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
