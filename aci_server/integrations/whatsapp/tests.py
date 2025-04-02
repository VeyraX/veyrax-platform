import pytest
from datetime import datetime
from integrations.common.tests.base import base_setup
from unittest.mock import patch, MagicMock
import sys
import os

# Mock the auth.get_user_from_request function
@pytest.fixture
def mock_auth(monkeypatch):
    async def mock_get_user_from_request(*args, **kwargs):
        return "test_user"
    
    monkeypatch.setattr("integrations.common.auth.get_user_from_request", mock_get_user_from_request)

# Mock the WhatsApp library functions
@pytest.fixture
def mock_whatsapp(monkeypatch):
    # Create mock objects for WhatsApp functions
    mock_authenticate = MagicMock()
    mock_check_status = MagicMock()
    mock_send_message = MagicMock()
    mock_list_users = MagicMock()
    mock_list_chats = MagicMock()
    mock_list_messages = MagicMock()
    mock_search_contacts = MagicMock()
    mock_get_chat = MagicMock()
    mock_recent_messages = MagicMock()
    
    # Set up default return values
    mock_authenticate.return_value = MagicMock(
        user_id="test_user",
        is_logged_in=False,
        qr_data="1@test_qr_code",
        qr_image_base64="test_qr_image_base64",
        error=None
    )
    
    mock_check_status.return_value = MagicMock(
        user_id="test_user",
        is_logged_in=True,
        phone="+1234567890",
        error=None
    )
    
    mock_send_message.return_value = (True, "Message sent successfully")
    
    mock_list_users.return_value = [
        MagicMock(
            user_id="test_user1",
            is_logged_in=True,
            phone="+1234567890",
            error=None
        ),
        MagicMock(
            user_id="test_user2",
            is_logged_in=False,
            phone=None,
            error="Session expired"
        )
    ]
    
    mock_list_chats.return_value = [
        MagicMock(
            jid="123456789@s.whatsapp.net",
            name="Test User",
            last_message_time=datetime.now(),
            last_message="Hello",
            last_sender="123456789@s.whatsapp.net",
            last_is_from_me=False,
            is_group=False
        )
    ]
    
    mock_list_messages.return_value = [
        MagicMock(
            id="msg1",
            timestamp=datetime.now(),
            sender="Test User",
            content="Hello",
            is_from_me=False,
            chat_jid="123456789@s.whatsapp.net",
            chat_name="Test User"
        )
    ]
    
    mock_search_contacts.return_value = [
        MagicMock(
            phone_number="123456789",
            name="Test User",
            jid="123456789@s.whatsapp.net"
        )
    ]
    
    mock_get_chat.return_value = MagicMock(
        jid="123456789@s.whatsapp.net",
        name="Test User",
        last_message_time=datetime.now(),
        last_message="Hello",
        last_sender="123456789@s.whatsapp.net",
        last_is_from_me=False,
        is_group=False
    )
    
    mock_recent_messages.return_value = [
        MagicMock(
            id="msg1",
            timestamp=datetime.now(),
            sender="Test User",
            content="Hello",
            is_from_me=False,
            chat_jid="123456789@s.whatsapp.net",
            chat_name="Test User"
        )
    ]
    
    # Apply monkeypatches
    monkeypatch.setattr("integrations.whatsapp.client.authenticate_whatsapp_user", mock_authenticate)
    monkeypatch.setattr("integrations.whatsapp.client.check_whatsapp_status", mock_check_status)
    monkeypatch.setattr("integrations.whatsapp.client.send_message", mock_send_message)
    monkeypatch.setattr("integrations.whatsapp.client.list_whatsapp_users", mock_list_users)
    monkeypatch.setattr("integrations.whatsapp.client.list_chats", mock_list_chats)
    monkeypatch.setattr("integrations.whatsapp.client.list_messages", mock_list_messages)
    monkeypatch.setattr("integrations.whatsapp.client.search_contacts", mock_search_contacts)
    monkeypatch.setattr("integrations.whatsapp.client.get_chat", mock_get_chat)
    monkeypatch.setattr("integrations.whatsapp.client.print_recent_messages", mock_recent_messages)
    
    return {
        "authenticate": mock_authenticate,
        "check_status": mock_check_status,
        "send_message": mock_send_message,
        "list_users": mock_list_users,
        "list_chats": mock_list_chats,
        "list_messages": mock_list_messages,
        "search_contacts": mock_search_contacts,
        "get_chat": mock_get_chat,
        "recent_messages": mock_recent_messages
    }

