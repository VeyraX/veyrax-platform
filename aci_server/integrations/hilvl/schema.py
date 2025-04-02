from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Union, Literal

# Common Business Models
class Business(BaseModel):
    id: str
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    description: Optional[str] = None
    state: Optional[str] = None
    postalCode: Optional[str] = None
    country: Optional[str] = None
    updatedBy: Optional[Dict[str, Any]] = None
    locationId: str
    createdBy: Optional[Dict[str, Any]] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None

class BusinessList(BaseModel):
    businesses: List[Business]

# Input schemas
class GetBusinessParams(BaseModel):
    business_id: str = Field(..., description="Business ID")

class GetBusinessesByLocationParams(BaseModel):
    location_id: str = Field(..., description="Location ID")

class CreateBusinessParams(BaseModel):
    name: str = Field(..., description="Business name")
    locationId: str = Field(..., description="Location ID")
    phone: Optional[str] = Field(None, description="Phone number")
    email: Optional[str] = Field(None, description="Email address")
    website: Optional[str] = Field(None, description="Website URL")
    address: Optional[str] = Field(None, description="Street address")
    city: Optional[str] = Field(None, description="City")
    postalCode: Optional[str] = Field(None, description="Postal code")
    state: Optional[str] = Field(None, description="State")
    country: Optional[str] = Field(None, description="Country")
    description: Optional[str] = Field(None, description="Business description")

class UpdateBusinessParams(BaseModel):
    business_id: str = Field(..., description="Business ID")
    name: Optional[str] = Field(None, description="Business name")
    phone: Optional[str] = Field(None, description="Phone number")
    email: Optional[str] = Field(None, description="Email address")
    website: Optional[str] = Field(None, description="Website URL")
    address: Optional[str] = Field(None, description="Street address")
    city: Optional[str] = Field(None, description="City")
    postalCode: Optional[str] = Field(None, description="Postal code")
    state: Optional[str] = Field(None, description="State")
    country: Optional[str] = Field(None, description="Country")
    description: Optional[str] = Field(None, description="Business description")

class DeleteBusinessParams(BaseModel):
    business_id: str = Field(..., description="Business ID")

# Response schemas
class SuccessResponse(BaseModel):
    success: bool

class BusinessResponse(BaseModel):
    business: Business

class BusinessesResponse(BaseModel):
    businesses: List[Business]

class CreateBusinessResponse(BaseModel):
    success: bool
    buiseness: Business  # Note: keeping misspelled field to match API response

class UpdateBusinessResponse(BaseModel):
    success: bool
    buiseness: Business  # Note: keeping misspelled field to match API response

class DeleteBusinessResponse(BaseModel):
    success: bool

# Calendar Models
class Hour(BaseModel):
    openHour: int
    openMinute: int
    closeHour: int
    closeMinute: int

class OpenHours(BaseModel):
    daysOfTheWeek: List[int]
    hours: List[Hour]

class Availability(BaseModel):
    date: str
    hours: List[Hour]
    deleted: Optional[bool] = False
    id: Optional[str] = None

class TeamMember(BaseModel):
    userId: str
    priority: Optional[float] = 0.5
    meetingLocationType: Optional[str] = "custom"
    meetingLocation: Optional[str] = None
    isPrimary: Optional[bool] = None

class LookBusyConfig(BaseModel):
    enabled: bool
    LookBusyPercentage: int

class Notification(BaseModel):
    type: str = "email"
    shouldSendToContact: bool
    shouldSendToGuest: bool
    shouldSendToUser: bool
    shouldSendToSelectedUsers: bool
    selectedUsers: str

class Recurring(BaseModel):
    freq: Optional[str] = None
    count: Optional[int] = None
    bookingOption: Optional[str] = None
    bookingOverlapDefaultStatus: Optional[str] = None

