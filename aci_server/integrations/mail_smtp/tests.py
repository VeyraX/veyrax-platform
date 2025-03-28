import unittest
import pytest
from unittest.mock import MagicMock, patch
from .client import MailSMTPClient
from .service import MailSMTPService
from .schema import GetMessagesParams, GetMessageParams, SendMessageParams


class TestMailSMTPClient:
    """Tests for MailSMTPClient class."""
    
    def setup_method(self):
        self.client = MailSMTPClient("mail.example.com", 993, "user@example.com", "password", True, False)
    
    @patch("imaplib.IMAP4_SSL")
    def test_get_messages(self, mock_imap):
        # Setup mock
        mock_conn = MagicMock()
        mock_imap.return_value = mock_conn
        
        # Mock select response
        mock_conn.select.return_value = ('OK', [b'1'])
        
        # Mock search response
        mock_conn.search.return_value = ('OK', [b'1 2 3'])
        
        # Mock fetch response for message data
        mock_conn.fetch.side_effect = [
            ('OK', [(b'1', (b'RFC822', b'From: sender@example.com\r\nTo: recipient@example.com\r\nSubject: Test Email\r\n\r\nTest body'))]),
            ('OK', [(b'1', b'FLAGS (\\Seen)')]),
            ('OK', [(b'2', (b'RFC822', b'From: sender2@example.com\r\nTo: recipient2@example.com\r\nSubject: Test Email 2\r\n\r\nTest body 2'))]),
            ('OK', [(b'2', b'FLAGS ()')]),
            ('OK', [(b'3', (b'RFC822', b'From: sender3@example.com\r\nTo: recipient3@example.com\r\nSubject: Test Email 3\r\n\r\nTest body 3'))]),
            ('OK', [(b'3', b'FLAGS (\\Seen)')])
        ]
        
        # Call the method
        result = self.client.get_messages(folder="INBOX", limit=3, offset=0)
        
        # Verify results
        assert len(result["messages"]) == 3
        assert result["total"] == 3
        assert result["offset"] == 0
        assert result["limit"] == 3
        
        # Verify the first message
        assert result["messages"][0]["subject"] == "Test Email"
        assert result["messages"][0]["from_email"]["email"] == "sender@example.com"
        assert result["messages"][0]["is_read"] == True
        
        # Verify the second message
        assert result["messages"][1]["subject"] == "Test Email 2"
        assert result["messages"][1]["from_email"]["email"] == "sender2@example.com"
        assert result["messages"][1]["is_read"] == False
    
    @patch("imaplib.IMAP4_SSL")
    def test_get_message(self, mock_imap):
        # Setup mock
        mock_conn = MagicMock()
        mock_imap.return_value = mock_conn
        
        # Mock select response
        mock_conn.select.return_value = ('OK', [b'1'])
        
        # Mock search response
        mock_conn.search.return_value = ('OK', [b'1'])
        
        # Mock fetch response for message data
        mock_conn.fetch.side_effect = [
            ('OK', [(b'1', b'FLAGS (\\Seen)')]),
            ('OK', [(b'1', (b'RFC822', b'From: sender@example.com\r\nTo: recipient@example.com\r\nSubject: Test Email\r\n\r\nTest body'))])
        ]
        
        # Call the method
        result = self.client.get_message(message_id="1", mark_as_read=False)
        
        # Verify results
        assert result["subject"] == "Test Email"
        assert result["from_email"]["email"] == "sender@example.com"
        assert result["is_read"] == True
    
    @patch("smtplib.SMTP_SSL")
    def test_send_message(self, mock_smtp):
        # Setup mock
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        # Prepare message data
        message_data = {
            "subject": "Test Email",
            "from_email": {"email": "user@example.com", "name": "Test User"},
            "to": [{"email": "recipient@example.com", "name": "Recipient"}],
            "body_text": "This is a test email",
            "body_html": "<p>This is a test email</p>"
        }
        
        # Call the method
        result = self.client.send_message(message_data)
        
        # Verify results
        assert result["success"] == True
        assert "message_id" in result
        
        # Verify SMTP calls
        mock_server.login.assert_called_once_with("user@example.com", "password")
        mock_server.send_message.assert_called_once()
        mock_server.quit.assert_called_once()
    
    @patch("imaplib.IMAP4_SSL")
    def test_get_folders(self, mock_imap):
        # Setup mock
        mock_conn = MagicMock()
        mock_imap.return_value = mock_conn
        
        # Mock list response
        mock_conn.list.return_value = ('OK', [
            b'(\\HasNoChildren) "/" "INBOX"',
            b'(\\HasChildren) "/" "Sent"',
            b'(\\HasNoChildren) "/" "Trash"'
        ])
        
        # Call the method
        result = self.client.get_folders()
        
        # Verify results
        assert len(result["folders"]) == 3
        assert result["folders"][0]["name"] == "INBOX"
        assert result["folders"][1]["name"] == "Sent"
        assert result["folders"][2]["name"] == "Trash"


