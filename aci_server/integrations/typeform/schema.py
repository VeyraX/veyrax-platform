from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union

# Input schemas
class GetFormsParams(BaseModel):
    page: Optional[int] = Field(None, description="Page number for pagination")
    page_size: Optional[int] = Field(None, description="Number of results per page")
    search: Optional[str] = Field(None, description="Filter forms by name")
    workspace_id: Optional[str] = Field(None, description="Filter forms by workspace")

class GetFormParams(BaseModel):
    form_id: str = Field(..., description="ID of the form to retrieve")

class GetFormResponsesParams(BaseModel):
    form_id: str = Field(..., description="ID of the form")
    page_size: Optional[int] = Field(None, description="Maximum number of responses")
    since: Optional[str] = Field(None, description="Limit to responses after this date/time")
    until: Optional[str] = Field(None, description="Limit to responses before this date/time")
    after: Optional[str] = Field(None, description="Pagination token for responses after this token")
    before: Optional[str] = Field(None, description="Pagination token for responses before this token")
    completed: Optional[bool] = Field(None, description="Filter by completion status")

class CreateWebhookParams(BaseModel):
    form_id: str = Field(..., description="ID of the form")
    tag: str = Field(..., description="Unique tag name for the webhook")
    url: str = Field(..., description="URL to send webhook events to")
    enabled: Optional[bool] = Field(True, description="Whether the webhook is enabled")
    secret: Optional[str] = Field(None, description="Secret used to sign webhook requests")

class GetWorkspacesParams(BaseModel):
    search: Optional[str] = Field(None, description="Filter results by name")
    page: Optional[int] = Field(None, description="Page number for pagination")
    page_size: Optional[int] = Field(None, description="Number of results per page")

class CreateFormParams(BaseModel):
    title: str = Field(..., description="Title of the form")
    workspace: Optional[str] = Field(None, description="ID of the workspace to create the form in")
    settings: Optional[Dict[str, Any]] = Field(None, description="Form settings")
    fields: Optional[List[Dict[str, Any]]] = Field(None, description="Form fields")
    welcome_screens: Optional[List[Dict[str, Any]]] = Field(None, description="Welcome screens")
    thankyou_screens: Optional[List[Dict[str, Any]]] = Field(None, description="Thank you screens")

class UpdateFormParams(BaseModel):
    form_id: str = Field(..., description="ID of the form to update")
    title: Optional[str] = Field(None, description="Updated title of the form")
    settings: Optional[Dict[str, Any]] = Field(None, description="Updated form settings")
    fields: Optional[List[Dict[str, Any]]] = Field(None, description="Updated form fields")
    welcome_screens: Optional[List[Dict[str, Any]]] = Field(None, description="Updated welcome screens")
    thankyou_screens: Optional[List[Dict[str, Any]]] = Field(None, description="Updated thank you screens")

class DeleteFormParams(BaseModel):
    form_id: str = Field(..., description="ID of the form to delete")

class DeleteWebhookParams(BaseModel):
    form_id: str = Field(..., description="ID of the form")
    tag: str = Field(..., description="Tag of the webhook to delete")

class CreateWorkspaceParams(BaseModel):
    name: str = Field(..., description="Name of the workspace")

# Output models
class Form(BaseModel):
    id: str
    title: str
    type: Optional[str] = None
    self: Optional[Dict[str, Any]] = None
    theme: Optional[Dict[str, Any]] = None
    settings: Optional[Dict[str, Any]] = None
    welcome_screens: Optional[List[Dict[str, Any]]] = None
    thankyou_screens: Optional[List[Dict[str, Any]]] = None
    fields: Optional[List[Dict[str, Any]]] = None
    logic: Optional[List[Dict[str, Any]]] = None
    hidden: Optional[List[str]] = None
    variables: Optional[Dict[str, Any]] = None
    workspace: Optional[Dict[str, Any]] = None
    _links: Optional[Dict[str, Any]] = None

class FormList(BaseModel):
    items: List[Form]
    page_count: Optional[int] = None
    page_size: Optional[int] = None
    total_items: Optional[int] = None
    _links: Optional[Dict[str, Any]] = None

class Response(BaseModel):
    response_id: str
    landing_id: Optional[str] = None
    token: Optional[str] = None
    landed_at: Optional[str] = None
    submitted_at: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    answers: Optional[List[Dict[str, Any]]] = None
    hidden: Optional[Dict[str, Any]] = None
    calculated: Optional[Dict[str, Any]] = None

class ResponseList(BaseModel):
    items: List[Response]
    page_count: Optional[int] = None
    total_items: Optional[int] = None
    _links: Optional[Dict[str, Any]] = None

class Webhook(BaseModel):
    id: str
    form_id: str
    tag: str
    url: str
    enabled: bool
    secret: Optional[str] = None
    verify_ssl: Optional[bool] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class WebhookList(BaseModel):
    items: List[Webhook]

class Workspace(BaseModel):
    id: str
    name: str
    default: Optional[bool] = None
    shared: Optional[bool] = None
    members: Optional[List[Dict[str, Any]]] = None
    forms: Optional[List[Dict[str, Any]]] = None
    _links: Optional[Dict[str, Any]] = None

class WorkspaceList(BaseModel):
    items: List[Workspace]
    page_count: Optional[int] = None
    page_size: Optional[int] = None
    total_items: Optional[int] = None
    _links: Optional[Dict[str, Any]] = None

# Response models
class GetFormsResponse(BaseModel):
    data: FormList

class GetFormResponse(BaseModel):
    data: Form

class GetFormResponsesResponse(BaseModel):
    data: ResponseList

class CreateWebhookResponse(BaseModel):
    data: Webhook

class GetWebhooksResponse(BaseModel):
    data: WebhookList

class GetWorkspacesResponse(BaseModel):
    data: WorkspaceList

class CreateFormResponse(BaseModel):
    data: Form

class UpdateFormResponse(BaseModel):
    data: Form

class DeleteFormResponse(BaseModel):
    data: Dict[str, Any]  # Usually an empty dict for successful deletion

class DeleteWebhookResponse(BaseModel):
    data: Dict[str, Any]  # Usually an empty dict for successful deletion

class CreateWorkspaceResponse(BaseModel):
    data: Workspace

# API Response
class ApiResponse(BaseModel):
    data: Union[
        Form, FormList, Response, ResponseList, Webhook, WebhookList, 
        Workspace, WorkspaceList, Dict[str, Any]  # Add Dict[str, Any] for delete operations
    ]
    component: Optional[Dict[str, Any]] = None
