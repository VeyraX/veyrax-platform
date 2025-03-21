from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union, Literal

# Base params
class BaseAirtableParams(BaseModel):
    base_id: str = Field(..., description="The ID of the Airtable base")
    table_id_or_name: str = Field(..., description="The ID or name of the table")

# List records params
class ListRecordsParams(BaseAirtableParams):
    time_zone: Optional[str] = Field(None, description="The time zone for date formatting when using string cell format")
    user_locale: Optional[str] = Field(None, description="The user locale for date formatting when using string cell format")
    page_size: Optional[int] = Field(None, ge=1, le=100, description="Number of records per page (max 100)")
    max_records: Optional[int] = Field(None, description="Maximum total number of records to return")
    offset: Optional[str] = Field(None, description="Pagination offset from a previous request")
    view: Optional[str] = Field(None, description="Name or ID of a view to use")
    sort: Optional[List[Dict[str, Any]]] = Field(None, description="List of sort objects")
    filter_by_formula: Optional[str] = Field(None, description="Formula to filter records")
    cell_format: Optional[Literal["json", "string"]] = Field("json", description="Format for cell values")
    fields: Optional[List[str]] = Field(None, description="List of field names or IDs to include")
    return_fields_by_field_id: Optional[bool] = Field(False, description="Return field objects keyed by field ID")
    record_metadata: Optional[List[str]] = Field(None, description="Metadata to include with records")

# Get record params
class GetRecordParams(BaseAirtableParams):
    record_id: str = Field(..., description="The ID of the record to retrieve")
    cell_format: Optional[Literal["json", "string"]] = Field("json", description="Format for cell values")
    return_fields_by_field_id: Optional[bool] = Field(False, description="Return field objects keyed by field ID")

# Create/update record field
class RecordFields(BaseModel):
    fields: Dict[str, Any] = Field(..., description="Field values for the record")

# Create single record params
class CreateRecordParams(BaseAirtableParams):
    fields: Dict[str, Any] = Field(..., description="Field values for the record")
    typecast: Optional[bool] = Field(False, description="Enable automatic data conversion")
    return_fields_by_field_id: Optional[bool] = Field(False, description="Return field objects keyed by field ID")

# Create multiple records params
class CreateRecordsParams(BaseAirtableParams):
    records: List[RecordFields] = Field(..., description="List of records to create")
    typecast: Optional[bool] = Field(False, description="Enable automatic data conversion")
    return_fields_by_field_id: Optional[bool] = Field(False, description="Return field objects keyed by field ID")

# Update single record params
class UpdateRecordParams(BaseAirtableParams):
    record_id: str = Field(..., description="The ID of the record to update")
    fields: Dict[str, Any] = Field(..., description="Field values to update")
    typecast: Optional[bool] = Field(False, description="Enable automatic data conversion")
    return_fields_by_field_id: Optional[bool] = Field(False, description="Return field objects keyed by field ID")
    is_patch: Optional[bool] = Field(True, description="Use PATCH (partial update) instead of PUT (destructive update)")

# Update record with ID for batch update
class UpdateRecordWithId(RecordFields):
    id: str = Field(..., description="Record ID to update")

# Update multiple records params
class UpdateRecordsParams(BaseAirtableParams):
    records: List[UpdateRecordWithId] = Field(..., description="List of records to update")
    typecast: Optional[bool] = Field(False, description="Enable automatic data conversion")
    return_fields_by_field_id: Optional[bool] = Field(False, description="Return field objects keyed by field ID")
    is_patch: Optional[bool] = Field(True, description="Use PATCH (partial update) instead of PUT (destructive update)")
    perform_upsert: Optional[Dict[str, List[str]]] = Field(None, description="Enable upsert with fields to merge on")

# Delete record params
class DeleteRecordParams(BaseAirtableParams):
    record_id: str = Field(..., description="The ID of the record to delete")

# Delete multiple records params
class DeleteRecordsParams(BaseAirtableParams):
    record_ids: List[str] = Field(..., description="List of record IDs to delete")

# Upload attachment params
class UploadAttachmentParams(BaseModel):
    base_id: str = Field(..., description="The ID of the Airtable base")
    record_id: str = Field(..., description="The ID of the record")
    attachment_field: str = Field(..., description="The ID or name of the attachment field")
    content_type: str = Field(..., description="Content type of the file")
    file: str = Field(..., description="Base64 encoded file content")
    filename: str = Field(..., description="Filename")

# Sync CSV params
class SyncCSVParams(BaseModel):
    base_id: str = Field(..., description="The ID of the Airtable base")
    table_id_or_name: str = Field(..., description="The ID or name of the table")
    api_endpoint_sync_id: str = Field(..., description="The API endpoint sync ID")
    csv_data: str = Field(..., description="CSV data to sync")

# Response Models
class RecordAttachment(BaseModel):
    id: str
    url: str
    filename: str
    size: int
    type: str

