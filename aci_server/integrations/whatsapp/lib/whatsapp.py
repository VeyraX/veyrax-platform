import sqlite3
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, List, Tuple, Dict
import os
import os.path
import requests
import json
import base64
from io import BytesIO

# Use environment variable for the API base URL with fallback
WHATSAPP_API_BASE_URL = os.environ.get("WHATSAPP_API_BASE_URL", "http://localhost:8080/api")
# Default timeout for API requests (in seconds)
DEFAULT_TIMEOUT = 15

@dataclass
class Message:
    timestamp: datetime
    sender: str
    content: str
    is_from_me: bool
    chat_jid: str
    id: str
    chat_name: Optional[str] = None

@dataclass
class Chat:
    jid: str
    name: Optional[str]
    last_message_time: Optional[datetime]
    last_message: Optional[str] = None
    last_sender: Optional[str] = None
    last_is_from_me: Optional[bool] = None

    @property
    def is_group(self) -> bool:
        """Determine if chat is a group based on JID pattern."""
        return self.jid.endswith("@g.us")

@dataclass
class Contact:
    phone_number: str
    name: Optional[str]
    jid: str

@dataclass
class MessageContext:
    message: Message
    before: List[Message]
    after: List[Message]

@dataclass
class WhatsAppSession:
    user_id: str
    is_logged_in: bool
    qr_data: Optional[str] = None
    qr_image_ascii: Optional[str] = None
    phone: Optional[str] = None
    error: Optional[str] = None

def get_messages_db_path(user_id: str) -> str:
    """Get the database path for a specific user"""
    base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'whatsapp-bridge', 'store')
    user_dir = os.path.join(base_path, user_id)
    db_path = os.path.join(user_dir, 'messages.db')
    print('[get_messages_db_path]', db_path)
    return db_path

def print_message(message: Message, show_chat_info: bool = True) -> None:
    """Print a single message with consistent formatting."""
    direction = "→" if message.is_from_me else "←"
    
    if show_chat_info and message.chat_name:
        print(f"[{message.timestamp:%Y-%m-%d %H:%M:%S}] {direction} Chat: {message.chat_name} ({message.chat_jid})")
    else:
        print(f"[{message.timestamp:%Y-%m-%d %H:%M:%S}] {direction}")
        
    print(f"From: {'Me' if message.is_from_me else message.sender}")
    print(f"Message: {message.content}")
    print("-" * 100)

def print_messages_list(messages: List[Message], title: str = "", show_chat_info: bool = True) -> None:
    """Print a list of messages with a title and consistent formatting."""
    if not messages:
        print("No messages to display.")
        return
        
    if title:
        print(f"\n{title}")
        print("-" * 100)
    
    for message in messages:
        print_message(message, show_chat_info)

def print_chat(chat: Chat) -> None:
    """Print a single chat with consistent formatting."""
    print(f"Chat: {chat.name} ({chat.jid})")
    if chat.last_message_time:
        print(f"Last active: {chat.last_message_time:%Y-%m-%d %H:%M:%S}")
        direction = "→" if chat.last_is_from_me else "←"
        sender = "Me" if chat.last_is_from_me else chat.last_sender
        print(f"Last message: {direction} {sender}: {chat.last_message}")
    print("-" * 100)

def print_chats_list(chats: List[Chat], title: str = "") -> None:
    """Print a list of chats with a title and consistent formatting."""
    if not chats:
        print("No chats to display.")
        return
        
    if title:
        print(f"\n{title}")
        print("-" * 100)
    
    for chat in chats:
        print_chat(chat)

def print_paginated_messages(messages: List[Message], page: int, total_pages: int, chat_name: str) -> None:
    """Print a paginated list of messages with navigation hints."""
    print(f"\nMessages for chat: {chat_name}")
    print(f"Page {page} of {total_pages}")
    print("-" * 100)
    
    print_messages_list(messages, show_chat_info=False)
    
    # Print pagination info
    if page > 1:
        print(f"Use page={page-1} to see newer messages")
    if page < total_pages:
        print(f"Use page={page+1} to see older messages")

"""
CREATE TABLE messages (
			id TEXT,
			chat_jid TEXT,
			sender TEXT,
			content TEXT,
			timestamp TIMESTAMP,
			is_from_me BOOLEAN,
			PRIMARY KEY (id, chat_jid),
			FOREIGN KEY (chat_jid) REFERENCES chats(jid)
		)

CREATE TABLE chats (
			jid TEXT PRIMARY KEY,
			name TEXT,
			last_message_time TIMESTAMP
		)
"""

