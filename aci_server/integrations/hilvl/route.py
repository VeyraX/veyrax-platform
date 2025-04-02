from fastapi import APIRouter, Body, Depends, HTTPException
from starlette.requests import Request as FastAPIRequest
from typing import Dict, Any, List, Optional
from .service import HilvlService
from .client import HilvlClient
from .schema import (
    # Business schemas
    GetBusinessParams,
    GetBusinessesByLocationParams,
    CreateBusinessParams,
    UpdateBusinessParams,
    DeleteBusinessParams,
    
    # Calendar schemas
    GetCalendarsParams,
    GetCalendarParams,
    CreateCalendarParams,
    UpdateCalendarParams,
    DeleteCalendarParams,
    GetFreeSlotsParams,
    CreateBlockSlotParams,
    
    # Contact schemas
    GetContactParams,
    GetContactsByBusinessParams,
    CreateContactParams,
    UpdateContactParams,
    DeleteContactParams,
    UpsertContactParams,
    
    # Task schemas
    GetTasksParams,
    GetTaskParams,
    CreateTaskParams,
    UpdateTaskParams,
    DeleteTaskParams,
    UpdateTaskCompletedParams,
    
    # Appointment schemas
    GetAppointmentsParams,
    
    # Tag schemas
    AddTagsParams,
    RemoveTagsParams,
    
    # Note schemas
    GetNotesParams,
    GetNoteParams,
    CreateNoteParams,
    UpdateNoteParams,
    DeleteNoteParams,
    
    # Campaign schemas
    AddContactToCampaignParams,
    RemoveContactFromCampaignParams,
    RemoveContactFromAllCampaignsParams,
    
    # Workflow schemas
    AddContactToWorkflowParams,
    RemoveContactFromWorkflowParams,
    
    # Bulk Operations params
    BulkTagUpdateParams,
    BulkBusinessUpdateParams,
    
    # Search params
    ContactSearchParams,
    GetDuplicateContactParams,
    
    # Followers params
    AddFollowersParams,
    RemoveFollowersParams,
    
    # Conversation params
    GetConversationParams,
    UpdateConversationParams,
    DeleteConversationParams,
    CreateConversationParams,
    
    # Conversation Search params
    SearchConversationsParams,
    
    # Conversation Message params
    GetMessageByIdParams,
    GetEmailByIdParams,
    CancelScheduledEmailParams,
    
    ApiResponse,
    GetMessagesByConversationParams,
    ConversationMessagesList,
    SendMessageParams,
    SendMessageResponse,
    BusinessResponse,
    BusinessesResponse,
    CreateBusinessResponse,
    UpdateBusinessResponse,
    DeleteBusinessResponse,
    CalendarsResponse,
    CalendarResponse,
    CreateCalendarResponse,
    UpdateCalendarResponse,
    FreeSlotsResponse,
    BlockSlotResponse,
    ContactResponse,
    ContactsResponse,
    CreateContactResponse,
    UpdateContactResponse,
    DeleteContactResponse,
    UpsertContactResponse,
    TasksResponse,
    TaskResponse,
    CreateTaskResponse,
    UpdateTaskResponse,
    DeleteTaskResponse,
    UpdateTaskCompletedResponse,
    AppointmentsResponse,
    TagsResponse,
    NotesResponse,
    NoteResponse,
    CreateNoteResponse,
    UpdateNoteResponse,
    DeleteNoteResponse,
    CampaignSuccessResponse,
    WorkflowSuccessResponse,
    BulkTagUpdateResponse,
    BulkBusinessUpdateResponse,
    ContactSearchResponse,
    ContactSearchResult,
    FollowersResponse,
    Conversation,
    ConversationSuccess,
    ConversationsSearchResponse,
    ConversationMessage,
    EmailMessage,
    CancelEmailResult,
    SuccessResponse,
    SendMessageResponse 
)
from ..common.auth import validate_provider_api_key
from ..common.input_schema_decorator import schema
from ..common.utils import apply_error_handler_to_service, apply_error_handler_to_router, apply_error_handler_to_client
from ..common.examples_handler import ExamplesLoader

router = APIRouter(prefix="/hilvl", tags=["hilvl"])
examples = ExamplesLoader()

async def get_hilvl_service(request: FastAPIRequest):
    try:
        api_key = await validate_provider_api_key(request, "hilvl")
        client = HilvlClient(api_key)
        apply_error_handler_to_client(client)
        service = HilvlService(client)
        apply_error_handler_to_service(service)
        return service
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Failed to initialize HiLvl service: {str(e)}"
        )