class Record(BaseModel):
    id: str
    createdTime: str
    fields: Dict[str, Any]
    commentCount: Optional[int] = None

class DeletedRecord(BaseModel):
    id: str
    deleted: bool

class RecordsList(BaseModel):
    records: List[Record]
    offset: Optional[str] = None

class DeletedRecordsList(BaseModel):
    records: List[DeletedRecord]

class UpsertResponse(BaseModel):
    records: List[Record]
    createdRecords: List[str]
    updatedRecords: List[str]

class SyncCSVResponse(BaseModel):
    success: bool


# Field Models
class FieldModel(BaseModel):
    id: str
    name: str
    type: str
    description: Optional[str] = None
    options: Optional[Dict[str, Any]] = None

# Create Field params
class CreateFieldParams(BaseModel):
    base_id: str = Field(..., description="The ID of the Airtable base")
    table_id: str = Field(..., description="The ID of the table")
    name: str = Field(..., description="The name of the field to create")
    type: str = Field(..., description="The type of field to create")
    description: Optional[str] = Field(None, description="Description of the field")
    options: Optional[Dict[str, Any]] = Field(None, description="Field-specific options")

# Update Field params
class UpdateFieldParams(BaseModel):
    base_id: str = Field(..., description="The ID of the Airtable base")
    table_id: str = Field(..., description="The ID of the table")
    column_id: str = Field(..., description="The ID of the field/column to update")
    name: Optional[str] = Field(None, description="The new name for the field")
    description: Optional[str] = Field(None, description="The new description for the field")

# Table Models
class TableView(BaseModel):
    id: str
    name: str
    type: str
    visibleFieldIds: Optional[List[str]] = None

class TableField(BaseModel):
    id: str
    name: str
    type: Optional[str] = None
    description: Optional[str] = None
    options: Optional[Dict[str, Any]] = None

