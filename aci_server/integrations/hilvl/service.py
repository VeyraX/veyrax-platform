from typing import Dict, Any, Optional, List, Union, cast
import os
from .client import HilvlClient
from .schema import (
    Business, 
    BusinessList,
    BusinessResponse,
    BusinessesResponse,
    CreateBusinessResponse,
    UpdateBusinessResponse,
    DeleteBusinessResponse,
    Calendar,
    CalendarList,
    CalendarResponse,
    CalendarsResponse,
    CreateCalendarResponse,
    UpdateCalendarResponse,
    FreeSlotsResponse,
    FreeSlotsData,
    BlockSlotResponse,
    Contact,
    ContactList,
    ContactResponse,
    ContactsResponse,
    CreateContactResponse,
    UpdateContactResponse,
    DeleteContactResponse,
    UpsertContactResponse,
    ApiResponse,
    GetBusinessParams,
    CreateBusinessParams,
    UpdateBusinessParams,
    DeleteBusinessParams,
    GetCalendarsParams,
    GetCalendarParams,
    CreateCalendarParams,
    UpdateCalendarParams,
    GetFreeSlotsParams,
    GetContactParams,
    CreateContactParams,
    UpdateContactParams,
    DeleteContactParams,
    UpsertContactParams,
    GetContactsByBusinessParams,
    TaskResponse,
    TasksResponse,
    CreateTaskParams,
    UpdateTaskParams,
    DeleteTaskParams,
    UpdateTaskCompletedParams,
    CreateTaskResponse,
    UpdateTaskResponse,
    DeleteTaskResponse,
    UpdateTaskCompletedResponse,
    GetAppointmentsParams,
    AppointmentsResponse,
    AddTagsParams,
    RemoveTagsParams,
    TagsResponse,
    GetTaskParams,
    GetNotesParams,
    GetNoteParams,
    CreateNoteParams,
    UpdateNoteParams,
    DeleteNoteParams,
    NoteResponse,
    NotesResponse,
    CreateNoteResponse,
    UpdateNoteResponse,
    DeleteNoteResponse,
    AddContactToCampaignParams,
    RemoveContactFromCampaignParams,
    RemoveContactFromAllCampaignsParams,
    CampaignSuccessResponse,
    AddContactToWorkflowParams,
    RemoveContactFromWorkflowParams,
    WorkflowSuccessResponse,
    BulkTagUpdateParams,
    BulkTagUpdateResponse,
    BulkBusinessUpdateParams,
    BulkBusinessUpdateResponse,
    ContactSearchParams,
    ContactSearchResponse,
    GetDuplicateContactParams,
    ContactSearchResult,
    AddFollowersParams,
    RemoveFollowersParams,
    FollowersResponse,
    GetConversationParams,
    UpdateConversationParams,
    DeleteConversationParams,
    CreateConversationParams,
    Conversation,
    ConversationSuccess,
    SearchConversationsParams,
    ConversationsSearchResponse,
    GetMessageByIdParams,
    GetEmailByIdParams,
    CancelScheduledEmailParams,
    ConversationMessage,
    EmailMessage,
    CancelEmailResult,
    GetMessagesByConversationParams,
    ConversationMessagesList,
    SendMessageParams,
    SendMessageResponse,
    GetTasksParams
)
from ..common.component_handler import load_components, prepare_components_auto