class Calendar(BaseModel):
    id: str
    isActive: Optional[bool] = True
    notifications: Optional[List[Notification]] = None
    locationId: str
    groupId: Optional[str] = None
    teamMembers: Optional[List[TeamMember]] = None
    eventType: Optional[str] = None
    name: str
    description: Optional[str] = None
    slug: Optional[str] = None
    widgetSlug: Optional[str] = None
    calendarType: Optional[str] = None
    widgetType: Optional[str] = "classic"
    eventTitle: Optional[str] = None
    eventColor: Optional[str] = "#039be5"
    meetingLocation: Optional[str] = None
    slotDuration: Optional[int] = 30
    slotDurationUnit: Optional[str] = "mins"
    slotInterval: Optional[int] = 30
    slotIntervalUnit: Optional[str] = "mins"
    slotBuffer: Optional[int] = None
    slotBufferUnit: Optional[str] = None
    preBuffer: Optional[int] = None
    preBufferUnit: Optional[str] = None
    appoinmentPerSlot: Optional[int] = 1
    appoinmentPerDay: Optional[int] = None
    allowBookingAfter: Optional[int] = None
    allowBookingAfterUnit: Optional[str] = None
    allowBookingFor: Optional[int] = None
    allowBookingForUnit: Optional[str] = None
    openHours: Optional[List[OpenHours]] = None
    enableRecurring: Optional[bool] = False
    recurring: Optional[Recurring] = None
    formId: Optional[str] = None
    stickyContact: Optional[bool] = None
    isLivePaymentMode: Optional[bool] = None
    autoConfirm: Optional[bool] = True
    shouldSendAlertEmailsToAssignedMember: Optional[bool] = None
    alertEmail: Optional[str] = None
    googleInvitationEmails: Optional[bool] = False
    allowReschedule: Optional[bool] = True
    allowCancellation: Optional[bool] = True
    shouldAssignContactToTeamMember: Optional[bool] = None
    shouldSkipAssigningContactForExisting: Optional[bool] = None
    notes: Optional[str] = None
    pixelId: Optional[str] = None
    formSubmitType: Optional[str] = "ThankYouMessage"
    formSubmitRedirectURL: Optional[str] = None
    formSubmitThanksMessage: Optional[str] = None
    availabilityType: Optional[int] = None
    availabilities: Optional[List[Availability]] = None
    guestType: Optional[str] = None
    consentLabel: Optional[str] = None
    calendarCoverImage: Optional[str] = None
    lookBusyConfig: Optional[LookBusyConfig] = None

class CalendarList(BaseModel):
    calendars: List[Calendar]

class BlockSlot(BaseModel):
    id: str
    locationId: str
    title: str
    startTime: str
    endTime: str
    calendarId: Optional[str] = None
    assignedUserId: Optional[str] = None

class FreeSlotsData(BaseModel):
    slots: List[str]

class FreeSlots(BaseModel):
    _dates_: FreeSlotsData

# Input schemas - Calendar
class GetCalendarsParams(BaseModel):
    location_id: str = Field(..., description="Location ID")
    group_id: Optional[str] = Field(None, description="Group ID")
    show_drafted: Optional[bool] = Field(True, description="Show drafted calendars")

class GetCalendarParams(BaseModel):
    calendar_id: str = Field(..., description="Calendar ID")

class CreateCalendarParams(BaseModel):
    locationId: str = Field(..., description="Location ID")
    name: str = Field(..., description="Calendar name")
    isActive: Optional[bool] = Field(True, description="Is calendar active")
    notifications: Optional[List[Dict[str, Any]]] = Field(None, description="Calendar notifications")
    groupId: Optional[str] = Field(None, description="Group ID")
    teamMembers: Optional[List[Dict[str, Any]]] = Field(None, description="Team members")
    description: Optional[str] = Field(None, description="Calendar description")
    eventType: Optional[str] = Field(None, description="Event type")
    widgetType: Optional[str] = Field("classic", description="Widget type")
    calendarType: Optional[str] = Field(None, description="Calendar type")

class UpdateCalendarParams(BaseModel):
    calendar_id: str = Field(..., description="Calendar ID")
    name: Optional[str] = Field(None, description="Calendar name")
    notifications: Optional[List[Dict[str, Any]]] = Field(None, description="Calendar notifications")
    teamMembers: Optional[List[Dict[str, Any]]] = Field(None, description="Team members")
    description: Optional[str] = Field(None, description="Calendar description")
    eventType: Optional[str] = Field(None, description="Event type")
    widgetType: Optional[str] = Field(None, description="Widget type")

class DeleteCalendarParams(BaseModel):
    calendar_id: str = Field(..., description="Calendar ID")

class GetFreeSlotsParams(BaseModel):
    calendar_id: str = Field(..., description="Calendar ID")
    start_date: int = Field(..., description="Start date timestamp in milliseconds")
    end_date: int = Field(..., description="End date timestamp in milliseconds")
    timezone: Optional[str] = Field(None, description="Timezone")
    user_id: Optional[str] = Field(None, description="User ID")
    user_ids: Optional[List[str]] = Field(None, description="List of user IDs")
    enable_look_busy: Optional[bool] = Field(False, description="Enable look busy")

class CreateBlockSlotParams(BaseModel):
    calendarId: str = Field(..., description="Calendar ID")
    locationId: str = Field(..., description="Location ID")
    startTime: str = Field(..., description="Start time")
    endTime: str = Field(..., description="End time")
    title: Optional[str] = Field(None, description="Title")
    assignedUserId: Optional[str] = Field(None, description="Assigned user ID")