# Business endpoints
@router.post("/get_business", response_model=ApiResponse)
@schema(
    input_schema_class=GetBusinessParams,
    output_schema_class=BusinessResponse,
    examples=examples["/hilvl/get_business"]
)
async def get_business(
    params: Dict[str, Any] = Body(...),
    service: HilvlService = Depends(get_hilvl_service)
):
    """Get business details"""
    validated_params = GetBusinessParams(**params)
    return service.get_business(validated_params.business_id)

@router.post("/get_businesses_by_location", response_model=ApiResponse)
@schema(
    input_schema_class=GetBusinessesByLocationParams,
    output_schema_class=BusinessesResponse,
    examples=examples["/hilvl/get_businesses_by_location"]
)
async def get_businesses_by_location(
    params: Dict[str, Any] = Body(...),
    service: HilvlService = Depends(get_hilvl_service)
):
    """Get businesses for a location"""
    validated_params = GetBusinessesByLocationParams(**params)
    return service.get_businesses_by_location(validated_params.location_id)

@router.post("/create_business", response_model=ApiResponse)
@schema(
    input_schema_class=CreateBusinessParams,
    output_schema_class=CreateBusinessResponse,
    examples=examples["/hilvl/create_business"]
)
async def create_business(
    params: Dict[str, Any] = Body(...),
    service: HilvlService = Depends(get_hilvl_service)
):
    """Create a new business"""
    validated_params = CreateBusinessParams(**params)
    return service.create_business(validated_params.model_dump(exclude_none=True))

@router.post("/update_business", response_model=ApiResponse)
@schema(
    input_schema_class=UpdateBusinessParams,
    output_schema_class=UpdateBusinessResponse,
    examples=examples["/hilvl/update_business"]
)
async def update_business(
    params: Dict[str, Any] = Body(...),
    service: HilvlService = Depends(get_hilvl_service)
):
    """Update an existing business"""
    validated_params = UpdateBusinessParams(**params)
    business_id = validated_params.business_id
    data = validated_params.model_dump(exclude={"business_id"}, exclude_none=True)
    return service.update_business(business_id, data)

@router.post("/delete_business", response_model=ApiResponse)
@schema(
    input_schema_class=DeleteBusinessParams,
    output_schema_class=DeleteBusinessResponse,
    examples=examples["/hilvl/delete_business"]
)
async def delete_business(
    params: Dict[str, Any] = Body(...),
    service: HilvlService = Depends(get_hilvl_service)
):
    """Delete a business"""
    validated_params = DeleteBusinessParams(**params)
    return service.delete_business(validated_params.business_id)

# Calendar endpoints
@router.post("/get_calendars", response_model=ApiResponse)
@schema(
    input_schema_class=GetCalendarsParams,
    output_schema_class=CalendarsResponse,
    examples=examples["/hilvl/get_calendars"]
)
async def get_calendars(
    params: Dict[str, Any] = Body(...),
    service: HilvlService = Depends(get_hilvl_service)
):
    """Get calendars for a location"""
    validated_params = GetCalendarsParams(**params)
    return service.get_calendars(
        validated_params.location_id, 
        validated_params.group_id, 
        validated_params.show_drafted
    )

@router.post("/get_calendar", response_model=ApiResponse)
@schema(
    input_schema_class=GetCalendarParams,
    output_schema_class=CalendarResponse,
    examples=examples["/hilvl/get_calendar"]
)
async def get_calendar(
    params: Dict[str, Any] = Body(...),
    service: HilvlService = Depends(get_hilvl_service)
):
    """Get calendar details"""
    validated_params = GetCalendarParams(**params)
    return service.get_calendar(validated_params.calendar_id)

@router.post("/create_calendar", response_model=ApiResponse)
@schema(
    input_schema_class=CreateCalendarParams,
    output_schema_class=CreateCalendarResponse,
    examples=examples["/hilvl/create_calendar"]
)
async def create_calendar(
    params: Dict[str, Any] = Body(...),
    service: HilvlService = Depends(get_hilvl_service)
):
    """Create a new calendar"""
    validated_params = CreateCalendarParams(**params)
    return service.create_calendar(validated_params.model_dump(exclude_none=True))

