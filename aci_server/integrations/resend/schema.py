from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any, Union

class EmailAddress(BaseModel):
    email: str
    name: Optional[str] = None

class EmailTag(BaseModel):
    name: str
    value: str

class EmailAttachment(BaseModel):
    content: str 
    filename: str
    content_type: Optional[str] = None
    path: Optional[str] = None

# Input schemas
class SendEmailParams(BaseModel):
    from_email: str = Field(..., alias="from")
    to: Union[str, List[str]]
    subject: str
    html: Optional[str] = None
    text: Optional[str] = None
    cc: Optional[Union[str, List[str]]] = None
    bcc: Optional[Union[str, List[str]]] = None
    reply_to: Optional[Union[str, List[str]]] = None
    headers: Optional[Dict[str, str]] = None
    attachments: Optional[List[EmailAttachment]] = None
    tags: Optional[List[EmailTag]] = None
    scheduled_at: Optional[str] = Field(None, description="Up to 72 hours in advance, ISO 8601 formatted date and time, i.e. 2024-08-05T11:52:01.858Z)")

class SendBatchEmailsParams(BaseModel):
    emails: List[SendEmailParams]

class GetEmailParams(BaseModel):
    email_id: str

class UpdateEmailParams(BaseModel):
    email_id: str
    scheduled_at: str

class CancelEmailParams(BaseModel):
    email_id: str

# Output schemas
class EmailResponse(BaseModel):
    id: str
    object: Optional[str] = None
    to: Optional[List[str]] = None
    from_email: Optional[str] = Field(None, alias="from")
    subject: Optional[str] = None
    html: Optional[str] = None
    text: Optional[str] = None
    created_at: Optional[str] = None
    bcc: Optional[List[Optional[str]]] = None
    cc: Optional[List[Optional[str]]] = None
    reply_to: Optional[List[Optional[str]]] = None
    last_event: Optional[str] = None

class BatchEmailResponse(BaseModel):
    data: List[Dict[str, str]]

# API Response models
class SendEmailResponse(BaseModel):
    data: EmailResponse
    message: Optional[str] = None

class SendBatchEmailsResponse(BaseModel):
    data: BatchEmailResponse
    message: Optional[str] = None

class GetEmailResponse(BaseModel):
    data: EmailResponse
    message: Optional[str] = None

class UpdateEmailResponse(BaseModel):
    data: EmailResponse
    message: Optional[str] = None

class CancelEmailResponse(BaseModel):
    data: EmailResponse
    message: Optional[str] = None

# Domain schemas
class DomainRecord(BaseModel):
    record: str
    name: str
    type: str
    ttl: Optional[str] = None
    status: Optional[str] = None
    value: str
    priority: Optional[int] = None

class Domain(BaseModel):
    id: str
    name: str
    status: str
    created_at: str
    region: str
    records: Optional[List[DomainRecord]] = None
    object: Optional[str] = None

class DomainList(BaseModel):
    data: List[Domain]

class CreateDomainParams(BaseModel):
    name: str
    region: Optional[str] = "us-east-1"

class GetDomainParams(BaseModel):
    domain_id: str

class VerifyDomainParams(BaseModel):
    domain_id: str

class UpdateDomainParams(BaseModel):
    domain_id: str
    click_tracking: Optional[bool] = None
    open_tracking: Optional[bool] = None
    tls: Optional[str] = None

class DeleteDomainParams(BaseModel):
    domain_id: str

# Domain response schemas
class CreateDomainResponse(BaseModel):
    data: Domain
    message: Optional[str] = None

class GetDomainResponse(BaseModel):
    data: Domain
    message: Optional[str] = None

class VerifyDomainResponse(BaseModel):
    data: Dict[str, Any]
    message: Optional[str] = None

class UpdateDomainResponse(BaseModel):
    data: Dict[str, Any]
    message: Optional[str] = None

class ListDomainsResponse(BaseModel):
    data: DomainList
    message: Optional[str] = None

class DeleteDomainResponse(BaseModel):
    data: Dict[str, Any]
    message: Optional[str] = None

# API Key schemas
class ApiKey(BaseModel):
    id: str
    name: str
    created_at: Optional[str] = None

class ApiKeyList(BaseModel):
    data: List[ApiKey]

class ApiKeyToken(BaseModel):
    id: str
    token: str

class CreateApiKeyParams(BaseModel):
    name: str
    permission: Optional[str] = "full_access"
    domain_id: Optional[str] = None

class DeleteApiKeyParams(BaseModel):
    api_key_id: str

# API Key response schemas
class CreateApiKeyResponse(BaseModel):
    data: ApiKeyToken
    message: Optional[str] = None

class ListApiKeysResponse(BaseModel):
    data: ApiKeyList
    message: Optional[str] = None

class DeleteApiKeyResponse(BaseModel):
    data: Dict[str, Any]
    message: Optional[str] = None