# Response schemas - Calendar
class CalendarResponse(BaseModel):
    calendar: Calendar

class CalendarsResponse(BaseModel):
    calendars: List[Calendar]

class CreateCalendarResponse(BaseModel):
    calendar: Calendar

class UpdateCalendarResponse(BaseModel):
    calendar: Calendar

class FreeSlotsResponse(BaseModel):
    _dates_: FreeSlotsData

class BlockSlotResponse(BaseModel):
    id: str
    locationId: str
    title: str
    startTime: str
    endTime: str
    calendarId: Optional[str] = None
    assignedUserId: Optional[str] = None

# Contact Models
class DndSettingDetail(BaseModel):
    status: Optional[str] = None
    message: Optional[str] = None
    code: Optional[str] = None

class DndChannelSettings(BaseModel):
    Call: Optional[DndSettingDetail] = None
    Email: Optional[DndSettingDetail] = None
    SMS: Optional[DndSettingDetail] = None
    WhatsApp: Optional[DndSettingDetail] = None
    GMB: Optional[DndSettingDetail] = None
    FB: Optional[DndSettingDetail] = None

class InboundDndSettings(BaseModel):
    all: Optional[Dict[str, Any]] = None

class AttributionSource(BaseModel):
    url: Optional[str] = None
    campaign: Optional[str] = None
    utmSource: Optional[str] = None
    utmMedium: Optional[str] = None
    utmContent: Optional[str] = None
    referrer: Optional[str] = None
    campaignId: Optional[str] = None
    fbclid: Optional[str] = None
    gclid: Optional[str] = None
    msclikid: Optional[str] = None
    dclid: Optional[str] = None
    fbc: Optional[str] = None
    fbp: Optional[str] = None
    fbEventId: Optional[str] = None
    userAgent: Optional[str] = None
    ip: Optional[str] = None
    medium: Optional[str] = None
    mediumId: Optional[str] = None

class CustomField(BaseModel):
    id: Optional[str] = None
    value: Optional[str] = None
    key: Optional[str] = None
    field_value: Optional[str] = None

class Contact(BaseModel):
    id: str
    name: Optional[str] = None
    locationId: str
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    email: Optional[str] = None
    emailLowerCase: Optional[str] = None
    timezone: Optional[str] = None
    companyName: Optional[str] = None
    phone: Optional[str] = None
    dnd: Optional[bool] = None
    dndSettings: Optional[DndChannelSettings] = None
    type: Optional[str] = None
    source: Optional[str] = None
    assignedTo: Optional[str] = None
    address1: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postalCode: Optional[str] = None
    website: Optional[str] = None
    tags: Optional[List[str]] = None
    dateOfBirth: Optional[str] = None
    dateAdded: Optional[str] = None
    dateUpdated: Optional[str] = None
    attachments: Optional[str] = None
    ssn: Optional[str] = None
    keyword: Optional[str] = None
    firstNameLowerCase: Optional[str] = None
    fullNameLowerCase: Optional[str] = None
    lastNameLowerCase: Optional[str] = None
    lastActivity: Optional[str] = None
    customFields: Optional[List[CustomField]] = None
    businessId: Optional[str] = None
    attributionSource: Optional[AttributionSource] = None
    lastAttributionSource: Optional[AttributionSource] = None
    visitorId: Optional[str] = None
    gender: Optional[str] = None
    deleted: Optional[bool] = None
    bounceEmail: Optional[bool] = None
    unsubscribeEmail: Optional[bool] = None
    birthMonth: Optional[int] = None
    birthDay: Optional[int] = None
    lastSessionActivityAt: Optional[str] = None
    offers: Optional[List[str]] = None
    products: Optional[List[str]] = None

class ContactList(BaseModel):
    contacts: List[Contact]
    count: Optional[int] = None

# Input schemas - Contact
class GetContactParams(BaseModel):
    contact_id: str = Field(..., description="Contact ID")

class GetContactsByBusinessParams(BaseModel):
    business_id: str = Field(..., description="Business ID")
    location_id: str = Field(..., description="Location ID")
    limit: Optional[int] = Field(25, description="Limit")
    skip: Optional[int] = Field(0, description="Skip")
    query: Optional[str] = Field(None, description="Search query")