@router.post("/update_calendar", response_model=ApiResponse)
@schema(
    input_schema_class=UpdateCalendarParams,
    output_schema_class=UpdateCalendarResponse,
    examples=examples["/hilvl/update_calendar"]
)
async def update_calendar(
    params: Dict[str, Any] = Body(...),
    service: HilvlService = Depends(get_hilvl_service)
):
    """Update an existing calendar"""
    validated_params = UpdateCalendarParams(**params)
    calendar_id = validated_params.calendar_id
    data = validated_params.model_dump(exclude={"calendar_id"}, exclude_none=True)
    return service.update_calendar(calendar_id, data)

@router.post("/delete_calendar", response_model=ApiResponse)
@schema(
    input_schema_class=DeleteCalendarParams,
    output_schema_class=SuccessResponse,
    examples=examples["/hilvl/delete_calendar"]
)
async def delete_calendar(
    params: Dict[str, Any] = Body(...),
    service: HilvlService = Depends(get_hilvl_service)
):
    """Delete a calendar"""
    validated_params = DeleteCalendarParams(**params)
    return service.delete_calendar(validated_params.calendar_id)

@router.post("/get_free_slots", response_model=ApiResponse)
@schema(
    input_schema_class=GetFreeSlotsParams,
    output_schema_class=FreeSlotsResponse,
    examples=examples["/hilvl/get_free_slots"]
)
async def get_free_slots(
    params: Dict[str, Any] = Body(...),
    service: HilvlService = Depends(get_hilvl_service)
):
    """Get free slots for a calendar"""
    validated_params = GetFreeSlotsParams(**params)
    return service.get_free_slots(
        validated_params.calendar_id,
        validated_params.start_date,
        validated_params.end_date,
        validated_params.timezone,
        validated_params.user_id,
        validated_params.user_ids,
        validated_params.enable_look_busy
    )

@router.post("/create_block_slot", response_model=ApiResponse)
@schema(
    input_schema_class=CreateBlockSlotParams,
    output_schema_class=BlockSlotResponse,
    examples=examples["/hilvl/create_block_slot"]
)
async def create_block_slot(
    params: Dict[str, Any] = Body(...),
    service: HilvlService = Depends(get_hilvl_service)
):
    """Create a blocked time slot on a calendar"""
    validated_params = CreateBlockSlotParams(**params)
    return service.create_block_slot(validated_params.model_dump(exclude_none=True))

# Contact endpoints
@router.post("/get_contact", response_model=ApiResponse)
@schema(
    input_schema_class=GetContactParams,
    output_schema_class=ContactResponse,
    examples=examples["/hilvl/get_contact"]
)
async def get_contact(
    params: Dict[str, Any] = Body(...),
    service: HilvlService = Depends(get_hilvl_service)
):
    """Get contact details"""
    validated_params = GetContactParams(**params)
    return service.get_contact(validated_params.contact_id)

@router.post("/get_contacts_by_business", response_model=ApiResponse)
@schema(
    input_schema_class=GetContactsByBusinessParams,
    output_schema_class=ContactsResponse,
    examples=examples["/hilvl/get_contacts_by_business"]
)
async def get_contacts_by_business(
    params: Dict[str, Any] = Body(...),
    service: HilvlService = Depends(get_hilvl_service)
):
    """Get contacts by business"""
    validated_params = GetContactsByBusinessParams(**params)
    return service.get_contacts_by_business(
        validated_params.business_id,
        validated_params.location_id,
        validated_params.limit,
        validated_params.skip,
        validated_params.query
    )

@router.post("/create_contact", response_model=ApiResponse)
@schema(
    input_schema_class=CreateContactParams,
    output_schema_class=CreateContactResponse,
    examples=examples["/hilvl/create_contact"]
)
async def create_contact(
    params: Dict[str, Any] = Body(...),
    service: HilvlService = Depends(get_hilvl_service)
):
    """Create a new contact"""
    validated_params = CreateContactParams(**params)
    return service.create_contact(validated_params.model_dump(exclude_none=True))

@router.post("/update_contact", response_model=ApiResponse)
@schema(
    input_schema_class=UpdateContactParams,
    output_schema_class=UpdateContactResponse,
    examples=examples["/hilvl/update_contact"]
)
async def update_contact(
    params: Dict[str, Any] = Body(...),
    service: HilvlService = Depends(get_hilvl_service)
):
    """Update an existing contact"""
    validated_params = UpdateContactParams(**params)
    contact_id = validated_params.contact_id
    data = validated_params.model_dump(exclude={"contact_id"}, exclude_none=True)
    return service.update_contact(contact_id, data)