def test_authenticate(base_setup, mock_whatsapp, mock_auth):
    """
    Test authentication endpoint
    """
    response = base_setup.post("/whatsapp/authenticate", payload={})
    
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}. Response: {response.text}"
    )
    
    data = response.json().get("data", {})
    
    assert data.get("user_id") == "test_user"
    assert "is_logged_in" in data
    assert "qr_data" in data or "error" in data
    
    mock_whatsapp["authenticate"].assert_called_once()

def test_check_status(base_setup, mock_whatsapp, mock_auth):
    """
    Test status check endpoint
    """
    response = base_setup.post("/whatsapp/check_status", payload={})
    
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}. Response: {response.text}"
    )
    
    data = response.json().get("data", {})
    
    assert data.get("user_id") == "test_user"
    assert "is_logged_in" in data
    
    mock_whatsapp["check_status"].assert_called_once()

def test_send_message(base_setup, mock_whatsapp, mock_auth):
    """
    Test sending a message
    """
    payload = {
        "recipient": "123456789@s.whatsapp.net",
        "message": "Hello, this is a test message!"
    }
    
    response = base_setup.post("/whatsapp/send_message", payload=payload)
    
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}. Response: {response.text}"
    )
    
    data = response.json().get("data", {})
    
    assert "success" in data
    assert "message" in data
    
    mock_whatsapp["send_message"].assert_called_once_with("test_user", "123456789@s.whatsapp.net", "Hello, this is a test message!")

def test_list_users(base_setup, mock_whatsapp, mock_auth):
    """
    Test listing users
    """
    response = base_setup.post("/whatsapp/list_users", payload={})
    
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}. Response: {response.text}"
    )
    
    data = response.json().get("data", {})
    
    assert "items" in data
    assert len(data["items"]) == 2
    
    mock_whatsapp["list_users"].assert_called_once()

def test_get_chats(base_setup, mock_whatsapp, mock_auth):
    """
    Test getting chats
    """
    payload = {
        "limit": 10,
        "page": 0
    }
    
    response = base_setup.post("/whatsapp/get_chats", payload=payload)
    
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}. Response: {response.text}"
    )
    
    data = response.json().get("data", {})
    
    assert "items" in data
    assert len(data["items"]) > 0
    
    mock_whatsapp["list_chats"].assert_called_once()

def test_get_messages(base_setup, mock_whatsapp, mock_auth):
    """
    Test getting messages
    """
    payload = {
        "chat_jid": "123456789@s.whatsapp.net",
        "limit": 20,
        "page": 0
    }
    
    response = base_setup.post("/whatsapp/get_messages", payload=payload)
    
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}. Response: {response.text}"
    )
    
    data = response.json().get("data", {})
    
    assert "items" in data
    assert len(data["items"]) > 0
    
    mock_whatsapp["list_messages"].assert_called_once()

def test_search_contacts(base_setup, mock_whatsapp, mock_auth):
    """
    Test searching contacts
    """
    payload = {
        "query": "Test"
    }
    
    response = base_setup.post("/whatsapp/search_contacts", payload=payload)
    
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}. Response: {response.text}"
    )
    
    data = response.json().get("data", {})
    
    assert "items" in data
    assert len(data["items"]) > 0
    
    mock_whatsapp["search_contacts"].assert_called_once()

def test_get_chat(base_setup, mock_whatsapp, mock_auth):
    """
    Test getting a single chat
    """
    payload = {
        "chat_jid": "123456789@s.whatsapp.net"
    }
    
    response = base_setup.post("/whatsapp/get_chat", payload=payload)
    
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}. Response: {response.text}"
    )
    
    data = response.json().get("data", {})
    
    assert data.get("jid") == "123456789@s.whatsapp.net"
    
    mock_whatsapp["get_chat"].assert_called_once()

def test_get_recent_messages(base_setup, mock_whatsapp, mock_auth):
    """
    Test getting recent messages
    """
    payload = {
        "limit": 5
    }
    
    response = base_setup.post("/whatsapp/get_recent_messages", payload=payload)
    
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}. Response: {response.text}"
    )
    
    data = response.json().get("data", {})
    
    assert "items" in data
    assert len(data["items"]) > 0
    
    mock_whatsapp["recent_messages"].assert_called_once()

def test_validate_user(base_setup, mock_whatsapp, mock_auth):
    """
    Test validating a user
    """
    response = base_setup.post("/whatsapp/validate_user", payload={})
    
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}. Response: {response.text}"
    )
    
    data = response.json()
    
    assert "valid" in data
    assert "message" in data
    
    mock_whatsapp["check_status"].assert_called_once() 