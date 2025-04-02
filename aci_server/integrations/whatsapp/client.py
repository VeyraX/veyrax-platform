import requests
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from .lib.whatsapp import (
    authenticate_whatsapp_user,
    check_whatsapp_status,
    send_message,
    list_whatsapp_users,
    list_chats,
    list_messages,
    search_contacts,
    get_chat,
    print_recent_messages,
    WhatsAppSession,
    disconnect_whatsapp_user
)

class WhatsAppClient:
    def __init__(self, user_id: str):
        self.user_id = user_id
        
    def authenticate(self) -> WhatsAppSession:
        """Authenticate WhatsApp for a user, returns QR code data if needed"""
        return authenticate_whatsapp_user(self.user_id)
        
    def check_status(self) -> WhatsAppSession:
        """Check status of a WhatsApp user"""
        return check_whatsapp_status(self.user_id)
        
    def send_message(self, recipient: str, message: str) -> Tuple[bool, str]:
        """Send a WhatsApp message to the specified recipient"""
        return send_message(self.user_id, recipient, message)
        
    def list_users(self) -> List[WhatsAppSession]:
        """List all active WhatsApp users"""
        return list_whatsapp_users()
        
    def get_chats(self, query: Optional[str] = None, limit: int = 20, 
                  page: int = 0, include_last_message: bool = True, 
                  sort_by: str = "last_active") -> Any:
        """Get chats matching the specified criteria"""
        return list_chats(
            self.user_id, 
            query=query, 
            limit=limit, 
            page=page, 
            include_last_message=include_last_message, 
            sort_by=sort_by
        )
        
    def get_messages(self, chat_jid: Optional[str] = None, 
                    query: Optional[str] = None, limit: int = 20, 
                    page: int = 0, include_context: bool = True,
                    sender_phone_number: Optional[str] = None,
                    date_range: Optional[Tuple[datetime, datetime]] = None) -> Any:
        """Get messages matching the specified criteria"""
        return list_messages(
            self.user_id,
            chat_jid=chat_jid,
            query=query,
            limit=limit,
            page=page,
            include_context=include_context,
            sender_phone_number=sender_phone_number,
            date_range=date_range
        )
        
    def get_contacts(self, query: str) -> Any:
        """Search contacts by name or phone number"""
        return search_contacts(self.user_id, query)
        
    def get_chat(self, chat_jid: str, include_last_message: bool = True) -> Any:
        """Get chat metadata by JID"""
        return get_chat(self.user_id, chat_jid, include_last_message)
        
    def get_recent_messages(self, limit: int = 10) -> Any:
        """Get recent messages for a user"""
        return print_recent_messages(self.user_id, limit)
        
    def disconnect(self) -> Tuple[bool, str]:
        """Disconnect the user from WhatsApp and delete their data"""
        return disconnect_whatsapp_user(self.user_id) 