@router.post("/delete_contact", response_model=ApiResponse)
@schema(
    input_schema_class=DeleteContactParams,
    output_schema_class=DeleteContactResponse,
    examples=examples["/hilvl/delete_contact"]
)
async def delete_contact(
    params: Dict[str, Any] = Body(...),
    service: HilvlService = Depends(get_hilvl_service)
):
    """Delete a contact"""
    validated_params = DeleteContactParams(**params)
    return service.delete_contact(validated_params.contact_id)

@router.post("/upsert_contact", response_model=ApiResponse)
@schema(
    input_schema_class=UpsertContactParams,
    output_schema_class=UpsertContactResponse,
    examples=examples["/hilvl/upsert_contact"]
)
async def upsert_contact(
    params: Dict[str, Any] = Body(...),
    service: HilvlService = Depends(get_hilvl_service)
):
    """Upsert a contact (create if not exists, update if exists)"""
    validated_params = UpsertContactParams(**params)
    return service.upsert_contact(validated_params.model_dump(exclude_none=True))

# Task endpoints
@router.post("/get_tasks", response_model=ApiResponse)
@schema(
    input_schema_class=GetTasksParams,
    output_schema_class=TasksResponse,
    examples=examples["/hilvl/get_tasks"]
)
async def get_tasks(
    params: Dict[str, Any] = Body(...),
    service: HilvlService = Depends(get_hilvl_service)
):
    """Get tasks for a contact"""
    task_params = GetTasksParams(**params)
    return await service.get_tasks(task_params)

@router.post("/get_task", response_model=ApiResponse)
@schema(
    input_schema_class=GetTaskParams,
    output_schema_class=TaskResponse,
    examples=examples["/hilvl/get_task"]
)
async def get_task(
    params: Dict[str, Any] = Body(...),
    service: HilvlService = Depends(get_hilvl_service)
):
    """Get a specific task for a contact"""
    task_params = GetTaskParams(**params)
    return await service.get_task(task_params)

@router.post("/create_task", response_model=ApiResponse)
@schema(
    input_schema_class=CreateTaskParams,
    output_schema_class=CreateTaskResponse,
    examples=examples["/hilvl/create_task"]
)
async def create_task(
    params: Dict[str, Any] = Body(...),
    service: HilvlService = Depends(get_hilvl_service)
):
    """Create a new task for a contact"""
    task_params = CreateTaskParams(**params)
    return await service.create_task(task_params)

@router.post("/update_task", response_model=ApiResponse)
@schema(
    input_schema_class=UpdateTaskParams,
    output_schema_class=UpdateTaskResponse,
    examples=examples["/hilvl/update_task"]
)
async def update_task(
    params: Dict[str, Any] = Body(...),
    service: HilvlService = Depends(get_hilvl_service)
):
    """Update an existing task for a contact"""
    task_params = UpdateTaskParams(**params)
    return await service.update_task(task_params)

@router.post("/delete_task", response_model=ApiResponse)
@schema(
    input_schema_class=DeleteTaskParams,
    output_schema_class=DeleteTaskResponse,
    examples=examples["/hilvl/delete_task"]
)
async def delete_task(
    params: Dict[str, Any] = Body(...),
    service: HilvlService = Depends(get_hilvl_service)
):
    """Delete a task for a contact"""
    task_params = DeleteTaskParams(**params)
    return await service.delete_task(task_params)

@router.post("/update_task_completed", response_model=ApiResponse)
@schema(
    input_schema_class=UpdateTaskCompletedParams,
    output_schema_class=UpdateTaskCompletedResponse,
    examples=examples["/hilvl/update_task_completed"]
)
async def update_task_completed(
    params: Dict[str, Any] = Body(...),
    service: HilvlService = Depends(get_hilvl_service)
):
    """Update task completion status"""
    task_params = UpdateTaskCompletedParams(**params)
    return await service.update_task_completed(task_params)

# Appointment endpoints
@router.post("/get_appointments", response_model=ApiResponse)
@schema(
    input_schema_class=GetAppointmentsParams,
    output_schema_class=AppointmentsResponse,
    examples=examples["/hilvl/get_appointments"]
)
async def get_appointments(
    params: Dict[str, Any] = Body(...),
    service: HilvlService = Depends(get_hilvl_service)
):
    """Get appointments for a contact"""
    appointment_params = GetAppointmentsParams(**params)
    return await service.get_appointments(appointment_params)