def authenticate_whatsapp_user(user_id: str, timeout: int = DEFAULT_TIMEOUT) -> WhatsAppSession:
    """Authenticate WhatsApp for a user, returns QR code data if needed"""
    try:
        url = f"{WHATSAPP_API_BASE_URL}/auth"
        response = requests.post(url, json={"user_id": user_id}, timeout=timeout)
        
        if response.status_code == 200:
            data = response.json()
            return WhatsAppSession(
                user_id=user_id,
                is_logged_in=data.get("is_logged_in", False),
                qr_data=data.get("qr_string"),
                qr_image_ascii=data.get("qr_image_base64"),
                error=None
            )
        else:
            return WhatsAppSession(
                user_id=user_id,
                is_logged_in=False,
                error=f"Error: HTTP {response.status_code} - {response.text}"
            )
    except requests.RequestException as e:
        return WhatsAppSession(
            user_id=user_id,
            is_logged_in=False,
            error=f"Request error: {str(e)}"
        )

def check_whatsapp_status(user_id: str, timeout: int = DEFAULT_TIMEOUT) -> WhatsAppSession:
    """Check status of a WhatsApp user"""
    try:
        url = f"{WHATSAPP_API_BASE_URL}/status?user_id={user_id}"
        response = requests.get(url, timeout=timeout)
        
        if response.status_code == 200:
            data = response.json()
            return WhatsAppSession(
                user_id=user_id,
                is_logged_in=data.get("logged_in", False),
                phone=data.get("phone"),
                error=None
            )
        else:
            return WhatsAppSession(
                user_id=user_id,
                is_logged_in=False,
                error=f"Error: HTTP {response.status_code} - {response.text}"
            )
    except requests.RequestException as e:
        return WhatsAppSession(
            user_id=user_id,
            is_logged_in=False,
            error=f"Request error: {str(e)}"
        )

def list_whatsapp_users(timeout: int = DEFAULT_TIMEOUT) -> List[WhatsAppSession]:
    """List all active WhatsApp users"""
    try:
        url = f"{WHATSAPP_API_BASE_URL}/users"
        response = requests.get(url, timeout=timeout)
        
        if response.status_code == 200:
            data = response.json()
            return [
                WhatsAppSession(
                    user_id=user.get("user_id", ""),
                    is_logged_in=user.get("logged_in", False),
                    phone=user.get("phone"),
                    error=None
                )
                for user in data.get("users", [])
            ]
        else:
            return []
    except requests.RequestException:
        return []