class TableModel(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    primaryFieldId: str
    fields: List[TableField]
    views: List[TableView]

# Table Params
class CreateTableParams(BaseModel):
    base_id: str = Field(..., description="The ID of the Airtable base")
    name: str = Field(..., description="The name for the table")
    description: Optional[str] = Field(None, description="The description for the table")
    fields: List[Dict[str, Any]] = Field(..., description="A list of fields to create in the table")

class UpdateTableParams(BaseModel):
    base_id: str = Field(..., description="The ID of the Airtable base")
    table_id_or_name: str = Field(..., description="The ID or name of the table to update")
    name: Optional[str] = Field(None, description="The new name for the table")
    description: Optional[str] = Field(None, description="The new description for the table")

# Response Models for specific endpoints
class ListRecordsResponse(BaseModel):
    data: RecordsList
    component: Optional[Dict[str, Any]] = None

class GetRecordResponse(BaseModel):
    data: Record
    component: Optional[Dict[str, Any]] = None

class CreateRecordResponse(BaseModel):
    data: Record
    component: Optional[Dict[str, Any]] = None

class CreateRecordsResponse(BaseModel):
    data: RecordsList
    component: Optional[Dict[str, Any]] = None

class UpdateRecordResponse(BaseModel):
    data: Record
    component: Optional[Dict[str, Any]] = None

class UpdateRecordsResponse(BaseModel):
    data: Union[RecordsList, UpsertResponse]
    component: Optional[Dict[str, Any]] = None

class DeleteRecordResponse(BaseModel):
    data: DeletedRecord
    component: Optional[Dict[str, Any]] = None

class DeleteRecordsResponse(BaseModel):
    data: DeletedRecordsList
    component: Optional[Dict[str, Any]] = None

class UploadAttachmentResponse(BaseModel):
    data: Record
    component: Optional[Dict[str, Any]] = None

class SyncCSVResponse(BaseModel):
    data: SyncCSVResponse
    component: Optional[Dict[str, Any]] = None

class CreateFieldResponse(BaseModel):
    data: FieldModel
    component: Optional[Dict[str, Any]] = None

class UpdateFieldResponse(BaseModel):
    data: FieldModel
    component: Optional[Dict[str, Any]] = None

class CreateTableResponse(BaseModel):
    data: TableModel
    component: Optional[Dict[str, Any]] = None

class UpdateTableResponse(BaseModel):
    data: TableModel
    component: Optional[Dict[str, Any]] = None

# Base Models
class BaseInfo(BaseModel):
    id: str
    name: str
    permissionLevel: str

class BasesList(BaseModel):
    bases: List[BaseInfo]
    offset: Optional[str] = None

class BaseSchema(BaseModel):
    tables: List[TableModel]

class BaseCreated(BaseModel):
    id: str
    tables: List[TableModel]

# Base Params
class ListBasesParams(BaseModel):
    offset: Optional[str] = Field(None, description="Pagination offset from a previous request")

class GetBaseSchemaParams(BaseModel):
    base_id: str = Field(..., description="The ID of the Airtable base")
    include: Optional[List[str]] = Field(None, description="Additional fields to include in the response")

class CreateBaseParams(BaseModel):
    name: str = Field(..., description="The name for the new base")
    workspace_id: str = Field(..., description="The workspace where the base will be created")
    tables: List[Dict[str, Any]] = Field(..., description="A list of tables to create in the base")

# Response Models
class ListBasesResponse(BaseModel):
    data: BasesList
    component: Optional[Dict[str, Any]] = None

class GetBaseSchemaResponse(BaseModel):
    data: BaseSchema
    component: Optional[Dict[str, Any]] = None

class CreateBaseResponse(BaseModel):
    data: BaseCreated
    component: Optional[Dict[str, Any]] = None

# Webhook Models
class WebhookNotificationResult(BaseModel):
    completionTimestamp: Optional[str] = None
    durationMs: Optional[float] = None
    retryNumber: Optional[int] = None
    success: bool
    willBeRetried: Optional[bool] = None
    error: Optional[Dict[str, Any]] = None

class WebhookSpecification(BaseModel):
    options: Dict[str, Any]

class Webhook(BaseModel):
    id: str
    areNotificationsEnabled: bool
    cursorForNextPayload: int
    isHookEnabled: bool
    lastSuccessfulNotificationTime: Optional[str] = None
    notificationUrl: Optional[str] = None
    expirationTime: Optional[str] = None
    lastNotificationResult: Optional[WebhookNotificationResult] = None
    specification: WebhookSpecification

class WebhooksList(BaseModel):
    webhooks: List[Webhook]

class WebhookPayload(BaseModel):
    actionMetadata: Dict[str, Any]
    baseTransactionNumber: int
    payloadFormat: str
    timestamp: str
    # Other fields will be included based on the specific payload type

class WebhookPayloadsList(BaseModel):
    cursor: int
    mightHaveMore: bool
    payloads: List[WebhookPayload]

class WebhookCreated(BaseModel):
    id: str
    macSecretBase64: str
    expirationTime: Optional[str] = None

# Webhook Params
class ListWebhooksParams(BaseModel):
    base_id: str = Field(..., description="The ID of the Airtable base")

class CreateWebhookParams(BaseModel):
    base_id: str = Field(..., description="The ID of the Airtable base")
    notificationUrl: Optional[str] = Field(None, description="URL to receive webhook notifications")
    specification: Dict[str, Any] = Field(..., description="Webhook specification with filters")

class DeleteWebhookParams(BaseModel):
    base_id: str = Field(..., description="The ID of the Airtable base")
    webhook_id: str = Field(..., description="The ID of the webhook to delete")

class ListWebhookPayloadsParams(BaseModel):
    base_id: str = Field(..., description="The ID of the Airtable base")
    webhook_id: str = Field(..., description="The ID of the webhook")
    cursor: Optional[int] = Field(None, description="The cursor to start listing payloads from")
    limit: Optional[int] = Field(None, ge=1, le=50, description="Maximum number of payloads to return (1-50)")

# Response Models
class ListWebhooksResponse(BaseModel):
    data: WebhooksList
    component: Optional[Dict[str, Any]] = None

class CreateWebhookResponse(BaseModel):
    data: WebhookCreated
    component: Optional[Dict[str, Any]] = None

class DeleteWebhookResponse(BaseModel):
    data: Dict[str, Any]
    component: Optional[Dict[str, Any]] = None

class ListWebhookPayloadsResponse(BaseModel):
    data: WebhookPayloadsList
    component: Optional[Dict[str, Any]] = None

# User info models
class UserInfo(BaseModel):
    id: str
    email: Optional[str] = None
    scopes: Optional[List[str]] = None

# Response model for user info
class GetUserInfoResponse(BaseModel):
    data: UserInfo
    component: Optional[Dict[str, Any]] = None

# Update ApiResponse Union type to include user info models
class ApiResponse(BaseModel):
    data: Union[
        Record, RecordsList, DeletedRecord, DeletedRecordsList, 
        UpsertResponse, SyncCSVResponse,
        FieldModel,
        TableModel,
        BasesList, BaseSchema, BaseCreated,
        ListRecordsResponse, GetRecordResponse, CreateRecordResponse, CreateRecordsResponse,
        UpdateRecordResponse, UpdateRecordsResponse, DeleteRecordResponse, DeleteRecordsResponse,
        UploadAttachmentResponse,
        CreateFieldResponse, UpdateFieldResponse,
        CreateTableResponse, UpdateTableResponse,
        ListBasesResponse, GetBaseSchemaResponse, CreateBaseResponse,
        WebhooksList, WebhookCreated, WebhookPayloadsList,
        ListWebhooksResponse, CreateWebhookResponse, DeleteWebhookResponse, ListWebhookPayloadsResponse,
        UserInfo, GetUserInfoResponse,
        Dict[str, Any]
    ]
    component: Optional[Dict[str, Any]] = None