# Tag endpoints
@router.post("/add_tags", response_model=ApiResponse)
@schema(
    input_schema_class=AddTagsParams,
    output_schema_class=TagsResponse,
    examples=examples["/hilvl/add_tags"]
)
async def add_tags(
    params: Dict[str, Any] = Body(...),
    service: HilvlService = Depends(get_hilvl_service)
):
    """Add tags to a contact"""
    tag_params = AddTagsParams(**params)
    return await service.add_tags(tag_params)

@router.post("/remove_tags", response_model=ApiResponse)
@schema(
    input_schema_class=RemoveTagsParams,
    output_schema_class=TagsResponse,
    examples=examples["/hilvl/remove_tags"]
)
async def remove_tags(
    params: Dict[str, Any] = Body(...),
    service: HilvlService = Depends(get_hilvl_service)
):
    """Remove tags from a contact"""
    tag_params = RemoveTagsParams(**params)
    return await service.remove_tags(tag_params)

# Note endpoints
@router.post("/get_notes", response_model=ApiResponse)
@schema(
    input_schema_class=GetNotesParams,
    output_schema_class=NotesResponse,
    examples=examples["/hilvl/get_notes"]
)
async def get_notes(
    params: Dict[str, Any] = Body(...),
    service: HilvlService = Depends(get_hilvl_service)
):
    """Get all notes for a contact"""
    note_params = GetNotesParams(**params)
    return await service.get_notes(note_params)

@router.post("/get_note", response_model=ApiResponse)
@schema(
    input_schema_class=GetNoteParams,
    output_schema_class=NoteResponse,
    examples=examples["/hilvl/get_note"]
)
async def get_note(
    params: Dict[str, Any] = Body(...),
    service: HilvlService = Depends(get_hilvl_service)
):
    """Get a specific note for a contact"""
    note_params = GetNoteParams(**params)
    return await service.get_note(note_params)

@router.post("/create_note", response_model=ApiResponse)
@schema(
    input_schema_class=CreateNoteParams,
    output_schema_class=CreateNoteResponse,
    examples=examples["/hilvl/create_note"]
)
async def create_note(
    params: Dict[str, Any] = Body(...),
    service: HilvlService = Depends(get_hilvl_service)
):
    """Create a new note for a contact"""
    note_params = CreateNoteParams(**params)
    return await service.create_note(note_params)

@router.post("/update_note", response_model=ApiResponse)
@schema(
    input_schema_class=UpdateNoteParams,
    output_schema_class=UpdateNoteResponse,
    examples=examples["/hilvl/update_note"]
)
async def update_note(
    params: Dict[str, Any] = Body(...),
    service: HilvlService = Depends(get_hilvl_service)
):
    """Update an existing note for a contact"""
    note_params = UpdateNoteParams(**params)
    return await service.update_note(note_params)

@router.post("/delete_note", response_model=ApiResponse)
@schema(
    input_schema_class=DeleteNoteParams,
    output_schema_class=DeleteNoteResponse,
    examples=examples["/hilvl/delete_note"]
)
async def delete_note(
    params: Dict[str, Any] = Body(...),
    service: HilvlService = Depends(get_hilvl_service)
):
    """Delete a note for a contact"""
    note_params = DeleteNoteParams(**params)
    return await service.delete_note(note_params)

# Campaign endpoints
@router.post("/add_contact_to_campaign", response_model=ApiResponse)
@schema(
    input_schema_class=AddContactToCampaignParams,
    output_schema_class=CampaignSuccessResponse,
    examples=examples["/hilvl/add_contact_to_campaign"]
)
async def add_contact_to_campaign(
    params: Dict[str, Any] = Body(...),
    service: HilvlService = Depends(get_hilvl_service)
):
    """Add a contact to a campaign"""
    campaign_params = AddContactToCampaignParams(**params)
    return await service.add_contact_to_campaign(campaign_params)

@router.post("/remove_contact_from_campaign", response_model=ApiResponse)
@schema(
    input_schema_class=RemoveContactFromCampaignParams,
    output_schema_class=CampaignSuccessResponse,
    examples=examples["/hilvl/remove_contact_from_campaign"]
)
async def remove_contact_from_campaign(
    params: Dict[str, Any] = Body(...),
    service: HilvlService = Depends(get_hilvl_service)
):
    """Remove a contact from a campaign"""
    campaign_params = RemoveContactFromCampaignParams(**params)
    return await service.remove_contact_from_campaign(campaign_params)