# Broadcast schemas
class Broadcast(BaseModel):
    id: str
    audience_id: str
    audience_name: Optional[str] = None
    status: str
    created_at: Optional[str] = None
    scheduled_at: Optional[str] = None
    sent_at: Optional[str] = None
    name: Optional[str] = None
    from_email: Optional[str] = Field(None, alias="from")
    subject: Optional[str] = None
    reply_to: Optional[Union[str, List[str]]] = None
    preview_text: Optional[str] = None
    object: Optional[str] = None

class BroadcastList(BaseModel):
    object: Optional[str] = None
    data: List[Broadcast]

class CreateBroadcastParams(BaseModel):
    audience_id: str
    from_email: str = Field(..., alias="from")
    subject: str
    html: Optional[str] = None
    text: Optional[str] = None
    reply_to: Optional[Union[str, List[str]]] = None
    name: Optional[str] = None

class GetBroadcastParams(BaseModel):
    broadcast_id: str

class SendBroadcastParams(BaseModel):
    broadcast_id: str
    scheduled_at: Optional[str] = None

class DeleteBroadcastParams(BaseModel):
    broadcast_id: str

# Broadcast response schemas
class CreateBroadcastResponse(BaseModel):
    data: Dict[str, str]
    message: Optional[str] = None

class GetBroadcastResponse(BaseModel):
    data: Broadcast
    message: Optional[str] = None

class SendBroadcastResponse(BaseModel):
    data: Dict[str, str]
    message: Optional[str] = None

class DeleteBroadcastResponse(BaseModel):
    data: Dict[str, Any] 
    message: Optional[str] = None

class ListBroadcastsResponse(BaseModel):
    data: BroadcastList
    message: Optional[str] = None

class Audience(BaseModel):
    id: str
    name: str
    url: Optional[str] = None
    created_at: Optional[str] = None
    object: Optional[str] = None

class AudienceList(BaseModel):
    object: Optional[str] = None
    data: List[Audience]

class CreateAudienceParams(BaseModel):
    name: str

class GetAudienceParams(BaseModel):
    audience_id: str

class DeleteAudienceParams(BaseModel):
    audience_id: str

# Audience response schemas
class CreateAudienceResponse(BaseModel):
    data: Audience
    message: Optional[str] = None

class GetAudienceResponse(BaseModel):
    data: Audience
    message: Optional[str] = None

class DeleteAudienceResponse(BaseModel):
    data: Dict[str, Any] 
    message: Optional[str] = None

class ListAudiencesResponse(BaseModel):
    data: AudienceList
    message: Optional[str] = None

# Contact schemas
class Contact(BaseModel):
    id: str
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    created_at: Optional[str] = None
    unsubscribed: Optional[bool] = None
    object: Optional[str] = None

class ContactList(BaseModel):
    object: Optional[str] = None
    data: List[Contact]

class CreateContactParams(BaseModel):
    audience_id: str = Field(..., alias="audienceId")
    email: str
    first_name: Optional[str] = Field(None, alias="firstName")
    last_name: Optional[str] = Field(None, alias="lastName")
    unsubscribed: Optional[bool] = None

class GetContactParams(BaseModel):
    audience_id: str = Field(..., alias="audienceId")
    contact_id: str = Field(..., alias="id")

class UpdateContactParams(BaseModel):
    audience_id: str = Field(..., alias="audienceId")
    contact_id: Optional[str] = Field(None, alias="id")
    email: Optional[str] = None
    first_name: Optional[str] = Field(None, alias="firstName")
    last_name: Optional[str] = Field(None, alias="lastName")
    unsubscribed: Optional[bool] = None

class DeleteContactParams(BaseModel):
    audience_id: str = Field(..., alias="audienceId")
    contact_id: Optional[str] = Field(None, alias="id")
    email: Optional[str] = None

class ListContactsParams(BaseModel):
    audience_id: str = Field(..., alias="audienceId")

# Contact response schemas
class CreateContactResponse(BaseModel):
    data: Dict[str, Any]  
    message: Optional[str] = None

class GetContactResponse(BaseModel):
    data: Contact
    message: Optional[str] = None

class UpdateContactResponse(BaseModel):
    data: Dict[str, Any] 
    message: Optional[str] = None

class DeleteContactResponse(BaseModel):
    data: Dict[str, Any] 
    message: Optional[str] = None

class ListContactsResponse(BaseModel):
    data: ContactList
    message: Optional[str] = None

# Update ApiResponse to include contact types
class ApiResponse(BaseModel):
    data: Union[EmailResponse, BatchEmailResponse, Domain, DomainList, ApiKeyToken, ApiKeyList, 
                Broadcast, BroadcastList, Audience, AudienceList, Contact, ContactList, Dict[str, Any]]
    component: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None
