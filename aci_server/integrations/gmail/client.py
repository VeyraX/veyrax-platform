from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from typing import Optional, Dict, Any
import base64
from email.mime.text import MIMEText

class GmailClient:
    def __init__(self, credentials: Credentials):
        self.service = build('gmail', 'v1', credentials=credentials)

    def list_messages(self, page_token: Optional[str] = None, max_results: int = 20, query: Optional[str] = None):
        return self.service.users().messages().list(
            userId='me',
            maxResults=max_results,
            pageToken=page_token,
            q=query
        ).execute()

    def get_message(self, message_id: str):
        return self.service.users().messages().get(
            userId='me',
            id=message_id,
            format='full'
        ).execute()

    def create_draft(self, to: str, subject: str, body: str):
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        return self.service.users().drafts().create(
            userId='me',
            body={'message': {'raw': raw}}
        ).execute()

    def delete_draft(self, draft_id: str):
        return self.service.users().drafts().delete(
            userId='me',
            id=draft_id
        ).execute()

    def send_draft(self, draft_id: str):
        return self.service.users().drafts().send(
            userId='me',
            body={'id': draft_id}
        ).execute()

    def list_drafts(self, page_token: Optional[str] = None, max_results: int = 20):
        return self.service.users().drafts().list(
            userId='me',
            maxResults=max_results,
            pageToken=page_token
        ).execute()

    def get_draft(self, draft_id: str):
        return self.service.users().drafts().get(
            userId='me',
            id=draft_id,
            format='full'
        ).execute()

    def send_message(self, message_id: str):
        return self.service.users().messages().send(
            userId='me',
            body={'id': message_id}
        ).execute()

    def delete_message(self, message_id: str):
        return self.service.users().messages().delete(
            userId='me',
            id=message_id
        ).execute()

    def modify_draft(self, draft_id: str, to: Optional[str] = None, 
                    subject: Optional[str] = None, body: Optional[str] = None):
        message = MIMEText(body) if body else MIMEText('')
        if to:
            message['to'] = to
        if subject:
            message['subject'] = subject
        
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        return self.service.users().drafts().update(
            userId='me',
            id=draft_id,
            body={
                'message': {'raw': raw}
            }
        ).execute()