@router.post("/remove_contact_from_all_campaigns", response_model=ApiResponse)
@schema(
    input_schema_class=RemoveContactFromAllCampaignsParams,
    output_schema_class=CampaignSuccessResponse,
    examples=examples["/hilvl/remove_contact_from_all_campaigns"]
)
async def remove_contact_from_all_campaigns(
    params: Dict[str, Any] = Body(...),
    service: HilvlService = Depends(get_hilvl_service)
):
    """Remove a contact from all campaigns"""
    campaign_params = RemoveContactFromAllCampaignsParams(**params)
    return await service.remove_contact_from_all_campaigns(campaign_params)

# Workflow endpoints
@router.post("/add_contact_to_workflow", response_model=ApiResponse)
@schema(
    input_schema_class=AddContactToWorkflowParams,
    output_schema_class=WorkflowSuccessResponse,
    examples=examples["/hilvl/add_contact_to_workflow"]
)
async def add_contact_to_workflow(
    params: Dict[str, Any] = Body(...),
    service: HilvlService = Depends(get_hilvl_service)
):
    """Add a contact to a workflow"""
    workflow_params = AddContactToWorkflowParams(**params)
    return await service.add_contact_to_workflow(workflow_params)

@router.post("/remove_contact_from_workflow", response_model=ApiResponse)
@schema(
    input_schema_class=RemoveContactFromWorkflowParams,
    output_schema_class=WorkflowSuccessResponse,
    examples=examples["/hilvl/remove_contact_from_workflow"]
)
async def remove_contact_from_workflow(
    params: Dict[str, Any] = Body(...),
    service: HilvlService = Depends(get_hilvl_service)
):
    """Remove a contact from a workflow"""
    workflow_params = RemoveContactFromWorkflowParams(**params)
    return await service.remove_contact_from_workflow(workflow_params)

# Bulk Contact Operations endpoints
@router.post("/update_contacts_tags", response_model=ApiResponse)
@schema(
    input_schema_class=BulkTagUpdateParams,
    output_schema_class=BulkTagUpdateResponse,
    examples=examples["/hilvl/update_contacts_tags"]
)
async def update_contacts_tags(
    params: Dict[str, Any] = Body(...),
    service: HilvlService = Depends(get_hilvl_service)
):
    """Update tags for multiple contacts at once (add or remove)"""
    # Extract required parameters
    operation_type = params.pop('operation_type', None)
    contacts = params.pop('contacts', None)
    tags = params.pop('tags', None)
    location_id = params.pop('location_id', None)
    remove_all_tags = params.pop('remove_all_tags', False)
    
    bulk_params = BulkTagUpdateParams(
        operation_type=operation_type,
        contacts=contacts,
        tags=tags,
        location_id=location_id,
        remove_all_tags=remove_all_tags
    )
    return await service.update_contacts_tags(bulk_params)

@router.post("/update_contacts_business", response_model=ApiResponse)
@schema(
    input_schema_class=BulkBusinessUpdateParams,
    output_schema_class=BulkBusinessUpdateResponse,
    examples=examples["/hilvl/update_contacts_business"]
)
async def update_contacts_business(
    params: Dict[str, Any] = Body(...),
    service: HilvlService = Depends(get_hilvl_service)
):
    """Add/remove contacts from a business"""
    bulk_params = BulkBusinessUpdateParams(**params)
    return await service.update_contacts_business(bulk_params)

# Contact Search endpoints
@router.post("/search_contacts", response_model=ApiResponse)
@schema(
    input_schema_class=ContactSearchParams,
    output_schema_class=ContactSearchResponse,
    examples=examples["/hilvl/search_contacts"]
)
async def search_contacts(
    params: Dict[str, Any] = Body(...),
    service: HilvlService = Depends(get_hilvl_service)
):
    """Search contacts based on advanced filters"""
    # Extract required location_id parameter
    location_id = params.pop('location_id', None)
    if not location_id:
        raise HTTPException(status_code=400, detail="location_id is required")
    
    # Extract common parameters
    search_params = ContactSearchParams(
        location_id=location_id,
        query=params.pop('query', None),
        assignedTo=params.pop('assignedTo', None),
        tags=params.pop('tags', None),
        businessId=params.pop('businessId', None),
        source=params.pop('source', None),
        type=params.pop('type', None),
        dnd=params.pop('dnd', None),
        limit=params.pop('limit', None),
        skip=params.pop('skip', None),
        page=params.pop('page', None),
        page_size=params.pop('page_size', None),
        sort_by=params.pop('sort_by', None),
        sort_dir=params.pop('sort_dir', None),
        search_params=params  # All remaining parameters go to search_params
    )
    
    return await service.search_contacts(search_params)