def print_recent_messages(user_id: str, limit=10, timeout: int = DEFAULT_TIMEOUT) -> List[Message]:
    """Get recent messages for a user"""
    try:
        url = f"{WHATSAPP_API_BASE_URL}/messages/recent?user_id={user_id}&limit={limit}"
        response = requests.get(url, timeout=timeout)
        
        if response.status_code != 200:
            print(f"Error fetching recent messages: HTTP {response.status_code} - {response.text}")
            return []
            
        data = response.json()
        messages = data.get("items", [])
        
        if not messages:
            print("No messages found.")
            return []
            
        result = []
        
        # Convert to Message objects
        for msg in messages:
            message = Message(
                timestamp=datetime.fromisoformat(msg.get("timestamp")),
                sender=msg.get("sender"),
                chat_name=msg.get("chat_name", "Unknown Chat"),
                content=msg.get("content", ""),
                is_from_me=msg.get("is_from_me", False),
                chat_jid=msg.get("chat_jid", ""),
                id=msg.get("id", "")
            )
            result.append(message)
        
        # Print messages using helper function
        print_messages_list(result, title=f"Last {limit} messages for {user_id}:")
        return result
            
    except requests.RequestException as e:
        print(f"Request error: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []


def list_messages(
    user_id: str,
    date_range: Optional[Tuple[datetime, datetime]] = None,
    sender_phone_number: Optional[str] = None,
    chat_jid: Optional[str] = None,
    query: Optional[str] = None,
    limit: int = 20,
    page: int = 0,
    include_context: bool = True,
    context_before: int = 1,
    context_after: int = 1,
    timeout: int = DEFAULT_TIMEOUT
) -> List[Message]:
    """Get messages matching the specified criteria with optional context."""
    try:
        # Build URL with query parameters
        url = f"{WHATSAPP_API_BASE_URL}/messages/list?user_id={user_id}&limit={limit}&page={page}"
        
        if date_range:
            url += f"&start_date={date_range[0].isoformat()}&end_date={date_range[1].isoformat()}"
            
        if sender_phone_number:
            url += f"&sender_phone_number={sender_phone_number}"
            
        if chat_jid:
            url += f"&chat_jid={chat_jid}"
            
        if query:
            url += f"&query={query}"
            
        url += f"&include_context={'true' if include_context else 'false'}"
        url += f"&context_before={context_before}&context_after={context_after}"
        
        # Make API request
        response = requests.get(url, timeout=timeout)
        
        if response.status_code != 200:
            print(f"Error fetching messages: HTTP {response.status_code} - {response.text}")
            return []
            
        data = response.json()
        messages = data.get("items", [])
        
        result = []
        for msg in messages:
            message = Message(
                timestamp=datetime.fromisoformat(msg.get("timestamp")),
                sender=msg.get("sender"),
                chat_name=msg.get("chat_name", "Unknown Chat"),
                content=msg.get("content", ""),
                is_from_me=msg.get("is_from_me", False),
                chat_jid=msg.get("chat_jid", ""),
                id=msg.get("id", "")
            )
            result.append(message)
            
        return result
        
    except requests.RequestException as e:
        print(f"Request error: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []


def get_message_context(
    user_id: str,
    message_id: str,
    before: int = 5,
    after: int = 5,
    timeout: int = DEFAULT_TIMEOUT
) -> MessageContext:
    """Get context around a specific message."""
    try:
        url = f"{WHATSAPP_API_BASE_URL}/messages/context?user_id={user_id}&message_id={message_id}&before={before}&after={after}"
        
        response = requests.get(url, timeout=timeout)
        
        if response.status_code != 200:
            raise ValueError(f"Error fetching message context: HTTP {response.status_code} - {response.text}")
            
        data = response.json()
        messages = data.get("items", [])
        
        if not messages:
            raise ValueError(f"Message with ID {message_id} not found")
            
        # The first message is the target message
        target_message = None
        before_messages = []
        after_messages = []
        found_target = False
        
        for msg in messages:
            message = Message(
                timestamp=datetime.fromisoformat(msg.get("timestamp")),
                sender=msg.get("sender"),
                chat_name=msg.get("chat_name", "Unknown Chat"),
                content=msg.get("content", ""),
                is_from_me=msg.get("is_from_me", False),
                chat_jid=msg.get("chat_jid", ""),
                id=msg.get("id", "")
            )
            
            # Check if this is the target message
            if message.id == message_id:
                target_message = message
                found_target = True
            elif not found_target:
                before_messages.append(message)
            else:
                after_messages.append(message)
        
        if not target_message:
            # If we didn't find the target message, use the middle message
            middle_idx = len(messages) // 2
            target_message = Message(
                timestamp=datetime.fromisoformat(messages[middle_idx].get("timestamp")),
                sender=messages[middle_idx].get("sender"),
                chat_name=messages[middle_idx].get("chat_name", "Unknown Chat"),
                content=messages[middle_idx].get("content", ""),
                is_from_me=messages[middle_idx].get("is_from_me", False),
                chat_jid=messages[middle_idx].get("chat_jid", ""),
                id=messages[middle_idx].get("id", "")
            )
            before_messages = messages[:middle_idx]
            after_messages = messages[middle_idx+1:]
        
        return MessageContext(
            message=target_message,
            before=before_messages,
            after=after_messages
        )
        
    except requests.RequestException as e:
        print(f"Request error: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise


def list_chats(
    user_id: str,
    query: Optional[str] = None,
    limit: int = 20,
    page: int = 0,
    include_last_message: bool = True,
    sort_by: str = "last_active",
    timeout: int = DEFAULT_TIMEOUT
) -> List[Chat]:
    """Get chats matching the specified criteria."""
    try:
        # Build URL with query parameters
        url = f"{WHATSAPP_API_BASE_URL}/chats/list?user_id={user_id}&limit={limit}&page={page}"
        
        if query:
            url += f"&query={query}"
            
        url += f"&include_last_message={'true' if include_last_message else 'false'}"
        url += f"&sort_by={sort_by}"
        
        # Make API request
        response = requests.get(url, timeout=timeout)
        
        if response.status_code != 200:
            print(f"Error fetching chats: HTTP {response.status_code} - {response.text}")
            return []
            
        data = response.json()
        chats_data = data.get("items", [])
        
        result = []
        for chat_data in chats_data:
            chat = Chat(
                jid=chat_data.get("jid", ""),
                name=chat_data.get("name"),
                last_message_time=datetime.fromisoformat(chat_data.get("last_message_time")) if chat_data.get("last_message_time") else None,
                last_message=chat_data.get("last_message"),
                last_sender=chat_data.get("last_sender"),
                last_is_from_me=chat_data.get("last_is_from_me")
            )
            result.append(chat)
            
        return result
        
    except requests.RequestException as e:
        print(f"Request error: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []


def search_contacts(user_id: str, query: str, timeout: int = DEFAULT_TIMEOUT) -> List[Contact]:
    """Search contacts by name or phone number."""
    try:
        url = f"{WHATSAPP_API_BASE_URL}/contacts/search?user_id={user_id}&query={query}"
        
        response = requests.get(url, timeout=timeout)
        
        if response.status_code != 200:
            print(f"Error searching contacts: HTTP {response.status_code} - {response.text}")
            return []
            
        data = response.json()
        contacts_data = data.get("items", [])
        
        result = []
        for contact_data in contacts_data:
            contact = Contact(
                phone_number=contact_data.get("phone_number", ""),
                name=contact_data.get("name"),
                jid=contact_data.get("jid", "")
            )
            result.append(contact)
            
        return result
        
    except requests.RequestException as e:
        print(f"Request error: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []


def get_contact_chats(user_id: str, jid: str, limit: int = 20, page: int = 0, timeout: int = DEFAULT_TIMEOUT) -> List[Chat]:
    """Get all chats involving the contact.
    
    Args:
        user_id: The user ID whose chats to search
        jid: The contact's JID to search for
        limit: Maximum number of chats to return (default 20)
        page: Page number for pagination (default 0)
    """
    try:
        url = f"{WHATSAPP_API_BASE_URL}/contacts/chats?user_id={user_id}&jid={jid}&limit={limit}&page={page}"
        
        response = requests.get(url, timeout=timeout)
        
        if response.status_code != 200:
            print(f"Error getting contact chats: HTTP {response.status_code} - {response.text}")
            return []
            
        data = response.json()
        chats_data = data.get("items", [])
        
        result = []
        for chat_data in chats_data:
            chat = Chat(
                jid=chat_data.get("jid", ""),
                name=chat_data.get("name"),
                last_message_time=datetime.fromisoformat(chat_data.get("last_message_time")) if chat_data.get("last_message_time") else None,
                last_message=chat_data.get("last_message"),
                last_sender=chat_data.get("last_sender"),
                last_is_from_me=chat_data.get("last_is_from_me")
            )
            result.append(chat)
            
        return result
        
    except requests.RequestException as e:
        print(f"Request error: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []


def get_last_interaction(user_id: str, jid: str, timeout: int = DEFAULT_TIMEOUT) -> Optional[Message]:
    """Get most recent message involving the contact."""
    try:
        url = f"{WHATSAPP_API_BASE_URL}/contacts/last-interaction?user_id={user_id}&jid={jid}"
        
        response = requests.get(url, timeout=timeout)
        
        if response.status_code == 404:
            return None
        
        if response.status_code != 200:
            print(f"Error getting last interaction: HTTP {response.status_code} - {response.text}")
            return None
            
        msg_data = response.json()
        
        return Message(
            timestamp=datetime.fromisoformat(msg_data.get("timestamp")),
            sender=msg_data.get("sender"),
            chat_name=msg_data.get("chat_name"),
            content=msg_data.get("content", ""),
            is_from_me=msg_data.get("is_from_me", False),
            chat_jid=msg_data.get("chat_jid", ""),
            id=msg_data.get("id", "")
        )
        
    except requests.RequestException as e:
        print(f"Request error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


def get_chat(user_id: str, chat_jid: str, include_last_message: bool = True, timeout: int = DEFAULT_TIMEOUT) -> Optional[Chat]:
    """Get chat metadata by JID."""
    try:
        url = f"{WHATSAPP_API_BASE_URL}/chats/get?user_id={user_id}&chat_jid={chat_jid}&include_last_message={'true' if include_last_message else 'false'}"
        
        response = requests.get(url, timeout=timeout)
        
        if response.status_code == 404:
            return None
        
        if response.status_code != 200:
            print(f"Error getting chat: HTTP {response.status_code} - {response.text}")
            return None
            
        chat_data = response.json()
        
        return Chat(
            jid=chat_data.get("jid", ""),
            name=chat_data.get("name"),
            last_message_time=datetime.fromisoformat(chat_data.get("last_message_time")) if chat_data.get("last_message_time") else None,
            last_message=chat_data.get("last_message"),
            last_sender=chat_data.get("last_sender"),
            last_is_from_me=chat_data.get("last_is_from_me")
        )
        
    except requests.RequestException as e:
        print(f"Request error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


def get_direct_chat_by_contact(user_id: str, sender_phone_number: str, timeout: int = DEFAULT_TIMEOUT) -> Optional[Chat]:
    """Get chat metadata by sender phone number."""
    try:
        url = f"{WHATSAPP_API_BASE_URL}/chats/get-by-contact?user_id={user_id}&phone_number={sender_phone_number}"
        
        response = requests.get(url, timeout=timeout)
        
        if response.status_code == 404:
            return None
        
        if response.status_code != 200:
            print(f"Error getting chat by contact: HTTP {response.status_code} - {response.text}")
            return None
            
        chat_data = response.json()
        
        return Chat(
            jid=chat_data.get("jid", ""),
            name=chat_data.get("name"),
            last_message_time=datetime.fromisoformat(chat_data.get("last_message_time")) if chat_data.get("last_message_time") else None,
            last_message=chat_data.get("last_message"),
            last_sender=chat_data.get("last_sender"),
            last_is_from_me=chat_data.get("last_is_from_me")
        )
        
    except requests.RequestException as e:
        print(f"Request error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def send_message(user_id: str, recipient: str, message: str, timeout: int = DEFAULT_TIMEOUT) -> Tuple[bool, str]:
    """Send a WhatsApp message to the specified recipient. For group messages use the JID.
    
    Args:
        user_id: The user ID to send the message as
        recipient: The recipient - either a phone number with country code but no + or other symbols,
                  or a JID (e.g., "123456789@s.whatsapp.net" or a group JID like "123456789@g.us").
        message: The message text to send
        
    Returns:
        Tuple[bool, str]: A tuple containing success status and a status message
    """
    try:
        # Validate input
        if not user_id or not recipient:
            return False, "User ID and recipient must be provided"
        
        url = f"{WHATSAPP_API_BASE_URL}/send"
        payload = {
            "user_id": user_id,
            "recipient": recipient,
            "message": message
        }
        
        response = requests.post(url, json=payload, timeout=timeout)
        
        # Check if the request was successful
        if response.status_code == 200:
            result = response.json()
            return result.get("success", False), result.get("message", "Unknown response")
        else:
            return False, f"Error: HTTP {response.status_code} - {response.text}"
            
    except requests.RequestException as e:
        return False, f"Request error: {str(e)}"
    except json.JSONDecodeError:
        return False, f"Error parsing response: {response.text}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

def disconnect_whatsapp_user(user_id: str, timeout: int = DEFAULT_TIMEOUT) -> Tuple[bool, str]:
    """Disconnect a WhatsApp user and delete their data.
    
    Args:
        user_id: The user ID to disconnect
        timeout: Request timeout in seconds
        
    Returns:
        Tuple[bool, str]: A tuple containing success status and a status message
    """
    try:
        url = f"{WHATSAPP_API_BASE_URL}/disconnect"
        payload = {
            "user_id": user_id
        }
        
        response = requests.post(url, json=payload, timeout=timeout)
        
        # Check if the request was successful
        if response.status_code == 200:
            result = response.json()
            return result.get("success", False), result.get("message", "Unknown response")
        else:
            return False, f"Error: HTTP {response.status_code} - {response.text}"
            
    except requests.RequestException as e:
        return False, f"Request error: {str(e)}"
    except json.JSONDecodeError:
        return False, f"Error parsing response: {response.text}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"