class CreateContactParams(BaseModel):
    firstName: Optional[str] = Field(None, description="First name")
    lastName: Optional[str] = Field(None, description="Last name")
    name: Optional[str] = Field(None, description="Full name")
    email: Optional[str] = Field(None, description="Email")
    locationId: str = Field(..., description="Location ID")
    gender: Optional[str] = Field(None, description="Gender")
    phone: Optional[str] = Field(None, description="Phone number")
    address1: Optional[str] = Field(None, description="Address")
    city: Optional[str] = Field(None, description="City")
    state: Optional[str] = Field(None, description="State")
    postalCode: Optional[str] = Field(None, description="Postal code")
    website: Optional[str] = Field(None, description="Website URL")
    timezone: Optional[str] = Field(None, description="Timezone")
    dnd: Optional[bool] = Field(None, description="Do not disturb")
    dndSettings: Optional[Dict[str, Any]] = Field(None, description="DND settings")
    inboundDndSettings: Optional[Dict[str, Any]] = Field(None, description="Inbound DND settings")
    tags: Optional[List[str]] = Field(None, description="Tags")
    customFields: Optional[List[Dict[str, Any]]] = Field(None, description="Custom fields")
    source: Optional[str] = Field(None, description="Source")
    country: Optional[str] = Field(None, description="Country")
    companyName: Optional[str] = Field(None, description="Company name")
    assignedTo: Optional[str] = Field(None, description="Assigned to user ID")

class UpdateContactParams(BaseModel):
    contact_id: str = Field(..., description="Contact ID")
    firstName: Optional[str] = Field(None, description="First name")
    lastName: Optional[str] = Field(None, description="Last name")
    name: Optional[str] = Field(None, description="Full name")
    email: Optional[str] = Field(None, description="Email")
    phone: Optional[str] = Field(None, description="Phone number")
    address1: Optional[str] = Field(None, description="Address")
    city: Optional[str] = Field(None, description="City")
    state: Optional[str] = Field(None, description="State")
    postalCode: Optional[str] = Field(None, description="Postal code")
    website: Optional[str] = Field(None, description="Website URL")
    timezone: Optional[str] = Field(None, description="Timezone")
    dnd: Optional[bool] = Field(None, description="Do not disturb")
    dndSettings: Optional[Dict[str, Any]] = Field(None, description="DND settings")
    inboundDndSettings: Optional[Dict[str, Any]] = Field(None, description="Inbound DND settings")
    tags: Optional[List[str]] = Field(None, description="Tags")
    customFields: Optional[List[Dict[str, Any]]] = Field(None, description="Custom fields")
    source: Optional[str] = Field(None, description="Source")
    country: Optional[str] = Field(None, description="Country")
    assignedTo: Optional[str] = Field(None, description="Assigned to user ID")

class DeleteContactParams(BaseModel):
    contact_id: str = Field(..., description="Contact ID")

class UpsertContactParams(CreateContactParams):
    pass

# Response schemas - Contact
class ContactResponse(BaseModel):
    contact: Contact

class ContactsResponse(BaseModel):
    contacts: List[Contact]
    count: Optional[int] = None

class CreateContactResponse(BaseModel):
    contact: Contact

class UpdateContactResponse(BaseModel):
    succeded: bool
    contact: Contact

class DeleteContactResponse(BaseModel):
    succeded: bool

class UpsertContactResponse(BaseModel):
    new: bool
    contact: Contact
    traceId: Optional[str] = None