@router.post("/get_duplicate_contact", response_model=ApiResponse)
@schema(
    input_schema_class=GetDuplicateContactParams,
    output_schema_class=ContactSearchResult,
    examples=examples["/hilvl/get_duplicate_contact"]
)
async def get_duplicate_contact(
    params: Dict[str, Any] = Body(...),
    service: HilvlService = Depends(get_hilvl_service)
):
    """Get duplicate contact by email or phone number"""
    duplicate_params = GetDuplicateContactParams(**params)
    return await service.get_duplicate_contact(duplicate_params)

# Followers endpoints
@router.post("/add_followers", response_model=ApiResponse)
@schema(
    input_schema_class=AddFollowersParams,
    output_schema_class=FollowersResponse,
    examples=examples["/hilvl/add_followers"]
)
async def add_followers(
    params: Dict[str, Any] = Body(...),
    service: HilvlService = Depends(get_hilvl_service)
):
    """Add followers to a contact"""
    followers_params = AddFollowersParams(**params)
    return await service.add_followers(followers_params)

@router.post("/remove_followers", response_model=ApiResponse)
@schema(
    input_schema_class=RemoveFollowersParams,
    output_schema_class=FollowersResponse,
    examples=examples["/hilvl/remove_followers"]
)
async def remove_followers(
    params: Dict[str, Any] = Body(...),
    service: HilvlService = Depends(get_hilvl_service)
):
    """Remove followers from a contact"""
    followers_params = RemoveFollowersParams(**params)
    return await service.remove_followers(followers_params)

# Conversation endpoints
@router.post("/get_conversation", response_model=ApiResponse)
@schema(
    input_schema_class=GetConversationParams,
    output_schema_class=Conversation,
    examples=examples["/hilvl/get_conversation"]
)
async def get_conversation(
    params: Dict[str, Any] = Body(...),
    service: HilvlService = Depends(get_hilvl_service)
):
    """
    Get conversation details
    """
    get_conversation_params = GetConversationParams(**params)
    return await service.get_conversation(get_conversation_params)

@router.post("/update_conversation", response_model=ApiResponse)
@schema(
    input_schema_class=UpdateConversationParams,
    output_schema_class=ConversationSuccess,
    examples=examples["/hilvl/update_conversation"]
)
async def update_conversation(
    params: Dict[str, Any] = Body(...),
    service: HilvlService = Depends(get_hilvl_service)
):
    """
    Update conversation details
    """
    update_params = UpdateConversationParams(**params)
    return await service.update_conversation(update_params)

@router.post("/delete_conversation", response_model=ApiResponse)
@schema(
    input_schema_class=DeleteConversationParams,
    output_schema_class=ConversationSuccess,
    examples=examples["/hilvl/delete_conversation"]
)
async def delete_conversation(
    params: Dict[str, Any] = Body(...),
    service: HilvlService = Depends(get_hilvl_service)
):
    """
    Delete a conversation
    """
    delete_params = DeleteConversationParams(**params)
    return await service.delete_conversation(delete_params)

@router.post("/create_conversation", response_model=ApiResponse)
@schema(
    input_schema_class=CreateConversationParams,
    output_schema_class=ConversationSuccess,
    examples=examples["/hilvl/create_conversation"]
)
async def create_conversation(
    params: Dict[str, Any] = Body(...),
    service: HilvlService = Depends(get_hilvl_service)
):
    """
    Create a new conversation
    """
    create_params = CreateConversationParams(**params)
    return await service.create_conversation(create_params)

