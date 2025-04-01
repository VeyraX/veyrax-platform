import requests
from typing import Dict, Any, Optional, List, Literal

class HilvlClient:
    BASE_URL = "https://services.leadconnectorhq.com"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Version": "2021-07-28",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    # Business endpoints
    def get_business(self, business_id: str) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/businesses/{business_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_businesses_by_location(self, location_id: str) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/businesses/",
            params={"locationId": location_id},
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def create_business(self, data: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.post(
            f"{self.BASE_URL}/businesses/",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def update_business(self, business_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.put(
            f"{self.BASE_URL}/businesses/{business_id}",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def delete_business(self, business_id: str) -> Dict[str, Any]:
        response = requests.delete(
            f"{self.BASE_URL}/businesses/{business_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
        
    # Calendar endpoints
    def get_calendars(self, location_id: str, group_id: Optional[str] = None, show_drafted: bool = True) -> Dict[str, Any]:
        params = {"locationId": location_id}
        if group_id:
            params["groupId"] = group_id
        if show_drafted is not None:
            params["showDrafted"] = str(show_drafted).lower()
            
        response = requests.get(
            f"{self.BASE_URL}/calendars/",
            params=params,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_calendar(self, calendar_id: str) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/calendars/{calendar_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def create_calendar(self, data: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.post(
            f"{self.BASE_URL}/calendars/",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def update_calendar(self, calendar_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.put(
            f"{self.BASE_URL}/calendars/{calendar_id}",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def delete_calendar(self, calendar_id: str) -> Dict[str, Any]:
        response = requests.delete(
            f"{self.BASE_URL}/calendars/{calendar_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_free_slots(self, calendar_id: str, start_date: int, end_date: int, 
                       timezone: Optional[str] = None, user_id: Optional[str] = None,
                       user_ids: Optional[list] = None, enable_look_busy: bool = False) -> Dict[str, Any]:
        params = {
            "startDate": start_date,
            "endDate": end_date,
            "enableLookBusy": str(enable_look_busy).lower()
        }
        if timezone:
            params["timezone"] = timezone
        if user_id:
            params["userId"] = user_id
        if user_ids:
            params["userIds"] = user_ids
        
        response = requests.get(
            f"{self.BASE_URL}/calendars/{calendar_id}/free-slots",
            params=params,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def create_block_slot(self, data: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.post(
            f"{self.BASE_URL}/calendars/events/block-slots",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
        
    # Contact endpoints
    def get_contact(self, contact_id: str) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/contacts/{contact_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def create_contact(self, data: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.post(
            f"{self.BASE_URL}/contacts/",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def update_contact(self, contact_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.put(
            f"{self.BASE_URL}/contacts/{contact_id}",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def delete_contact(self, contact_id: str) -> Dict[str, Any]:
        response = requests.delete(
            f"{self.BASE_URL}/contacts/{contact_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def upsert_contact(self, data: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.post(
            f"{self.BASE_URL}/contacts/upsert",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def get_contacts_by_business(self, business_id: str, location_id: str, 
                               limit: int = 25, skip: int = 0, query: Optional[str] = None) -> Dict[str, Any]:
        params = {
            "locationId": location_id,
            "limit": limit,
            "skip": skip
        }
        if query:
            params["query"] = query
            
        response = requests.get(
            f"{self.BASE_URL}/contacts/business/{business_id}",
            params=params,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
        
    # Task endpoints
    def get_tasks(self, contact_id: str) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/contacts/{contact_id}/tasks",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_task(self, contact_id: str, task_id: str) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/contacts/{contact_id}/tasks/{task_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def create_task(self, contact_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.post(
            f"{self.BASE_URL}/contacts/{contact_id}/tasks",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def update_task(self, contact_id: str, task_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.put(
            f"{self.BASE_URL}/contacts/{contact_id}/tasks/{task_id}",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def delete_task(self, contact_id: str, task_id: str) -> Dict[str, Any]:
        response = requests.delete(
            f"{self.BASE_URL}/contacts/{contact_id}/tasks/{task_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def update_task_completed(self, contact_id: str, task_id: str, completed: bool) -> Dict[str, Any]:
        response = requests.put(
            f"{self.BASE_URL}/contacts/{contact_id}/tasks/{task_id}/completed",
            headers=self.headers,
            json={"completed": completed}
        )
        response.raise_for_status()
        return response.json()
    
    # Contact Appointments endpoints
    def get_appointments(self, contact_id: str) -> Dict[str, Any]:
        """Get appointments for a contact"""
        response = requests.get(
            f"{self.BASE_URL}/contacts/{contact_id}/appointments",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    # Contact Tags endpoints
    def add_tags(self, contact_id: str, tags: List[str]) -> Dict[str, Any]:
        """Add tags to a contact"""
        response = requests.post(
            f"{self.BASE_URL}/contacts/{contact_id}/tags",
            headers=self.headers,
            json={"tags": tags}
        )
        response.raise_for_status()
        return response.json()
    
    def remove_tags(self, contact_id: str, tags: List[str]) -> Dict[str, Any]:
        """Remove tags from a contact"""
        response = requests.delete(
            f"{self.BASE_URL}/contacts/{contact_id}/tags",
            headers=self.headers,
            json={"tags": tags}
        )
        response.raise_for_status()
        return response.json()
    
    # Contact Notes endpoints
    def get_notes(self, contact_id: str) -> Dict[str, Any]:
        """Get all notes for a contact"""
        response = requests.get(
            f"{self.BASE_URL}/contacts/{contact_id}/notes",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_note(self, contact_id: str, note_id: str) -> Dict[str, Any]:
        """Get a specific note for a contact"""
        response = requests.get(
            f"{self.BASE_URL}/contacts/{contact_id}/notes/{note_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def create_note(self, contact_id: str, body: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a new note for a contact"""
        data = {"body": body}
        if user_id:
            data["userId"] = user_id
            
        response = requests.post(
            f"{self.BASE_URL}/contacts/{contact_id}/notes",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def update_note(self, contact_id: str, note_id: str, body: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Update an existing note for a contact"""
        data = {"body": body}
        if user_id:
            data["userId"] = user_id
            
        response = requests.put(
            f"{self.BASE_URL}/contacts/{contact_id}/notes/{note_id}",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def delete_note(self, contact_id: str, note_id: str) -> Dict[str, Any]:
        """Delete a note for a contact"""
        response = requests.delete(
            f"{self.BASE_URL}/contacts/{contact_id}/notes/{note_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    # Contact Campaign endpoints
    def add_contact_to_campaign(self, contact_id: str, campaign_id: str) -> Dict[str, Any]:
        """Add a contact to a campaign"""
        response = requests.post(
            f"{self.BASE_URL}/contacts/{contact_id}/campaigns/{campaign_id}",
            headers=self.headers,
            json={}
        )
        response.raise_for_status()
        return response.json()
    
    def remove_contact_from_campaign(self, contact_id: str, campaign_id: str) -> Dict[str, Any]:
        """Remove a contact from a campaign"""
        response = requests.delete(
            f"{self.BASE_URL}/contacts/{contact_id}/campaigns/{campaign_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def remove_contact_from_all_campaigns(self, contact_id: str) -> Dict[str, Any]:
        """Remove a contact from all campaigns"""
        response = requests.delete(
            f"{self.BASE_URL}/contacts/{contact_id}/campaigns/removeAll",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    # Contact Workflow endpoints
    def add_contact_to_workflow(self, contact_id: str, workflow_id: str, event_start_time: Optional[str] = None) -> Dict[str, Any]:
        """Add a contact to a workflow"""
        data = {}
        if event_start_time:
            data["eventStartTime"] = event_start_time
            
        response = requests.post(
            f"{self.BASE_URL}/contacts/{contact_id}/workflow/{workflow_id}",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def remove_contact_from_workflow(self, contact_id: str, workflow_id: str) -> Dict[str, Any]:
        """Remove a contact from a workflow"""
        response = requests.delete(
            f"{self.BASE_URL}/contacts/{contact_id}/workflow/{workflow_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    # Bulk Contact Operations
    def update_contacts_tags(self, 
                             operation_type: Literal["add", "remove"], 
                             contacts: List[str], 
                             tags: List[str], 
                             location_id: str,
                             remove_all_tags: bool = False) -> Dict[str, Any]:
        """Update tags for multiple contacts at once (add or remove)"""
        data = {
            "contacts": contacts,
            "tags": tags,
            "locationId": location_id
        }
        
        if operation_type == "remove" and remove_all_tags:
            data["removeAllTags"] = True
            
        response = requests.post(
            f"{self.BASE_URL}/contacts/bulk/tags/update/{operation_type}",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def update_contacts_business(self, 
                                location_id: str, 
                                contact_ids: List[str], 
                                business_id: Optional[str] = None) -> Dict[str, Any]:
        """Add/remove contacts from a business"""
        data = {
            "locationId": location_id,
            "ids": contact_ids,
            "businessId": business_id
        }
        
        response = requests.post(
            f"{self.BASE_URL}/contacts/bulk/business",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    # Contact Search Operations
    def search_contacts(self, search_params: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """
        Search contacts with advanced filters
        
        Parameters:
        - location_id: Required location ID
        - query: Optional text search
        - assignedTo: Filter by assigned user
        - tags: Filter by tags list
        - businessId: Filter by business ID
        - source: Filter by source
        - type: Filter by contact type
        - dnd: Filter by do not disturb status
        - limit: Number of results to return
        - skip: Number of results to skip
        - page: Page number
        - page_size: Results per page
        - sort_by: Field to sort by
        - sort_dir: Sort direction (asc or desc)
        - Additional parameters can be passed as kwargs
        """
        if search_params is None:
            search_params = {}
        
        # Add any additional parameters
        if kwargs:
            search_params.update(kwargs)
        
        response = requests.post(
            f"{self.BASE_URL}/contacts/search",
            headers=self.headers,
            json=search_params
        )
        response.raise_for_status()
        return response.json()
    
    def get_duplicate_contact(self, 
                             location_id: str, 
                             email: Optional[str] = None, 
                             phone: Optional[str] = None) -> Dict[str, Any]:
        """Get duplicate contact by email or phone number"""
        params = {"locationId": location_id}
        
        if email:
            params["email"] = email
        if phone:
            params["number"] = phone
            
        response = requests.get(
            f"{self.BASE_URL}/contacts/search/duplicate",
            params=params,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    # Contact Followers endpoints
    def add_followers(self, contact_id: str, followers: List[str]) -> Dict[str, Any]:
        """Add followers to a contact"""
        response = requests.post(
            f"{self.BASE_URL}/contacts/{contact_id}/followers",
            headers=self.headers,
            json={"followers": followers}
        )
        response.raise_for_status()
        return response.json()
    
    def remove_followers(self, contact_id: str, followers: List[str]) -> Dict[str, Any]:
        """Remove followers from a contact"""
        response = requests.delete(
            f"{self.BASE_URL}/contacts/{contact_id}/followers",
            headers=self.headers,
            json={"followers": followers}
        )
        response.raise_for_status()
        return response.json()
    
    # Conversation endpoints
    def get_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """Get conversation details"""
        response = requests.get(
            f"{self.BASE_URL}/conversations/{conversation_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def update_conversation(self, 
                          conversation_id: str,
                          location_id: str,
                          unread_count: Optional[int] = None,
                          starred: Optional[bool] = None,
                          feedback: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Update conversation details"""
        data = {"locationId": location_id}
        
        if unread_count is not None:
            data["unreadCount"] = unread_count
            
        if starred is not None:
            data["starred"] = starred
            
        if feedback is not None:
            data["feedback"] = feedback
            
        response = requests.put(
            f"{self.BASE_URL}/conversations/{conversation_id}",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def delete_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """Delete a conversation"""
        response = requests.delete(
            f"{self.BASE_URL}/conversations/{conversation_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def create_conversation(self, location_id: str, contact_id: str) -> Dict[str, Any]:
        """Create a new conversation"""
        response = requests.post(
            f"{self.BASE_URL}/conversations/",
            headers=self.headers,
            json={
                "locationId": location_id,
                "contactId": contact_id
            }
        )
        response.raise_for_status()
        return response.json()

    # Conversation Search endpoints
    def search_conversations(self, 
                          location_id: str,
                          assigned_to: Optional[str] = None,
                          contact_id: Optional[str] = None,
                          followers: Optional[str] = None,
                          conversation_id: Optional[str] = None,
                          last_message_action: Optional[str] = None,
                          last_message_direction: Optional[str] = None,
                          last_message_type: Optional[str] = None,
                          limit: Optional[int] = None,
                          mentions: Optional[str] = None,
                          query: Optional[str] = None,
                          score_profile: Optional[str] = None,
                          score_profile_min: Optional[int] = None,
                          score_profile_max: Optional[int] = None,
                          sort: Optional[str] = None,
                          sort_by: Optional[str] = None,
                          sort_score_profile: Optional[str] = None,
                          start_after_date: Optional[str] = None,
                          status: Optional[str] = None,
                          page: Optional[int] = None,
                          page_size: Optional[int] = None,
                          **kwargs) -> Dict[str, Any]:
        """Search conversations based on criteria with pagination support"""
        params = {"locationId": location_id}
        
        if assigned_to:
            params["assignedTo"] = assigned_to
        if contact_id:
            params["contactId"] = contact_id
        if followers:
            params["followers"] = followers
        if conversation_id:
            params["id"] = conversation_id
        if last_message_action:
            params["lastMessageAction"] = last_message_action
        if last_message_direction:
            params["lastMessageDirection"] = last_message_direction
        if last_message_type:
            params["lastMessageType"] = last_message_type
        if limit:
            params["limit"] = limit
        if mentions:
            params["mentions"] = mentions
        if query:
            params["query"] = query
        if score_profile:
            params["scoreProfile"] = score_profile
        if score_profile_min:
            params["scoreProfileMin"] = score_profile_min
        if score_profile_max:
            params["scoreProfileMax"] = score_profile_max
        if sort:
            params["sort"] = sort
        if sort_by:
            params["sortBy"] = sort_by
        if sort_score_profile:
            params["sortScoreProfile"] = sort_score_profile
        if start_after_date:
            params["startAfterDate"] = start_after_date
        if status:
            params["status"] = status
        if page:
            params["page"] = page
        if page_size:
            params["pageSize"] = page_size
        
        # Add any additional parameters
        for key, value in kwargs.items():
            params[key] = value
        
        # Update version for conversation endpoints
        custom_headers = self.headers.copy()
        custom_headers["Version"] = "2021-04-15"
        
        response = requests.get(
            f"{self.BASE_URL}/conversations/search",
            params=params,
            headers=custom_headers
        )
        response.raise_for_status()
        return response.json()
    
    # Conversation Message endpoints
    def get_message_by_id(self, message_id: str) -> Dict[str, Any]:
        """Get message details by message ID"""
        custom_headers = self.headers.copy()
        custom_headers["Version"] = "2021-04-15"
        
        response = requests.get(
            f"{self.BASE_URL}/conversations/messages/{message_id}",
            headers=custom_headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_email_by_id(self, email_id: str) -> Dict[str, Any]:
        """Get email details by email ID"""
        response = requests.get(
            f"{self.BASE_URL}/conversations/messages/email/{email_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def cancel_scheduled_email(self, email_message_id: str) -> Dict[str, Any]:
        """Cancel a scheduled email message"""
        response = requests.delete(
            f"{self.BASE_URL}/conversations/messages/email/{email_message_id}/schedule",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    # Conversation Messages endpoints
    def get_messages_by_conversation_id(self, 
                                     conversation_id: str,
                                     last_message_id: Optional[str] = None,
                                     limit: Optional[int] = None,
                                     message_types: Optional[str] = None,
                                     direction: Optional[str] = None,
                                     status: Optional[str] = None,
                                     from_date: Optional[str] = None,
                                     to_date: Optional[str] = None,
                                     sort_by: Optional[str] = None,
                                     sort_dir: Optional[str] = None) -> Dict[str, Any]:
        """Get messages by conversation ID with advanced filtering"""
        params = {}
        
        if last_message_id:
            params["lastMessageId"] = last_message_id
        if limit:
            params["limit"] = limit
        if message_types:
            params["type"] = message_types
        if direction:
            params["direction"] = direction
        if status:
            params["status"] = status
        if from_date:
            params["fromDate"] = from_date
        if to_date:
            params["toDate"] = to_date
        if sort_by:
            params["sortBy"] = sort_by
        if sort_dir:
            params["sortDir"] = sort_dir
        
        # Update version for conversation endpoints
        custom_headers = self.headers.copy()
        custom_headers["Version"] = "2021-04-15"
        
        response = requests.get(
            f"{self.BASE_URL}/conversations/{conversation_id}/messages",
            params=params,
            headers=custom_headers
        )
        response.raise_for_status()
        return response.json()
    
    def send_message(self, 
                   message_type: str,
                   contact_id: str,
                   message: Optional[str] = None,
                   html: Optional[str] = None,
                   subject: Optional[str] = None,
                   appointment_id: Optional[str] = None,
                   attachments: Optional[List[str]] = None,
                   email_from: Optional[str] = None,
                   email_to: Optional[str] = None,
                   email_cc: Optional[List[str]] = None,
                   email_bcc: Optional[List[str]] = None,
                   email_reply_mode: Optional[str] = None,
                   reply_message_id: Optional[str] = None,
                   template_id: Optional[str] = None,
                   thread_id: Optional[str] = None,
                   scheduled_timestamp: Optional[int] = None,
                   conversation_provider_id: Optional[str] = None,
                   from_number: Optional[str] = None,
                   to_number: Optional[str] = None) -> Dict[str, Any]:
        """Send a new message"""
        data = {
            "type": message_type,
            "contactId": contact_id
        }
        
        # Add optional parameters
        if message:
            data["message"] = message
        if html:
            data["html"] = html
        if subject:
            data["subject"] = subject
        if appointment_id:
            data["appointmentId"] = appointment_id
        if attachments:
            data["attachments"] = attachments
        if email_from:
            data["emailFrom"] = email_from
        if email_to:
            data["emailTo"] = email_to
        if email_cc:
            data["emailCc"] = email_cc
        if email_bcc:
            data["emailBcc"] = email_bcc
        if email_reply_mode:
            data["emailReplyMode"] = email_reply_mode
        if reply_message_id:
            data["replyMessageId"] = reply_message_id
        if template_id:
            data["templateId"] = template_id
        if thread_id:
            data["threadId"] = thread_id
        if scheduled_timestamp:
            data["scheduledTimestamp"] = scheduled_timestamp
        if conversation_provider_id:
            data["conversationProviderId"] = conversation_provider_id
        if from_number:
            data["fromNumber"] = from_number
        if to_number:
            data["toNumber"] = to_number
        
        # Update version for conversation endpoints
        custom_headers = self.headers.copy()
        custom_headers["Version"] = "2021-04-15"
        
        response = requests.post(
            f"{self.BASE_URL}/conversations/messages",
            json=data,
            headers=custom_headers
        )
        response.raise_for_status()
        return response.json()
