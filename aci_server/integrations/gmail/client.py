from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from typing import Optional, Dict, Any
import base64
from email.mime.text import MIMEText

class GmailClient:
    def __init__(self, credentials: Credentials):
        self.service = build('gmail', 'v1', credentials=credentials)

    def list_messages(self, **kwargs) -> Dict[str, Any]:
        return self.service.users().messages().list(
            userId='me',
            **kwargs
        ).execute()

    def get_message(self, message_id: str) -> Dict[str, Any]:
        return self.service.users().messages().get(
            userId='me',
            id=message_id,
            format='full'
        ).execute()

    def create_draft(self, message: Dict[str, Any]) -> Dict[str, Any]:
        return self.service.users().drafts().create(
            userId='me',
            body={'message': message}
        ).execute()

    def delete_draft(self, draft_id: str) -> None:
        self.service.users().drafts().delete(
            userId='me',
            id=draft_id
        ).execute()

    def send_draft(self, draft_id: str) -> Dict[str, Any]:
        return self.service.users().drafts().send(
            userId='me',
            body={'id': draft_id}
        ).execute()

    def list_drafts(self, **kwargs) -> Dict[str, Any]:
        return self.service.users().drafts().list(
            userId='me',
            **kwargs
        ).execute()

    def get_draft(self, draft_id: str) -> Dict[str, Any]:
        return self.service.users().drafts().get(
            userId='me',
            id=draft_id,
            format='full'
        ).execute()

    def send_message(self, message_id: str) -> Dict[str, Any]:
        return self.service.users().messages().send(
            userId='me',
            body={'id': message_id}
        ).execute()

    def delete_message(self, message_id: str) -> None:
        self.service.users().messages().delete(
            userId='me',
            id=message_id
        ).execute()

    def update_draft(self, draft_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
        return self.service.users().drafts().update(
            userId='me',
            id=draft_id,
            body={'message': message}
        ).execute()