@router.post("/search_conversations", response_model=ApiResponse)
@schema(
    input_schema_class=SearchConversationsParams,
    output_schema_class=ConversationsSearchResponse,
    examples=examples["/hilvl/search_conversations"]
)
async def search_conversations(
    params: Dict[str, Any] = Body(...),
    service: HilvlService = Depends(get_hilvl_service)
):
    """
    Search conversations
    """
    # Extract required location_id parameter
    location_id = params.pop('location_id', None)
    if not location_id:
        raise HTTPException(status_code=400, detail="location_id is required")
    
    # Create search params object with all possible parameters
    search_params = SearchConversationsParams(
        location_id=location_id,
        assigned_to=params.get('assigned_to'),
        contact_id=params.get('contact_id'),
        followers=params.get('followers'),
        conversation_id=params.get('conversation_id'),
        last_message_action=params.get('last_message_action'),
        last_message_direction=params.get('last_message_direction'),
        last_message_type=params.get('last_message_type'),
        limit=params.get('limit'),
        mentions=params.get('mentions'),
        query=params.get('query'),
        score_profile=params.get('score_profile'),
        score_profile_min=params.get('score_profile_min'),
        score_profile_max=params.get('score_profile_max'),
        sort=params.get('sort'),
        sort_by=params.get('sort_by'),
        sort_score_profile=params.get('sort_score_profile'),
        start_after_date=params.get('start_after_date'),
        status=params.get('status'),
        page=params.get('page'),
        page_size=params.get('page_size')
    )
    
    return await service.search_conversations(search_params)

@router.post("/get_message", response_model=ApiResponse)
@schema(
    input_schema_class=GetMessageByIdParams,
    output_schema_class=ConversationMessage,
    examples=examples["/hilvl/get_message"]
)
async def get_message(
    params: Dict[str, Any] = Body(...),
    service: HilvlService = Depends(get_hilvl_service)
):
    """
    Get message details by message ID
    """
    get_message_params = GetMessageByIdParams(**params)
    return await service.get_message_by_id(get_message_params)

@router.post("/get_email_message", response_model=ApiResponse)
@schema(
    input_schema_class=GetEmailByIdParams,
    output_schema_class=EmailMessage,
    examples=examples["/hilvl/get_email_message"]
)
async def get_email_message(
    params: Dict[str, Any] = Body(...),
    service: HilvlService = Depends(get_hilvl_service)
):
    """
    Get email message details by email ID
    """
    get_email_params = GetEmailByIdParams(**params)
    return await service.get_email_by_id(get_email_params)

@router.post("/cancel_scheduled_email", response_model=ApiResponse)
@schema(
    input_schema_class=CancelScheduledEmailParams,
    output_schema_class=CancelEmailResult,
    examples=examples["/hilvl/cancel_scheduled_email"]
)
async def cancel_scheduled_email(
    params: Dict[str, Any] = Body(...),
    service: HilvlService = Depends(get_hilvl_service)
):
    """
    Cancel a scheduled email
    """
    cancel_params = CancelScheduledEmailParams(**params)
    return await service.cancel_scheduled_email(cancel_params)

@router.post("/get_conversation_messages", response_model=ApiResponse)
@schema(
    input_schema_class=GetMessagesByConversationParams,
    output_schema_class=ConversationMessagesList,
    examples=examples["/hilvl/get_conversation_messages"]
)
async def get_conversation_messages(
    params: Dict[str, Any] = Body(...),
    service: HilvlService = Depends(get_hilvl_service)
):
    """
    Get messages for a specific conversation
    """
    # Extract required conversation_id parameter
    conversation_id = params.get('conversation_id')
    if not conversation_id:
        raise HTTPException(status_code=400, detail="conversation_id is required")
    
    # Create params object with all possible parameters
    get_messages_params = GetMessagesByConversationParams(
        conversation_id=conversation_id,
        last_message_id=params.get('last_message_id'),
        limit=params.get('limit'),
        message_types=params.get('message_types'),
        direction=params.get('direction'),
        status=params.get('status'),
        from_date=params.get('from_date'),
        to_date=params.get('to_date'),
        sort_by=params.get('sort_by'),
        sort_dir=params.get('sort_dir')
    )
    
    return await service.get_messages_by_conversation_id(get_messages_params)

@router.post("/send_message", response_model=ApiResponse)
@schema(
    input_schema_class=SendMessageParams,
    output_schema_class=SendMessageResponse,
    examples=examples["/hilvl/send_message"]
)
async def send_message(
    params: Dict[str, Any] = Body(...),
    service: HilvlService = Depends(get_hilvl_service)
):
    """
    Send a message
    """
    send_message_params = SendMessageParams(**params)
    return await service.send_message(send_message_params)

apply_error_handler_to_router(router)