class TestMailSMTPService:
    """Tests for MailSMTPService class."""
    
    def setup_method(self):
        self.mock_client = MagicMock()
        self.service = MailSMTPService(self.mock_client)
        
        # Mock the load_components method
        self.service._load_components = MagicMock(return_value={
            "MailSMTPMessageList": {
                "name": "MailSMTPMessageList",
                "displayName": "Email Messages"
            },
            "MailSMTPMessageDetail": {
                "name": "MailSMTPMessageDetail",
                "displayName": "Email Message"
            },
            "MailSMTPSendResult": {
                "name": "MailSMTPSendResult",
                "displayName": "Send Email Result"
            }
        })
        self.service.components_data = self.service._load_components()
    
    def test_get_messages(self):
        # Mock client response
        self.mock_client.get_messages.return_value = {
            "messages": [
                {
                    "id": "1",
                    "subject": "Test Email",
                    "from_email": {"email": "sender@example.com", "name": None},
                    "to": [{"email": "recipient@example.com", "name": None}],
                    "cc": [],
                    "body": {"text": "Test body", "html": None},
                    "attachments": [],
                    "headers": [],
                    "date": "Mon, 1 Jan 2023 12:00:00 +0000",
                    "folder": "INBOX",
                    "is_read": True
                }
            ],
            "total": 1,
            "offset": 0,
            "limit": 20
        }
        
        # Create params
        params = GetMessagesParams(
            folder="INBOX",
            limit=20,
            offset=0
        )
        
        # Call the service method
        result = self.service.get_messages(params)
        
        # Verify results
        assert result.data.messages[0].id == "1"
        assert result.data.messages[0].subject == "Test Email"
        assert result.data.total == 1
        assert result.component is not None
    
    def test_get_message(self):
        # Mock client response
        self.mock_client.get_message.return_value = {
            "id": "1",
            "subject": "Test Email",
            "from_email": {"email": "sender@example.com", "name": None},
            "to": [{"email": "recipient@example.com", "name": None}],
            "cc": [],
            "body": {"text": "Test body", "html": None},
            "attachments": [],
            "headers": [],
            "date": "Mon, 1 Jan 2023 12:00:00 +0000",
            "folder": "INBOX",
            "is_read": True
        }
        
        # Create params
        params = GetMessageParams(
            message_id="1",
            mark_as_read=True
        )
        
        # Call the service method
        result = self.service.get_message(params)
        
        # Verify results
        assert result.data.id == "1"
        assert result.data.subject == "Test Email"
        assert result.component is not None
    
    def test_send_message(self):
        # Mock client response
        self.mock_client.send_message.return_value = {
            "success": True,
            "message_id": "<test123@example.com>"
        }
        
        # Create params
        params = SendMessageParams(
            from_email={"email": "user@example.com", "name": "Test User"},
            to=[{"email": "recipient@example.com", "name": "Recipient"}],
            subject="Test Email",
            body_text="This is a test email",
            body_html="<p>This is a test email</p>"
        )
        
        # Call the service method
        result = self.service.send_message(params)
        
        # Verify results
        assert result.data.success == True
        assert result.data.message_id == "<test123@example.com>"
        assert result.component is not None 