class HilvlService:
    def __init__(self, client: HilvlClient):
        self.client = client
        self.components_data = self._load_components()
    
    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
    
    def prepare_response(self, data: Any, component_name: str = None) -> ApiResponse:
        tool_name = "hilvl"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)
    
    def get_business(self, business_id: str) -> ApiResponse:
        response = self.client.get_business(business_id)
        business_data = Business(**response["business"])
        result = BusinessResponse(business=business_data)
        return self.prepare_response(result)
    
    def get_businesses_by_location(self, location_id: str) -> ApiResponse:
        response = self.client.get_businesses_by_location(location_id)
        businesses = [Business(**business) for business in response["businesses"]]
        result = BusinessesResponse(businesses=businesses)
        return self.prepare_response(result)
    
    def create_business(self, data: Dict[str, Any]) -> ApiResponse:
        response = self.client.create_business(data)
        business_data = Business(**response["buiseness"])
        result = CreateBusinessResponse(success=response["success"], buiseness=business_data)
        return self.prepare_response(result)
    
    def update_business(self, business_id: str, data: Dict[str, Any]) -> ApiResponse:
        response = self.client.update_business(business_id, data)
        business_data = Business(**response["buiseness"])
        result = UpdateBusinessResponse(success=response["success"], buiseness=business_data)
        return self.prepare_response(result)
    
    def delete_business(self, business_id: str) -> ApiResponse:
        response = self.client.delete_business(business_id)
        result = DeleteBusinessResponse(success=response["success"])
        return self.prepare_response(result)
    
    def get_calendars(self, location_id: str, group_id: Optional[str] = None, show_drafted: bool = True) -> ApiResponse:
        response = self.client.get_calendars(location_id, group_id, show_drafted)
        calendars = [Calendar(**calendar) for calendar in response.get("calendars", [])]
        result = CalendarsResponse(calendars=calendars)
        return self.prepare_response(result)
    
    def get_calendar(self, calendar_id: str) -> ApiResponse:
        response = self.client.get_calendar(calendar_id)
        calendar_data = Calendar(**response.get("calendar", {}))
        result = CalendarResponse(calendar=calendar_data)
        return self.prepare_response(result)
    
    def create_calendar(self, data: Dict[str, Any]) -> ApiResponse:
        response = self.client.create_calendar(data)
        calendar_data = Calendar(**response.get("calendar", {}))
        result = CreateCalendarResponse(calendar=calendar_data)
        return self.prepare_response(result)
    
    def update_calendar(self, calendar_id: str, data: Dict[str, Any]) -> ApiResponse:
        response = self.client.update_calendar(calendar_id, data)
        calendar_data = Calendar(**response.get("calendar", {}))
        result = UpdateCalendarResponse(calendar=calendar_data)
        return self.prepare_response(result)
    
    def delete_calendar(self, calendar_id: str) -> ApiResponse:
        response = self.client.delete_calendar(calendar_id)
        return self.prepare_response(DeleteBusinessResponse(success=response.get("success", False)))
    
    def get_free_slots(self, calendar_id: str, start_date: int, end_date: int, 
                       timezone: Optional[str] = None, user_id: Optional[str] = None,
                       user_ids: Optional[List[str]] = None, enable_look_busy: bool = False) -> ApiResponse:
        response = self.client.get_free_slots(
            calendar_id, start_date, end_date, timezone, user_id, user_ids, enable_look_busy
        )
        dates_data = FreeSlotsData(slots=response.get("_dates_", {}).get("slots", []))
        result = FreeSlotsResponse(_dates_=dates_data)
        return self.prepare_response(result)
    
    def create_block_slot(self, data: Dict[str, Any]) -> ApiResponse:
        response = self.client.create_block_slot(data)
        result = BlockSlotResponse(**response)
        return self.prepare_response(result)
    
    def get_contact(self, contact_id: str) -> ApiResponse:
        response = self.client.get_contact(contact_id)
        contact_data = Contact(**response.get("contact", {}))
        result = ContactResponse(contact=contact_data)
        return self.prepare_response(result)
    
    def get_contacts_by_business(self, business_id: str, location_id: str, 
                               limit: int = 25, skip: int = 0, query: Optional[str] = None) -> ApiResponse:
        response = self.client.get_contacts_by_business(business_id, location_id, limit, skip, query)
        contacts = [Contact(**contact) for contact in response.get("contacts", [])]
        result = ContactsResponse(contacts=contacts, count=response.get("count"))
        return self.prepare_response(result)
    
    def create_contact(self, data: Dict[str, Any]) -> ApiResponse:
        response = self.client.create_contact(data)
        contact_data = Contact(**response.get("contact", {}))
        result = CreateContactResponse(contact=contact_data)
        return self.prepare_response(result)
    
    def update_contact(self, contact_id: str, data: Dict[str, Any]) -> ApiResponse:
        response = self.client.update_contact(contact_id, data)
        contact_data = Contact(**response.get("contact", {}))
        result = UpdateContactResponse(succeded=response.get("succeded", False), contact=contact_data)
        return self.prepare_response(result)
    
    def delete_contact(self, contact_id: str) -> ApiResponse:
        response = self.client.delete_contact(contact_id)
        result = DeleteContactResponse(succeded=response.get("succeded", False))
        return self.prepare_response(result)
    
    def upsert_contact(self, data: Dict[str, Any]) -> ApiResponse:
        response = self.client.upsert_contact(data)
        contact_data = Contact(**response.get("contact", {}))
        result = UpsertContactResponse(
            new=response.get("new", False),
            contact=contact_data,
            traceId=response.get("traceId")
        )
        return self.prepare_response(result)

    async def get_tasks(self, params: GetTasksParams) -> ApiResponse:
        if params.contact_id:
            response = await self.client.get_tasks(params.contact_id)
            return ApiResponse(data=TasksResponse(tasks=response["tasks"]))
        if params.location_id:
            response = {"tasks": []}
            return ApiResponse(data=TasksResponse(tasks=response["tasks"]))
        else:
            raise ValueError("Either contact_id or location_id must be provided")
    
    async def get_task(self, params: GetTaskParams) -> ApiResponse:
        response = await self.client.get_task(params.contact_id, params.task_id)
        return ApiResponse(data=TaskResponse(task=response["task"]))
    
    async def create_task(self, params: CreateTaskParams) -> ApiResponse:
        response = await self.client.create_task(
            params.contact_id,
            params.title,
            params.body,
            params.dueDate,
            params.completed,
            params.assignedTo
        )
        return ApiResponse(data=CreateTaskResponse(task=response["task"]))
    
    async def update_task(self, params: UpdateTaskParams) -> ApiResponse:
        task_data = params.dict(exclude_unset=True, exclude={'contact_id', 'task_id'})
        response = await self.client.update_task(
            params.contact_id,
            params.task_id,
            **task_data
        )
        return ApiResponse(data=UpdateTaskResponse(task=response["task"]))
    
    async def delete_task(self, params: DeleteTaskParams) -> ApiResponse:
        response = await self.client.delete_task(params.contact_id, params.task_id)
        return ApiResponse(data=DeleteTaskResponse(succeded=response["succeeded"]))
    
    async def update_task_completed(self, params: UpdateTaskCompletedParams) -> ApiResponse:
        response = await self.client.update_task_completed(
            params.contact_id,
            params.task_id,
            params.completed
        )
        return ApiResponse(data=UpdateTaskCompletedResponse(task=response["task"]))

    async def get_appointments(self, params: GetAppointmentsParams) -> ApiResponse:
        response = await self.client.get_appointments(params.contact_id)
        return ApiResponse(data=AppointmentsResponse(events=response["events"]))
    
    async def add_tags(self, params: AddTagsParams) -> ApiResponse:
        """Add tags to a contact"""
        response = await self.client.add_tags(params.contact_id, params.tags)
        return ApiResponse(data=TagsResponse(tags=response["tags"]))
    
    async def remove_tags(self, params: RemoveTagsParams) -> ApiResponse:
        """Remove tags from a contact"""
        response = await self.client.remove_tags(params.contact_id, params.tags)
        return ApiResponse(data=TagsResponse(tags=response["tags"]))

    async def get_notes(self, params: GetNotesParams) -> ApiResponse:
        """Get all notes for a contact"""
        response = await self.client.get_notes(params.contact_id)
        return ApiResponse(data=NotesResponse(notes=response["notes"]))
    
    async def get_note(self, params: GetNoteParams) -> ApiResponse:
        """Get a specific note for a contact"""
        response = await self.client.get_note(params.contact_id, params.note_id)
        return ApiResponse(data=NoteResponse(note=response["note"]))
    
    async def create_note(self, params: CreateNoteParams) -> ApiResponse:
        """Create a new note for a contact"""
        response = await self.client.create_note(
            params.contact_id,
            params.body,
            params.userId
        )
        return ApiResponse(data=CreateNoteResponse(note=response["note"]))
    
    async def update_note(self, params: UpdateNoteParams) -> ApiResponse:
        """Update an existing note for a contact"""
        response = await self.client.update_note(
            params.contact_id,
            params.note_id,
            params.body,
            params.userId
        )
        return ApiResponse(data=UpdateNoteResponse(note=response["note"]))
    
    async def delete_note(self, params: DeleteNoteParams) -> ApiResponse:
        """Delete a note for a contact"""
        response = await self.client.delete_note(params.contact_id, params.note_id)
        return ApiResponse(data=DeleteNoteResponse(succeded=response["succeded"]))

    async def add_contact_to_campaign(self, params: AddContactToCampaignParams) -> ApiResponse:
        """Add a contact to a campaign"""
        response = await self.client.add_contact_to_campaign(params.contact_id, params.campaign_id)
        return ApiResponse(data=CampaignSuccessResponse(succeded=response["succeded"]))
    
    async def remove_contact_from_campaign(self, params: RemoveContactFromCampaignParams) -> ApiResponse:
        """Remove a contact from a campaign"""
        response = await self.client.remove_contact_from_campaign(params.contact_id, params.campaign_id)
        return ApiResponse(data=CampaignSuccessResponse(succeded=response["succeded"]))
    
    async def remove_contact_from_all_campaigns(self, params: RemoveContactFromAllCampaignsParams) -> ApiResponse:
        """Remove a contact from all campaigns"""
        response = await self.client.remove_contact_from_all_campaigns(params.contact_id)
        return ApiResponse(data=CampaignSuccessResponse(succeded=response["succeded"]))
    
    async def add_contact_to_workflow(self, params: AddContactToWorkflowParams) -> ApiResponse:
        """Add a contact to a workflow"""
        response = await self.client.add_contact_to_workflow(
            params.contact_id, 
            params.workflow_id,
            params.eventStartTime
        )
        return ApiResponse(data=WorkflowSuccessResponse(succeded=response["succeded"]))
    
    async def remove_contact_from_workflow(self, params: RemoveContactFromWorkflowParams) -> ApiResponse:
        """Remove a contact from a workflow"""
        response = await self.client.remove_contact_from_workflow(params.contact_id, params.workflow_id)
        return ApiResponse(data=WorkflowSuccessResponse(succeded=response["succeded"]))

    async def update_contacts_tags(self, params: BulkTagUpdateParams) -> ApiResponse:
        """Update tags for multiple contacts (add or remove)"""
        response = await self.client.update_contacts_tags(
            params.operation_type,
            params.contacts,
            params.tags,
            params.location_id,
            params.remove_all_tags
        )
        return ApiResponse(data=BulkTagUpdateResponse(**response))
    
    async def update_contacts_business(self, params: BulkBusinessUpdateParams) -> ApiResponse:
        """Add or remove contacts from a business"""
        response = await self.client.update_contacts_business(
            params.location_id,
            params.contact_ids,
            params.business_id
        )
        return ApiResponse(data=BulkBusinessUpdateResponse(**response))
    
    async def search_contacts(self, params: ContactSearchParams) -> ApiResponse:
        """Search contacts based on advanced filters"""
        # Create a search parameters dictionary from the provided params
        search_params = {}
        
        # Add the required location_id
        search_params["location_id"] = params.location_id
        
        # Add all defined parameters if they exist
        if params.query is not None:
            search_params["query"] = params.query
        
        if params.assignedTo is not None:
            search_params["assignedTo"] = params.assignedTo
        
        if params.tags is not None:
            search_params["tags"] = params.tags
        
        if params.businessId is not None:
            search_params["businessId"] = params.businessId
        
        if params.source is not None:
            search_params["source"] = params.source
        
        if params.type is not None:
            search_params["type"] = params.type
        
        if params.dnd is not None:
            search_params["dnd"] = params.dnd
        
        if params.limit is not None:
            search_params["limit"] = params.limit
        
        if params.skip is not None:
            search_params["skip"] = params.skip
        
        if params.page is not None:
            search_params["page"] = params.page
        
        if params.page_size is not None:
            search_params["page_size"] = params.page_size
        
        if params.sort_by is not None:
            search_params["sort_by"] = params.sort_by
        
        if params.sort_dir is not None:
            search_params["sort_dir"] = params.sort_dir
        
        # Add any additional parameters from the search_params field
        if params.search_params:
            for key, value in params.search_params.items():
                if value is not None:
                    search_params[key] = value
        
        # Call the client method with the constructed parameters
        response = await self.client.search_contacts(search_params)
        return ApiResponse(data=ContactSearchResponse(**response))
    
    async def get_duplicate_contact(self, params: GetDuplicateContactParams) -> ApiResponse:
        """Get duplicate contact by email or phone"""
        response = await self.client.get_duplicate_contact(
            params.location_id,
            params.email,
            params.phone
        )
        
        # Check if contact was found in the response
        if "contact" in response and response["contact"]:
            return ApiResponse(data=ContactSearchResult(**response["contact"]))
        
        # Return an empty response if no contact was found
        return ApiResponse(data=ContactSearchResult(id="", locationId=""))

    async def add_followers(self, params: AddFollowersParams) -> ApiResponse:
        """Add followers to a contact"""
        response = await self.client.add_followers(params.contact_id, params.followers)
        return ApiResponse(data=FollowersResponse(**response))
    
    async def remove_followers(self, params: RemoveFollowersParams) -> ApiResponse:
        """Remove followers from a contact"""
        response = await self.client.remove_followers(params.contact_id, params.followers)
        return ApiResponse(data=FollowersResponse(**response))
    
    async def get_conversation(self, params: GetConversationParams) -> ApiResponse:
        """Get conversation details"""
        response = await self.client.get_conversation(params.conversation_id)
        return ApiResponse(data=Conversation(**response))
    
    async def update_conversation(self, params: UpdateConversationParams) -> ApiResponse:
        """Update conversation details"""
        response = await self.client.update_conversation(
            params.conversation_id,
            params.location_id,
            params.unread_count,
            params.starred,
            params.feedback
        )
        return ApiResponse(data=ConversationSuccess(**response))
    
    async def delete_conversation(self, params: DeleteConversationParams) -> ApiResponse:
        """Delete a conversation"""
        response = await self.client.delete_conversation(params.conversation_id)
        return ApiResponse(data=ConversationSuccess(success=response["success"]))
    
    async def create_conversation(self, params: CreateConversationParams) -> ApiResponse:
        """Create a new conversation"""
        response = await self.client.create_conversation(params.location_id, params.contact_id)
        return ApiResponse(data=ConversationSuccess(**response))

    async def search_conversations(self, params: SearchConversationsParams) -> ApiResponse:
        """Search conversations based on criteria"""
        # Create a parameters dictionary with all possible parameters
        search_params = {
            "location_id": params.location_id
        }
        
        # Add all optional parameters if they exist
        if params.assigned_to is not None:
            search_params["assigned_to"] = params.assigned_to
        
        if params.contact_id is not None:
            search_params["contact_id"] = params.contact_id
        
        if params.followers is not None:
            search_params["followers"] = params.followers
        
        if params.conversation_id is not None:
            search_params["id"] = params.conversation_id
        
        if params.last_message_action is not None:
            search_params["last_message_action"] = params.last_message_action
        
        if params.last_message_direction is not None:
            search_params["last_message_direction"] = params.last_message_direction
        
        if params.last_message_type is not None:
            search_params["last_message_type"] = params.last_message_type
        
        if params.limit is not None:
            search_params["limit"] = params.limit
        
        if params.mentions is not None:
            search_params["mentions"] = params.mentions
        
        if params.query is not None:
            search_params["query"] = params.query
        
        if params.score_profile is not None:
            search_params["score_profile"] = params.score_profile
        
        if params.score_profile_min is not None:
            search_params["score_profile_min"] = params.score_profile_min
        
        if params.score_profile_max is not None:
            search_params["score_profile_max"] = params.score_profile_max
        
        if params.sort is not None:
            search_params["sort"] = params.sort
        
        if params.sort_by is not None:
            search_params["sort_by"] = params.sort_by
        
        if params.sort_score_profile is not None:
            search_params["sort_score_profile"] = params.sort_score_profile
        
        if params.start_after_date is not None:
            search_params["start_after_date"] = params.start_after_date
        
        if params.status is not None:
            search_params["status"] = params.status
        
        if params.page is not None:
            search_params["page"] = params.page
        
        if params.page_size is not None:
            search_params["page_size"] = params.page_size
        
        # Call client method with all parameters
        response = await self.client.search_conversations(**search_params)
        return ApiResponse(data=ConversationsSearchResponse(**response))
    
    async def get_message_by_id(self, params: GetMessageByIdParams) -> ApiResponse:
        """Get message details by message ID"""
        response = await self.client.get_message_by_id(params.message_id)
        return ApiResponse(data=ConversationMessage(**response))
    
    async def get_email_by_id(self, params: GetEmailByIdParams) -> ApiResponse:
        """Get email details by email ID"""
        response = await self.client.get_email_by_id(params.email_id)
        return ApiResponse(data=EmailMessage(**response))
    
    async def cancel_scheduled_email(self, params: CancelScheduledEmailParams) -> ApiResponse:
        """Cancel a scheduled email message"""
        response = await self.client.cancel_scheduled_email(params.email_message_id)
        return ApiResponse(data=CancelEmailResult(**response))

    async def get_messages_by_conversation_id(
        self, params: GetMessagesByConversationParams
    ) -> ApiResponse:
        """
        Get messages by conversation ID
        """
        # Create a parameters dictionary with all possible parameters
        message_params = {
            "conversation_id": params.conversation_id
        }
        
        # Add all optional parameters if they exist
        if params.last_message_id is not None:
            message_params["last_message_id"] = params.last_message_id
        
        if params.limit is not None:
            message_params["limit"] = params.limit
        
        if params.message_types is not None:
            message_params["message_types"] = params.message_types
        
        if params.direction is not None:
            message_params["direction"] = params.direction
        
        if params.status is not None:
            message_params["status"] = params.status
        
        if params.from_date is not None:
            message_params["from_date"] = params.from_date
        
        if params.to_date is not None:
            message_params["to_date"] = params.to_date
        
        if params.sort_by is not None:
            message_params["sort_by"] = params.sort_by
        
        if params.sort_dir is not None:
            message_params["sort_dir"] = params.sort_dir
        
        # Call client method with all parameters
        response = await self.client.get_messages_by_conversation_id(**message_params)
        
        # Convert the response to a ConversationMessagesList object
        messages_list = ConversationMessagesList(
            lastMessageId=response.get("lastMessageId", ""),
            nextPage=response.get("nextPage", False),
            messages=[ConversationMessage(**msg) for msg in response.get("messages", [])]
        )
        
        return ApiResponse(data=messages_list)

    async def send_message(
        self, params: SendMessageParams
    ) -> ApiResponse:
        """
        Send a message
        """
        response = await self.client.send_message(
            message_type=params.message_type,
            contact_id=params.contact_id,
            message=params.message,
            html=params.html,
            subject=params.subject,
            appointment_id=params.appointment_id,
            attachments=params.attachments,
            email_from=params.email_from,
            email_to=params.email_to,
            email_cc=params.email_cc,
            email_bcc=params.email_bcc,
            email_reply_mode=params.email_reply_mode,
            reply_message_id=params.reply_message_id,
            template_id=params.template_id,
            thread_id=params.thread_id,
            scheduled_timestamp=params.scheduled_timestamp,
            conversation_provider_id=params.conversation_provider_id,
            from_number=params.from_number,
            to_number=params.to_number
        )
        
        # Convert the response to a SendMessageResponse object
        send_message_response = SendMessageResponse(
            conversationId=response.get("conversationId", ""),
            messageId=response.get("messageId", ""),
            emailMessageId=response.get("emailMessageId"),
            messageIds=response.get("messageIds"),
            msg=response.get("msg")
        )
        
        return ApiResponse(data=send_message_response)
