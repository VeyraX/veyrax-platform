import smtplib
import imaplib
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.utils import formatdate, make_msgid, parseaddr
from email.header import decode_header
import base64
import re
import time
from typing import Dict, Any, List, Optional, Union, Tuple
import os
import uuid
from datetime import datetime, timedelta
import socket

class MailSMTPError(Exception):
    def __init__(self, message, errors=None):
        self.message = message
        self.errors = errors
        super().__init__(self.message)

class MailSMTPClient:
    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        imap_host: str,
        imap_port: int,
        username: str,
        password: str,
        use_ssl: bool = True,
        use_tls: bool = False,
        imap_use_ssl: bool = True
    ):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.imap_host = imap_host
        self.imap_port = imap_port
        self.username = username
        self.password = password
        self.use_ssl = use_ssl
        self.use_tls = use_tls
        self.imap_use_ssl = imap_use_ssl
        
        self._test_connections()
    
    def _test_connections(self):
        """Test both SMTP and IMAP connections, handling each separately."""
        smtp_error = None
        imap_error = None
        
        try:
            smtp_conn = self._get_smtp_connection()
            smtp_conn.quit()
        except Exception as e:
            smtp_error = e
        
        try:
            imap_conn = self._get_imap_connection()
            try:
                imap_conn.logout()
            except Exception as logout_error:
                # Log but ignore errors during logout as we've already verified the connection works
                # This happens with some Gmail IMAP servers that return unexpected responses on logout
                pass
        except Exception as e:
            imap_error = e
        
        if smtp_error and imap_error:
            raise MailSMTPError(
                f"Failed to connect to mail servers. SMTP: {str(smtp_error)}, IMAP: {str(imap_error)}"
            )
        elif smtp_error:
            raise MailSMTPError(f"Failed to connect to SMTP server: {str(smtp_error)}")
        elif imap_error:
            raise MailSMTPError(f"Failed to connect to IMAP server: {str(imap_error)}")
            
    
    def _get_smtp_connection(self):
        try:
            if self.use_ssl and not self.use_tls:
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)
            else:
                server = smtplib.SMTP(self.smtp_host, self.smtp_port)
                if self.use_tls:
                    server.starttls()
            
            # # Set debug level to see detailed connection information
            # server.set_debuglevel(1)
            
            try:
                server.login(self.username, self.password)
            except smtplib.SMTPAuthenticationError as auth_error:
                # Handle authentication errors specifically
                if "Application-specific password required" in str(auth_error):
                    raise MailSMTPError(
                        "Gmail authentication failed. If you have 2-Factor Authentication enabled, "
                        "you need to use an App Password instead of your regular password. "
                        "Go to your Google Account -> Security -> App Passwords to generate one."
                    )
                elif "Username and Password not accepted" in str(auth_error):
                    raise MailSMTPError(
                        "Login credentials rejected. Please verify your email and password. "
                        "For Gmail, make sure 'Less secure app access' is enabled or use an App Password."
                    )
                else:
                    raise MailSMTPError(f"SMTP Authentication Error: {str(auth_error)}")
            
            return server
        except smtplib.SMTPConnectError as e:
            raise MailSMTPError(f"Failed to connect to SMTP server: {str(e)}")
        except smtplib.SMTPServerDisconnected as e:
            raise MailSMTPError(f"SMTP server disconnected: {str(e)}")
        except smtplib.SMTPException as e:
            raise MailSMTPError(f"SMTP Error: {str(e)}")
        except Exception as e:
            raise MailSMTPError(f"SMTP Connection Error: {str(e)}")
    
    def _get_imap_connection(self):
        try:
            # Use imap_use_ssl instead of use_ssl for IMAP connection
            if self.imap_use_ssl:
                server = imaplib.IMAP4_SSL(self.imap_host, self.imap_port, timeout=30)
            else:
                server = imaplib.IMAP4(self.imap_host, self.imap_port, timeout=30)
                if self.use_tls:
                    server.starttls()
            
            try:
                server.login(self.username, self.password)
            except imaplib.IMAP4.error as auth_error:
                # Handle authentication errors specifically for IMAP
                error_str = str(auth_error)
                if "AUTHENTICATIONFAILED" in error_str:
                    if "gmail" in self.imap_host.lower():
                        raise MailSMTPError(
                            "Gmail IMAP authentication failed. Check your credentials. "
                            "If you have 2-Factor Authentication enabled, "
                            "you need to use an App Password instead of your regular password."
                        )
                    else:
                        raise MailSMTPError(f"IMAP Authentication failed: {error_str}")
                else:
                    raise MailSMTPError(f"IMAP Error: {error_str}")
                
            return server
        except ConnectionRefusedError:
            raise MailSMTPError(f"IMAP Connection refused to {self.imap_host}:{self.imap_port}")
        except socket.timeout:
            raise MailSMTPError(f"IMAP Connection timeout to {self.imap_host}:{self.imap_port}")
        except socket.gaierror as e:
            raise MailSMTPError(f"IMAP DNS resolution error: {str(e)}")
        except socket.error as e:
            raise MailSMTPError(f"IMAP Socket error: {str(e)}")
        except imaplib.IMAP4.error as e:
            raise MailSMTPError(f"IMAP Protocol error: {str(e)}")
        except Exception as e:
            raise MailSMTPError(f"IMAP Connection Error: {str(e)}")
    
    def _decode_mime_words(self, text: str) -> str:
        try:
            if not text:
                return ""
            
            decoded_parts = []
            for part, encoding in decode_header(text):
                if isinstance(part, bytes):
                    if encoding:
                        try:
                            decoded_parts.append(part.decode(encoding, errors='replace'))
                        except LookupError:
                            decoded_parts.append(part.decode('utf-8', errors='replace'))
                    else:
                        decoded_parts.append(part.decode('utf-8', errors='replace'))
                else:
                    decoded_parts.append(part)
            return ' '.join(decoded_parts)
        except Exception as e:
            return text
    
    def _parse_address(self, address: str) -> Dict[str, Optional[str]]:
        if not address:
            return {"email": None, "name": None}
        
        name, email = parseaddr(address)
        if not email:
            # Try to extract email if parsing failed
            match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', address)
            if match:
                email = match.group(0)
        
        return {
            "email": email,
            "name": self._decode_mime_words(name) if name else None
        }
    
    def _parse_addresses(self, addresses: Union[str, List[str]]) -> List[Dict[str, Optional[str]]]:
        if not addresses:
            return []
        
        if isinstance(addresses, str):
            return [self._parse_address(addresses)]
        
        parsed = []
        for addr in addresses:
            parsed.append(self._parse_address(addr))
        
        return parsed
    
    def _parse_email_message(self, msg, folder: str = 'INBOX', mark_as_read: bool = False) -> Dict[str, Any]:
        # Basic message info
        message_id = msg.get('Message-ID', str(uuid.uuid4()))
        if not message_id:
            message_id = str(uuid.uuid4())
        
        # Parse date
        date_str = msg.get('Date')
        try:
            if date_str:
                # Try to parse with email.utils
                date_tuple = email.utils.parsedate_tz(date_str)
                if date_tuple:
                    date = email.utils.formatdate(
                        email.utils.mktime_tz(date_tuple),
                        localtime=False,
                        usegmt=True
                    )
                else:
                    date = date_str
            else:
                date = formatdate(localtime=False, usegmt=True)
        except Exception:
            date = date_str if date_str else formatdate(localtime=False, usegmt=True)
        
        # Get subject
        subject = self._decode_mime_words(msg.get('Subject', '(No Subject)'))
        
        # Parse addresses
        from_email = self._parse_address(msg.get('From', ''))
        to = self._parse_addresses(msg.get_all('To', []))
        cc = self._parse_addresses(msg.get_all('Cc', []))
        bcc = self._parse_addresses(msg.get_all('Bcc', []))
        
        # Extract body
        body = {"text": None, "html": None}
        attachments = []
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition", ""))
                
                # Skip attachments in the first pass (we'll process them later)
                if "attachment" in content_disposition:
                    filename = part.get_filename()
                    if filename:
                        # Decode filename if needed
                        try:
                            filename = self._decode_mime_words(filename)
                        except Exception:
                            pass
                        
                        # Get content
                        content = part.get_payload(decode=True)
                        if content:
                            # Create a proper attachment object
                            attachments.append({
                                "filename": filename,
                                "content_type": content_type,
                                "size": len(content),
                                "content": base64.b64encode(content).decode('utf-8')
                            })
                elif content_type == "text/plain" and not body["text"]:
                    try:
                        payload = part.get_payload(decode=True)
                        if payload:
                            charset = part.get_content_charset() or 'utf-8'
                            body["text"] = payload.decode(charset, errors='replace')
                    except Exception as e:
                        body["text"] = f"[Error decoding plain text: {str(e)}]"
                
                elif content_type == "text/html" and not body["html"]:
                    try:
                        payload = part.get_payload(decode=True)
                        if payload:
                            charset = part.get_content_charset() or 'utf-8'
                            body["html"] = payload.decode(charset, errors='replace')
                    except Exception as e:
                        body["html"] = f"[Error decoding HTML: {str(e)}]"
        else:
            # Not multipart - get the content directly
            content_type = msg.get_content_type()
            try:
                payload = msg.get_payload(decode=True)
                if payload:
                    charset = msg.get_content_charset() or 'utf-8'
                    if content_type == 'text/html':
                        body["html"] = payload.decode(charset, errors='replace')
                    else:
                        body["text"] = payload.decode(charset, errors='replace')
            except Exception as e:
                body["text"] = f"[Error decoding message: {str(e)}]"
        
        # Extract headers
        headers = []
        for name, value in msg.items():
            if name.lower() not in ['from', 'to', 'cc', 'bcc', 'subject', 'date', 'message-id']:
                headers.append({
                    "name": name,
                    "value": self._decode_mime_words(value)
                })
        
        # Construct the message object
        email_message = {
            "id": message_id.strip('<>'),
            "subject": subject,
            "from_email": from_email,
            "to": to,
            "cc": cc,
            "bcc": bcc,
            "body": body,
            "attachments": attachments,
            "headers": headers,
            "date": date,
            "folder": folder,
            "is_read": mark_as_read
        }
        
        return email_message
    
    def get_messages(
        self, 
        folder: str = 'INBOX',
        limit: int = 20,
        offset: int = 0,
        search_query: Optional[str] = None,
        mark_as_read: bool = False,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get messages from a specific folder.
        
        Args:
            folder: Mailbox folder to fetch from
            limit: Maximum number of messages to return
            offset: Number of messages to skip
            search_query: Optional text to search in subject or from fields
            mark_as_read: Whether to mark fetched messages as read
            from_date: Optional start date filter in format YYYY-MM-DD
            to_date: Optional end date filter in format YYYY-MM-DD
        """
        try:
            imap = self._get_imap_connection()
            
            # Select the folder
            result, data = imap.select(f'"{folder}"', readonly=not mark_as_read)
            if result != 'OK':
                raise MailSMTPError(f"Failed to select folder '{folder}': {data[0].decode()}")
            
            # Get total message count
            total_messages = int(data[0])
            
            # Build search criteria
            search_criteria_list = []
            
            # Add text search if provided
            if search_query:
                search_criteria_list.append(f'(OR SUBJECT "{search_query}" FROM "{search_query}")')
            
            # Add date filters if provided
            if from_date:
                try:
                    # Convert YYYY-MM-DD to DD-MMM-YYYY format required by IMAP
                    parsed_date = datetime.strptime(from_date, "%Y-%m-%d")
                    formatted_date = parsed_date.strftime("%d-%b-%Y")
                    search_criteria_list.append(f'(SINCE "{formatted_date}")')
                except ValueError:
                    # If date parsing fails, ignore the filter
                    pass
            
            if to_date:
                try:
                    # Convert YYYY-MM-DD to DD-MMM-YYYY format required by IMAP
                    # Add one day to make the search inclusive of the to_date
                    parsed_date = datetime.strptime(to_date, "%Y-%m-%d")
                    next_day = parsed_date + timedelta(days=1)
                    formatted_date = next_day.strftime("%d-%b-%Y")
                    search_criteria_list.append(f'(BEFORE "{formatted_date}")')
                except ValueError:
                    # If date parsing fails, ignore the filter
                    pass
            
            # Combine all search criteria or use ALL if none specified
            if search_criteria_list:
                search_criteria = " ".join(search_criteria_list)
            else:
                search_criteria = "ALL"
            
            # First, try to use SORT command if available (for server-side sorting)
            has_sort_capability = False
            try:
                # Check if server supports SORT
                capability_result, capability_data = imap.capability()
                if capability_result == 'OK':
                    capabilities = ' '.join(x.decode() for x in capability_data).upper()
                    has_sort_capability = 'SORT' in capabilities
                
                if has_sort_capability:
                    # Use SORT command to sort by date in descending order (newest first)
                    result, data = imap.uid('SORT', '(REVERSE DATE)', 'UTF-8', search_criteria)
                    if result == 'OK':
                        # Get message IDs from sorted results
                        if data and data[0]:
                            message_nums = data[0].split()
                        else:
                            message_nums = []
                    else:
                        # Fall back to regular search if SORT failed
                        has_sort_capability = False
            except (imaplib.IMAP4.error, AttributeError):
                # Server doesn't support SORT or there was an error
                has_sort_capability = False
            
            # Fall back to regular search if SORT is not available
            if not has_sort_capability:
                result, data = imap.search(None, search_criteria)
                if result != 'OK':
                    raise MailSMTPError(f"Search failed: {data[0].decode()}")
                
                message_nums = data[0].split()
                # Since we can't sort on server, we'll reverse the list to get newest first (approximate)
                # This assumes message IDs are assigned chronologically, which is often but not always true
                message_nums = message_nums[::-1]
            
            total = len(message_nums)
            
            # Apply offset and limit
            start_idx = max(0, offset)
            end_idx = min(total, offset + limit)
            
            message_ids = message_nums[start_idx:end_idx]
            messages = []
            
            # Fetch emails in the selected range
            for num in message_ids:
                try:
                    result, msg_data = imap.fetch(num, '(RFC822)')
                    if result != 'OK':
                        continue
                    
                    raw_email = msg_data[0][1]
                    msg = email.message_from_bytes(raw_email)
                    
                    # Mark as read if requested
                    if mark_as_read:
                        imap.store(num, '+FLAGS', '\\Seen')
                    
                    # Parse the email
                    email_message = self._parse_email_message(msg, folder, mark_as_read)
                    messages.append(email_message)
                except Exception as e:
                    # Skip problematic emails
                    continue
            
            imap.close()
            imap.logout()
            
            # If we couldn't sort on the server, ensure proper sorting here
            if not has_sort_capability:
                # Sort messages by date (newest first)
                from email.utils import parsedate_tz
                
                def get_date_timestamp(msg):
                    date_str = msg.get('date')
                    if date_str:
                        date_tuple = parsedate_tz(date_str)
                        if date_tuple:
                            return email.utils.mktime_tz(date_tuple)
                    return 0  # Default timestamp if date parsing fails
                
                # Sort messages with newest first
                messages.sort(key=get_date_timestamp, reverse=True)
            
            return {
                "messages": messages,
                "total": total,
                "offset": offset,
                "limit": limit
            }
        except MailSMTPError:
            raise
        except Exception as e:
            raise MailSMTPError(f"Failed to get messages: {str(e)}")
    
    def get_message(
        self,
        message_id: str,
        folder: str = 'INBOX',
        mark_as_read: bool = True
    ) -> Dict[str, Any]:
        """Get a specific message by ID."""
        try:
            imap = self._get_imap_connection()
            
            # Select the folder
            result, data = imap.select(f'"{folder}"', readonly=not mark_as_read)
            if result != 'OK':
                raise MailSMTPError(f"Failed to select folder '{folder}': {data[0].decode()}")
            
            # First try to find the message by Message-ID
            result, data = imap.search(None, f'HEADER "Message-ID" "{message_id}"')
            if result != 'OK' or not data[0]:
                # If not found, try without the angle brackets
                stripped_id = message_id.strip('<>')
                result, data = imap.search(None, f'HEADER "Message-ID" "{stripped_id}"')
                
                # If still not found, try with angle brackets
                if result != 'OK' or not data[0]:
                    result, data = imap.search(None, f'HEADER "Message-ID" "<{stripped_id}>"')
            
            if result != 'OK' or not data[0]:
                raise MailSMTPError(f"Message with ID '{message_id}' not found")
            
            # Get the first matching message
            num = data[0].split()[0]
            result, msg_data = imap.fetch(num, '(RFC822)')
            if result != 'OK':
                raise MailSMTPError("Failed to fetch message")
            
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)
            
            # Mark as read if requested
            if mark_as_read:
                imap.store(num, '+FLAGS', '\\Seen')
            
            # Parse the email
            email_message = self._parse_email_message(msg, folder, mark_as_read)
            
            imap.close()
            imap.logout()
            
            return email_message
        except MailSMTPError:
            raise
        except Exception as e:
            raise MailSMTPError(f"Failed to get message: {str(e)}")
    
    def get_folders(self) -> Dict[str, Any]:
        """Get list of mail folders."""
        try:
            imap = self._get_imap_connection()
            
            # List all folders
            result, mailbox_list = imap.list()
            if result != 'OK':
                raise MailSMTPError("Failed to retrieve folders")
            
            folders = []
            for item in mailbox_list:
                # Parse the folder name
                # Format: (flags) delimiter "folder_name"
                mailbox = item.decode()
                if '"' in mailbox:
                    # Extract the folder name
                    folder_name = mailbox.split('"')[-2]
                    
                    # Create folder object
                    folder = {
                        "id": folder_name,
                        "name": folder_name,
                        "type": "custom"
                    }
                    
                    # Set folder type based on common names
                    lower_name = folder_name.lower()
                    if "inbox" in lower_name:
                        folder["type"] = "inbox"
                    elif "sent" in lower_name:
                        folder["type"] = "sent"
                    elif "draft" in lower_name:
                        folder["type"] = "drafts"
                    elif "trash" in lower_name or "bin" in lower_name:
                        folder["type"] = "trash"
                    elif "spam" in lower_name or "junk" in lower_name:
                        folder["type"] = "spam"
                    elif "archive" in lower_name:
                        folder["type"] = "archive"
                    
                    # Try to get message count in folder
                    try:
                        result, data = imap.select(f'"{folder_name}"', readonly=True)
                        if result == 'OK':
                            folder["total_messages"] = int(data[0])
                            # Get unread count
                            result, data = imap.search(None, 'UNSEEN')
                            if result == 'OK':
                                folder["unread_messages"] = len(data[0].split())
                        imap.close()  # Close the selected mailbox without expunging
                    except Exception:
                        folder["total_messages"] = 0
                        folder["unread_messages"] = 0
                    
                    folders.append(folder)
            
            imap.logout()
            
            return {
                "folders": folders
            }
        except MailSMTPError:
            raise
        except Exception as e:
            raise MailSMTPError(f"Failed to get folders: {str(e)}")
    
    def create_folder(self, folder_name: str) -> Dict[str, Any]:
        """Create a new mail folder."""
        try:
            imap = self._get_imap_connection()
            
            # Create the folder
            result, data = imap.create(f'"{folder_name}"')
            if result != 'OK':
                raise MailSMTPError(f"Failed to create folder '{folder_name}': {data[0].decode()}")
            
            imap.logout()
            
            return {
                "success": True,
                "message": f"Folder '{folder_name}' created successfully"
            }
        except MailSMTPError:
            raise
        except Exception as e:
            raise MailSMTPError(f"Failed to create folder: {str(e)}")
    
    def delete_message(self, message_id: str, folder: str = 'INBOX') -> Dict[str, Any]:
        """Delete a message by moving it to the Trash folder or marking it as deleted."""
        try:
            imap = self._get_imap_connection()
            
            # Select the folder
            result, data = imap.select(f'"{folder}"')
            if result != 'OK':
                raise MailSMTPError(f"Failed to select folder '{folder}': {data[0].decode()}")
            
            # Find the message by Message-ID
            result, data = imap.search(None, f'HEADER "Message-ID" "{message_id}"')
            if result != 'OK' or not data[0]:
                # If not found, try without the angle brackets
                stripped_id = message_id.strip('<>')
                result, data = imap.search(None, f'HEADER "Message-ID" "{stripped_id}"')
                
                # If still not found, try with angle brackets
                if result != 'OK' or not data[0]:
                    result, data = imap.search(None, f'HEADER "Message-ID" "<{stripped_id}>"')
            
            if result != 'OK' or not data[0]:
                raise MailSMTPError(f"Message with ID '{message_id}' not found")
            
            num = data[0].split()[0]
            
            # Try to find a trash folder
            trash_folders = ['Trash', 'TRASH', '[Gmail]/Trash', 'Deleted Items', 'Deleted']
            trash_folder = None
            
            # Check which trash folder exists
            for tf in trash_folders:
                result, _ = imap.select(f'"{tf}"')
                if result == 'OK':
                    trash_folder = tf
                    break
            
            imap.select(f'"{folder}"')  # Re-select the original folder
            
            if trash_folder:
                # Move to trash if trash folder exists
                result, data = imap.copy(num, f'"{trash_folder}"')
                if result != 'OK':
                    # If copy fails, just mark as deleted
                    result, data = imap.store(num, '+FLAGS', '\\Deleted')
                    if result != 'OK':
                        raise MailSMTPError("Failed to mark message as deleted")
                else:
                    # If copy succeeds, mark the original for deletion
                    imap.store(num, '+FLAGS', '\\Deleted')
            else:
                # Just mark as deleted if no trash folder
                result, data = imap.store(num, '+FLAGS', '\\Deleted')
                if result != 'OK':
                    raise MailSMTPError("Failed to mark message as deleted")
            
            # Expunge to actually remove messages marked for deletion
            imap.expunge()
            
            imap.close()
            imap.logout()
            
            return {
                "success": True,
                "message": "Message deleted successfully"
            }
        except MailSMTPError:
            raise
        except Exception as e:
            raise MailSMTPError(f"Failed to delete message: {str(e)}")
    
    def move_message(self, message_id: str, source_folder: str, target_folder: str) -> Dict[str, Any]:
        """Move a message from one folder to another."""
        try:
            imap = self._get_imap_connection()
            
            # Select the source folder
            result, data = imap.select(f'"{source_folder}"')
            if result != 'OK':
                raise MailSMTPError(f"Failed to select folder '{source_folder}': {data[0].decode()}")
            
            # Find the message by Message-ID
            result, data = imap.search(None, f'HEADER "Message-ID" "{message_id}"')
            if result != 'OK' or not data[0]:
                # If not found, try without the angle brackets
                stripped_id = message_id.strip('<>')
                result, data = imap.search(None, f'HEADER "Message-ID" "{stripped_id}"')
                
                # If still not found, try with angle brackets
                if result != 'OK' or not data[0]:
                    result, data = imap.search(None, f'HEADER "Message-ID" "<{stripped_id}>"')
            
            if result != 'OK' or not data[0]:
                raise MailSMTPError(f"Message with ID '{message_id}' not found")
            
            num = data[0].split()[0]
            
            # Copy to target folder
            result, data = imap.copy(num, f'"{target_folder}"')
            if result != 'OK':
                raise MailSMTPError(f"Failed to copy message to '{target_folder}'")
            
            # Mark original for deletion
            result, data = imap.store(num, '+FLAGS', '\\Deleted')
            if result != 'OK':
                raise MailSMTPError("Failed to mark original message as deleted")
            
            # Expunge to actually remove
            imap.expunge()
            
            imap.close()
            imap.logout()
            
            return {
                "success": True,
                "message": f"Message moved from '{source_folder}' to '{target_folder}' successfully"
            }
        except MailSMTPError:
            raise
        except Exception as e:
            raise MailSMTPError(f"Failed to move message: {str(e)}")
    
    def send_message(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send an email message."""
        try:
            # Create a multipart message
            msg = MIMEMultipart('alternative')
            
            # Required parameters
            from_email = params.get('from_email', {})
            to = params.get('to', [])
            subject = params.get('subject', '')
            
            # Optional parameters
            cc = params.get('cc', [])
            bcc = params.get('bcc', [])
            body_text = params.get('body_text', '')
            body_html = params.get('body_html', '')
            attachments = params.get('attachments', [])
            
            # Validate required fields
            if not from_email or not (from_email.get('email') or from_email.get('address')):
                raise MailSMTPError("From email is required")
            
            if not to or not any(recipient.get('email') or recipient.get('address') for recipient in to):
                raise MailSMTPError("At least one recipient is required")
            
            # Set basic headers
            from_addr = from_email.get('email') or from_email.get('address')
            from_name = from_email.get('name')
            if from_name:
                msg['From'] = f"{from_name} <{from_addr}>"
            else:
                msg['From'] = from_addr
            
            # Add To header (list of recipients)
            to_addresses = []
            for recipient in to:
                to_addr = recipient.get('email') or recipient.get('address')
                to_name = recipient.get('name')
                if to_addr:
                    if to_name:
                        to_addresses.append(f"{to_name} <{to_addr}>")
                    else:
                        to_addresses.append(to_addr)
            
            msg['To'] = ', '.join(to_addresses)
            
            # Add CC header if present
            if cc:
                cc_addresses = []
                for recipient in cc:
                    cc_addr = recipient.get('email') or recipient.get('address')
                    cc_name = recipient.get('name')
                    if cc_addr:
                        if cc_name:
                            cc_addresses.append(f"{cc_name} <{cc_addr}>")
                        else:
                            cc_addresses.append(cc_addr)
                
                if cc_addresses:
                    msg['Cc'] = ', '.join(cc_addresses)
            
            # Set subject
            msg['Subject'] = subject
            
            # Set other headers
            msg['Date'] = formatdate(localtime=True)
            msg['Message-ID'] = make_msgid(domain=from_addr.split('@')[1])
            
            # Add text part if provided
            if body_text:
                msg.attach(MIMEText(body_text, 'plain'))
            
            # Add HTML part if provided
            if body_html:
                msg.attach(MIMEText(body_html, 'html'))
            
            # Add attachments if any
            for attachment in attachments:
                filename = attachment.get('filename')
                content = attachment.get('content')
                content_type = attachment.get('content_type', 'application/octet-stream')
                
                if filename and content:
                    # Decode base64 content if needed
                    if isinstance(content, str):
                        try:
                            content = base64.b64decode(content)
                        except Exception:
                            # If not base64, treat as binary
                            content = content.encode('utf-8')
                    
                    attach_part = MIMEApplication(content)
                    attach_part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
                    msg.attach(attach_part)
            
            # Get all recipients for sending
            recipients = []
            
            # Add to recipients
            for recipient in to:
                addr = recipient.get('email') or recipient.get('address')
                if addr:
                    recipients.append(addr)
            
            # Add cc recipients
            for recipient in cc:
                addr = recipient.get('email') or recipient.get('address')
                if addr:
                    recipients.append(addr)
            
            # Add bcc recipients
            for recipient in bcc:
                addr = recipient.get('email') or recipient.get('address')
                if addr:
                    recipients.append(addr)
            
            # Connect to SMTP server and send
            smtp = self._get_smtp_connection()
            smtp.send_message(msg)
            smtp.quit()
            
            return {
                "success": True,
                "message_id": msg['Message-ID']
            }
        except MailSMTPError:
            raise
        except Exception as e:
            raise MailSMTPError(f"Failed to send message: {str(e)}") 