# Task Models
class Task(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    status: str
    dueDate: Optional[str] = None
    completedDate: Optional[str] = None
    contactId: Optional[str] = None
    assignedTo: Optional[str] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None

class TaskList(BaseModel):
    tasks: List[Task]

# Input schemas - Task
class GetTasksParams(BaseModel):
    contact_id: Optional[str] = Field(None, description="Contact ID")
    location_id: Optional[str] = Field(None, description="Location ID")
    limit: Optional[int] = Field(25, description="Limit")
    skip: Optional[int] = Field(0, description="Skip")

class GetTaskParams(BaseModel):
    contact_id: str = Field(..., description="Contact ID")
    task_id: str = Field(..., description="Task ID")

class CreateTaskParams(BaseModel):
    contact_id: str = Field(..., description="Contact ID")
    title: str = Field(..., description="Task title")
    body: Optional[str] = Field(None, description="Task body")
    dueDate: str = Field(..., description="Due date in ISO format")
    completed: bool = Field(..., description="Completion status")
    assignedTo: Optional[str] = Field(None, description="User ID the task is assigned to")

class UpdateTaskParams(BaseModel):
    contact_id: str = Field(..., description="Contact ID")
    task_id: str = Field(..., description="Task ID")
    title: Optional[str] = Field(None, description="Task title")
    body: Optional[str] = Field(None, description="Task body")
    dueDate: Optional[str] = Field(None, description="Due date in ISO format")
    completed: Optional[bool] = Field(None, description="Completion status")
    assignedTo: Optional[str] = Field(None, description="User ID the task is assigned to")

class DeleteTaskParams(BaseModel):
    contact_id: str = Field(..., description="Contact ID")
    task_id: str = Field(..., description="Task ID")

class UpdateTaskCompletedParams(BaseModel):
    contact_id: str = Field(..., description="Contact ID")
    task_id: str = Field(..., description="Task ID")
    completed: bool = Field(..., description="Completion status")

# Response schemas - Task
class TaskResponse(BaseModel):
    task: Task

class TasksResponse(BaseModel):
    tasks: List[Task]

class CreateTaskResponse(BaseModel):
    task: Task

class UpdateTaskResponse(BaseModel):
    task: Task

class DeleteTaskResponse(BaseModel):
    succeded: bool

class UpdateTaskCompletedResponse(BaseModel):
    task: Task

# Appointment Models
class Appointment(BaseModel):
    id: str
    calendarId: str
    status: str
    title: str
    appoinmentStatus: Optional[str] = None
    appointmentStatus: Optional[str] = None
    assignedUserId: Optional[str] = None
    notes: Optional[str] = None
    startTime: str
    endTime: str
    address: Optional[str] = None
    locationId: str
    contactId: str
    groupId: Optional[str] = None
    users: Optional[List[str]] = None
    dateAdded: Optional[str] = None
    dateUpdated: Optional[str] = None
    assignedResources: Optional[List[str]] = None

class AppointmentList(BaseModel):
    events: List[Appointment]

# Input schemas - Appointment
class GetAppointmentsParams(BaseModel):
    contact_id: str = Field(..., description="Contact ID")

# Response schemas - Appointment
class AppointmentsResponse(BaseModel):
    events: List[Appointment]

# Tag Models
class TagsList(BaseModel):
    tags: List[str]

# Input schemas - Tags
class AddTagsParams(BaseModel):
    contact_id: str = Field(..., description="Contact ID")
    tags: List[str] = Field(..., description="Tags to add")

class RemoveTagsParams(BaseModel):
    contact_id: str = Field(..., description="Contact ID")
    tags: List[str] = Field(..., description="Tags to remove")

# Response schemas - Tags
class TagsResponse(BaseModel):
    tags: List[str]

# Note Models
class Note(BaseModel):
    id: str
    body: str
    userId: str
    dateAdded: str
    contactId: str

class NoteList(BaseModel):
    notes: List[Note]

# Input schemas - Note
class GetNotesParams(BaseModel):
    contact_id: str = Field(..., description="Contact ID")

class GetNoteParams(BaseModel):
    contact_id: str = Field(..., description="Contact ID")
    note_id: str = Field(..., description="Note ID")

class CreateNoteParams(BaseModel):
    contact_id: str = Field(..., description="Contact ID")
    body: str = Field(..., description="Note content")
    userId: Optional[str] = Field(None, description="User ID who created the note")

class UpdateNoteParams(BaseModel):
    contact_id: str = Field(..., description="Contact ID")
    note_id: str = Field(..., description="Note ID")
    body: str = Field(..., description="Note content")
    userId: Optional[str] = Field(None, description="User ID who updated the note")

class DeleteNoteParams(BaseModel):
    contact_id: str = Field(..., description="Contact ID")
    note_id: str = Field(..., description="Note ID")

# Response schemas - Note
class NoteResponse(BaseModel):
    note: Note

class NotesResponse(BaseModel):
    notes: List[Note]

class CreateNoteResponse(BaseModel):
    note: Note

class UpdateNoteResponse(BaseModel):
    note: Note

class DeleteNoteResponse(BaseModel):
    succeded: bool

# Campaign Models
class AddContactToCampaignParams(BaseModel):
    contact_id: str = Field(..., description="Contact ID")
    campaign_id: str = Field(..., description="Campaign ID")

class RemoveContactFromCampaignParams(BaseModel):
    contact_id: str = Field(..., description="Contact ID")
    campaign_id: str = Field(..., description="Campaign ID")

class RemoveContactFromAllCampaignsParams(BaseModel):
    contact_id: str = Field(..., description="Contact ID")

class CampaignSuccessResponse(BaseModel):
    succeded: bool

# Workflow Models
class AddContactToWorkflowParams(BaseModel):
    contact_id: str = Field(..., description="Contact ID")
    workflow_id: str = Field(..., description="Workflow ID")
    eventStartTime: Optional[str] = Field(None, description="Event start time")

class RemoveContactFromWorkflowParams(BaseModel):
    contact_id: str = Field(..., description="Contact ID")
    workflow_id: str = Field(..., description="Workflow ID")

class WorkflowSuccessResponse(BaseModel):
    succeded: bool

# Bulk Contact Operations Models
class BulkTagUpdateResponse(BaseModel):
    succeded: bool
    errorCount: int
    responses: List[Dict[str, Any]]

class BulkTagUpdateParams(BaseModel):
    operation_type: Literal["add", "remove"] = Field(..., description="Operation type (add or remove)")
    contacts: List[str] = Field(..., description="List of contact IDs to be processed")
    tags: List[str] = Field(..., description="List of tags to be added or removed")
    location_id: str = Field(..., description="Location ID")
    remove_all_tags: Optional[bool] = Field(False, description="Option to remove all tags (only for remove operation)")

class BulkBusinessUpdateResponse(BaseModel):
    success: bool
    ids: List[str]

class BulkBusinessUpdateParams(BaseModel):
    location_id: str = Field(..., description="Location ID")
    contact_ids: List[str] = Field(..., description="List of contact IDs to be processed")
    business_id: Optional[str] = Field(None, description="Business ID (null to remove contacts from business)")

# Contact Search Models
class ContactSearchResult(BaseModel):
    id: str
    locationId: str
    phone: Optional[str] = None
    email: Optional[str] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    tags: Optional[List[str]] = None
    businessId: Optional[str] = None
    dateAdded: Optional[str] = None
    dateUpdated: Optional[str] = None
    customFields: Optional[List[Dict[str, Any]]] = None
    # Adding additional fields from the response
    phoneLabel: Optional[str] = None
    country: Optional[str] = None
    address: Optional[str] = None
    source: Optional[str] = None
    type: Optional[str] = None
    dnd: Optional[bool] = None
    state: Optional[str] = None
    businessName: Optional[str] = None
    companyName: Optional[str] = None
    city: Optional[str] = None
    postalCode: Optional[str] = None
    assignedTo: Optional[str] = None
    validEmail: Optional[bool] = None
    # Include other fields as needed
    # Using Dict[str, Any] for complex nested structures
    dndSettings: Optional[Dict[str, Any]] = None
    opportunities: Optional[List[Dict[str, Any]]] = None
    additionalEmails: Optional[List[str]] = None
    additionalPhones: Optional[List[str]] = None
    dateOfBirth: Optional[str] = None
    firstNameLowerCase: Optional[str] = None
    lastNameLowerCase: Optional[str] = None
    followers: Optional[List[str]] = None
    searchAfter: Optional[List[Any]] = None

class ContactSearchResponse(BaseModel):
    contacts: List[ContactSearchResult]
    total: int

class ContactSearchParams(BaseModel):
    # Common search parameters
    location_id: str = Field(..., description="Location ID")
    query: Optional[str] = Field(None, description="Free text search")
    assignedTo: Optional[str] = Field(None, description="Filter by assigned user")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    businessId: Optional[str] = Field(None, description="Filter by business ID")
    source: Optional[str] = Field(None, description="Filter by source")
    type: Optional[str] = Field(None, description="Filter by contact type")
    dnd: Optional[bool] = Field(None, description="Filter by do not disturb status")
    limit: Optional[int] = Field(None, description="Number of results to return")
    skip: Optional[int] = Field(None, description="Number of results to skip")
    page: Optional[int] = Field(None, description="Page number")
    page_size: Optional[int] = Field(None, description="Results per page")
    sort_by: Optional[str] = Field(None, description="Field to sort by")
    sort_dir: Optional[str] = Field(None, description="Sort direction (asc or desc)")
    # Allow for any additional parameters
    search_params: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional search parameters")

class GetDuplicateContactParams(BaseModel):
    location_id: str = Field(..., description="Location ID")
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")

# Followers Models
class AddFollowersParams(BaseModel):
    contact_id: str = Field(..., description="Contact ID")
    followers: List[str] = Field(..., description="List of follower IDs to add")

class RemoveFollowersParams(BaseModel):
    contact_id: str = Field(..., description="Contact ID")
    followers: List[str] = Field(..., description="List of follower IDs to remove")

class FollowersResponse(BaseModel):
    followers: List[str]
    followersAdded: Optional[List[str]] = None
    followersRemoved: Optional[List[str]] = None

# Conversation Models
class Conversation(BaseModel):
    id: str
    contactId: str
    locationId: str
    deleted: bool = False
    inbox: Optional[bool] = None
    type: Optional[int] = None
    unreadCount: Optional[int] = None
    assignedTo: Optional[str] = None
    starred: Optional[bool] = None
    lastMessageBody: Optional[str] = None
    lastMessageDate: Optional[str] = None
    lastMessageType: Optional[str] = None
    userId: Optional[str] = None
    dateAdded: Optional[str] = None
    dateUpdated: Optional[str] = None

class ConversationSuccess(BaseModel):
    success: bool
    conversation: Optional[Conversation] = None

# Input schemas - Conversation
class GetConversationParams(BaseModel):
    conversation_id: str = Field(..., description="Conversation ID")

class UpdateConversationParams(BaseModel):
    conversation_id: str = Field(..., description="Conversation ID")
    location_id: str = Field(..., description="Location ID")
    unread_count: Optional[int] = Field(None, description="Count of unread messages")
    starred: Optional[bool] = Field(None, description="Whether the conversation is starred")
    feedback: Optional[Dict[str, Any]] = Field(None, description="Feedback data")

class DeleteConversationParams(BaseModel):
    conversation_id: str = Field(..., description="Conversation ID")

class CreateConversationParams(BaseModel):
    location_id: str = Field(..., description="Location ID")
    contact_id: str = Field(..., description="Contact ID")

# Conversation Search Models
class ConversationSearchResult(BaseModel):
    id: str
    contactId: str
    locationId: str
    lastMessageBody: Optional[str] = None
    lastMessageType: Optional[str] = None
    type: Optional[str] = None
    unreadCount: Optional[int] = None
    fullName: Optional[str] = None
    contactName: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

class ConversationsSearchResponse(BaseModel):
    conversations: List[ConversationSearchResult]
    total: int

class SearchConversationsParams(BaseModel):
    location_id: str = Field(..., description="Location ID")
    assigned_to: Optional[str] = Field(None, description="Comma-separated user IDs")
    contact_id: Optional[str] = Field(None, description="Contact ID")
    followers: Optional[str] = Field(None, description="Comma-separated follower IDs")
    conversation_id: Optional[str] = Field(None, description="Conversation ID")
    last_message_action: Optional[str] = Field(None, description="Last message action")
    last_message_direction: Optional[str] = Field(None, description="Last message direction")
    last_message_type: Optional[str] = Field(None, description="Last message type")
    limit: Optional[int] = Field(None, description="Limit of conversations")
    mentions: Optional[str] = Field(None, description="Comma-separated user IDs")
    query: Optional[str] = Field(None, description="Search query")
    score_profile: Optional[str] = Field(None, description="Score profile ID")
    score_profile_min: Optional[int] = Field(None, description="Minimum score")
    score_profile_max: Optional[int] = Field(None, description="Maximum score")
    sort: Optional[str] = Field(None, description="Sort direction")
    sort_by: Optional[str] = Field(None, description="Sort field")
    sort_score_profile: Optional[str] = Field(None, description="Score profile to sort by")
    start_after_date: Optional[str] = Field(None, description="Start after date")
    status: Optional[str] = Field(None, description="Conversation status")
    page: Optional[int] = Field(None, description="Page number")
    page_size: Optional[int] = Field(None, description="Results per page")

# Conversation Message Models
class MessageMeta(BaseModel):
    callDuration: Optional[str] = None
    callStatus: Optional[str] = None
    email: Optional[Dict[str, Any]] = None

class ConversationMessage(BaseModel):
    id: str
    type: Optional[int] = None
    messageType: Optional[str] = None
    locationId: str
    contactId: str
    conversationId: str
    dateAdded: str
    body: Optional[str] = None
    direction: Optional[str] = None
    status: Optional[str] = None
    contentType: Optional[str] = None
    attachments: Optional[List[str]] = None
    meta: Optional[MessageMeta] = None
    source: Optional[str] = None
    userId: Optional[str] = None
    conversationProviderId: Optional[str] = None

class EmailMessage(BaseModel):
    id: str
    altId: Optional[str] = None
    threadId: str
    locationId: str
    contactId: str
    conversationId: str
    dateAdded: str
    subject: Optional[str] = None
    body: str
    direction: str
    status: Optional[str] = None
    contentType: str
    attachments: Optional[List[str]] = None
    provider: Optional[str] = None
    from_field: Optional[str] = Field(None, alias="from")
    to: Optional[List[str]] = None
    cc: Optional[List[str]] = None
    bcc: Optional[List[str]] = None
    replyToMessageId: Optional[str] = None
    source: Optional[str] = None
    conversationProviderId: Optional[str] = None

class CancelEmailResult(BaseModel):
    status: int
    message: str

# Input schemas - Conversation Messages
class GetMessageByIdParams(BaseModel):
    message_id: str = Field(..., description="Message ID")

class GetEmailByIdParams(BaseModel):
    email_id: str = Field(..., description="Email ID")

class CancelScheduledEmailParams(BaseModel):
    email_message_id: str = Field(..., description="Email message ID")

# Conversation Messages List Models
class ConversationMessagesList(BaseModel):
    lastMessageId: str
    nextPage: bool
    messages: List[ConversationMessage]

# Updated Input schemas - Conversation Messages
class GetMessagesByConversationParams(BaseModel):
    conversation_id: str = Field(..., description="Conversation ID")
    last_message_id: Optional[str] = Field(None, description="Last message ID for pagination")
    limit: Optional[int] = Field(None, description="Limit of messages to retrieve")
    message_types: Optional[str] = Field(None, description="Types of messages to retrieve (comma-separated)")
    direction: Optional[str] = Field(None, description="Filter by message direction")
    status: Optional[str] = Field(None, description="Filter by message status")
    from_date: Optional[str] = Field(None, description="Filter by date from")
    to_date: Optional[str] = Field(None, description="Filter by date to")
    sort_by: Optional[str] = Field(None, description="Field to sort by")
    sort_dir: Optional[str] = Field(None, description="Sort direction (asc or desc)")

# Send Message Models
class SendMessageResponse(BaseModel):
    conversationId: str
    messageId: str
    emailMessageId: Optional[str] = None
    messageIds: Optional[List[str]] = None
    msg: Optional[str] = None

class SendMessageParams(BaseModel):
    message_type: str = Field(..., description="Type of message")
    contact_id: str = Field(..., description="Contact ID")
    message: Optional[str] = Field(None, description="Message content")
    html: Optional[str] = Field(None, description="HTML content")
    subject: Optional[str] = Field(None, description="Subject line")
    appointment_id: Optional[str] = Field(None, description="Appointment ID")
    attachments: Optional[List[str]] = Field(None, description="List of attachment URLs")
    email_from: Optional[str] = Field(None, description="Email sender address")
    email_to: Optional[str] = Field(None, description="Email recipient address")
    email_cc: Optional[List[str]] = Field(None, description="CC email addresses")
    email_bcc: Optional[List[str]] = Field(None, description="BCC email addresses")
    email_reply_mode: Optional[str] = Field(None, description="Email reply mode")
    reply_message_id: Optional[str] = Field(None, description="Message ID being replied to")
    template_id: Optional[str] = Field(None, description="Template ID")
    thread_id: Optional[str] = Field(None, description="Thread ID")
    scheduled_timestamp: Optional[int] = Field(None, description="Scheduled timestamp")
    conversation_provider_id: Optional[str] = Field(None, description="Conversation provider ID")
    from_number: Optional[str] = Field(None, description="Sender phone number")
    to_number: Optional[str] = Field(None, description="Recipient phone number")

# API Response
class ApiResponse(BaseModel):
    data: Union[
        # Business responses
        Business, 
        BusinessList, 
        SuccessResponse, 
        CreateBusinessResponse, 
        UpdateBusinessResponse, 
        DeleteBusinessResponse,
        
        # Calendar responses
        Calendar,
        CalendarList,
        CalendarResponse,
        CalendarsResponse,
        CreateCalendarResponse,
        UpdateCalendarResponse,
        FreeSlotsResponse,
        BlockSlotResponse,
        
        # Contact responses
        Contact,
        ContactList,
        ContactResponse,
        ContactsResponse,
        CreateContactResponse,
        UpdateContactResponse,
        DeleteContactResponse,
        UpsertContactResponse,
        
        # Task responses
        Task,
        TaskList,
        TaskResponse,
        TasksResponse,
        CreateTaskResponse,
        UpdateTaskResponse,
        DeleteTaskResponse,
        UpdateTaskCompletedResponse,
        
        # Appointment responses
        Appointment,
        AppointmentList,
        AppointmentsResponse,
        
        # Tag responses
        TagsList,
        TagsResponse,
        
        # Note responses
        Note,
        NoteList,
        NoteResponse,
        NotesResponse,
        CreateNoteResponse,
        UpdateNoteResponse,
        DeleteNoteResponse,
        
        # Campaign responses
        CampaignSuccessResponse,
        
        # Workflow responses
        WorkflowSuccessResponse,
        
        # Bulk Contact Operations responses
        BulkTagUpdateResponse,
        BulkBusinessUpdateResponse,
        
        # Contact Search responses
        ContactSearchResponse,
        ContactSearchResult,
        
        # Followers responses
        FollowersResponse,
        
        # Conversation responses
        Conversation,
        ConversationSuccess,
        
        # Conversation Search responses
        ConversationsSearchResponse,
        
        # Conversation Message responses
        ConversationMessage,
        EmailMessage,
        CancelEmailResult,
        ConversationMessagesList,
        GetMessagesByConversationParams,
        SendMessageResponse
    ]
    component: Optional[Dict[str, Any]] = None
