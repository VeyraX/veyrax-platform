from pydantic import BaseModel, Field, AnyUrl
from typing import List, Dict, Optional, Any, Union
from enum import Enum
from datetime import datetime

class TagColor(str, Enum):
    RED = "red"
    ORANGE = "orange"
    YELLOW = "yellow"
    GREEN = "green"
    BLUE = "blue"
    PURPLE = "purple"
    PINK = "pink"
    GRAY = "gray"

class Tag(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    color: Optional[TagColor] = None

class GeoRedirect(BaseModel):
    class Config:
        extra = "allow"

class LinkBase(BaseModel):
    domain: Optional[str] = None
    key: Optional[str] = None
    url: Optional[str] = None
    trackConversion: Optional[bool] = None
    externalId: Optional[str] = None
    tenantId: Optional[str] = None
    programId: Optional[str] = None
    partnerId: Optional[str] = None
    archived: Optional[bool] = None
    expiresAt: Optional[str] = None
    expiredUrl: Optional[str] = None
    password: Optional[str] = None
    proxy: Optional[bool] = None
    title: Optional[str] = None
    description: Optional[str] = None
    image: Optional[str] = None
    video: Optional[str] = None
    rewrite: Optional[bool] = None
    doIndex: Optional[bool] = None
    ios: Optional[str] = None
    android: Optional[str] = None
    geo: Optional[GeoRedirect] = None
    publicStats: Optional[bool] = None
    tagId: Optional[str] = None
    tags: Optional[List[Tag]] = None
    folderId: Optional[str] = None
    webhookIds: Optional[List[str]] = None
    comments: Optional[str] = None
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    utm_term: Optional[str] = None
    utm_content: Optional[str] = None

class CreateLinkParams(LinkBase):
    url: str = Field(..., description="The destination URL")

class UpdateLinkParams(LinkBase):
    link_id: str = Field(..., description="The ID of the link to update")

class UpsertLinkParams(LinkBase):
    url: str = Field(..., description="The destination URL")
    key: Optional[str] = Field(None, description="Custom short link path")
    domain: Optional[str] = Field(None, description="Domain for the short link")

class DeleteLinkParams(BaseModel):
    link_id: str = Field(..., description="The ID of the link to delete")

class GetLinkParams(BaseModel):
    link_id: Optional[str] = Field(None, description="The ID of the link to retrieve")

class GetLinksParams(BaseModel):
    pass

# New schemas
class BulkCreateLinksParams(BaseModel):
    links: List[CreateLinkParams] = Field(..., description="List of links to create in bulk")

class BulkUpdateLinksParams(BaseModel):
    data: Dict[str, Any] = Field(..., description="Data to update all links with")
    linkIds: List[str] = Field(..., description="List of link IDs to update in bulk")

class BulkDeleteLinksParams(BaseModel):
    link_ids: List[str] = Field(..., description="List of link IDs to delete in bulk")

class GetQRCodeParams(BaseModel):
    link_id: Optional[str] = Field(None, description="Link ID to get QR code for. If not provided, returns a generic QR code.")

class GetAnalyticsParams(BaseModel):
    pass

class GetEventsParams(BaseModel):
    pass

class LinkCount(BaseModel):
    count: int

class ClickEvent(BaseModel):
    id: str
    timestamp: str
    url: str
    country: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    continent: Optional[str] = None
    device: Optional[str] = None
    browser: Optional[str] = None
    os: Optional[str] = None
    referer: Optional[str] = None
    refererUrl: Optional[str] = None
    qr: Optional[bool] = None
    ip: Optional[str] = None


class BulkDeleteResponse(BaseModel):
    deletedCount: int

class Analytics(BaseModel):
    clicks: int
    leads: int
    sales: int
    saleAmount: int

class Link(LinkBase):
    id: str
    shortLink: Optional[str] = None
    qrCode: Optional[str] = None
    userId: Optional[str] = None
    workspaceId: Optional[str] = None
    clicks: Optional[int] = None
    lastClicked: Optional[str] = None
    leads: Optional[int] = None
    sales: Optional[int] = None
    saleAmount: Optional[int] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None
    projectId: Optional[str] = None

class Event(BaseModel):
    event: str
    timestamp: str
    click: Optional[ClickEvent] = None
    link: Optional[Link] = None
    click_id: Optional[str] = None
    link_id: Optional[str] = None
    domain: Optional[str] = None
    key: Optional[str] = None
    url: Optional[str] = None
    continent: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    device: Optional[str] = None
    browser: Optional[str] = None
    os: Optional[str] = None
    qr: Optional[int] = None
    ip: Optional[str] = None


class LinkResponse(BaseModel):
    data: Link

class LinksResponse(BaseModel):
    data: List[Link]

# Add these list wrapper classes
class LinkList(BaseModel):
    items: List[Link]

class EventList(BaseModel):
    items: List[Event]

# Update ApiResponse to use the wrapper classes for lists
class ApiResponse(BaseModel):
    data: Union[
        Link, LinkList, str, LinkCount, BulkDeleteResponse, Analytics, 
        EventList
    ]
    component: Optional[Dict[str, Any]] = None

# Customer schema definitions
class CustomerLinkInfo(BaseModel):
    id: Optional[str] = None
    domain: Optional[str] = None
    key: Optional[str] = None
    shortLink: Optional[str] = None
    programId: Optional[str] = None

class PartnerInfo(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    image: Optional[str] = None

class DiscountInfo(BaseModel):
    id: Optional[str] = None
    amount: Optional[int] = None
    type: Optional[str] = None
    maxDuration: Optional[int] = None
    couponId: Optional[str] = None
    couponTestId: Optional[str] = None
    partnersCount: Optional[int] = None

class CustomerBase(BaseModel):
    externalId: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    avatar: Optional[str] = None
    country: Optional[str] = None
    link: Optional[CustomerLinkInfo] = None
    partner: Optional[PartnerInfo] = None
    discount: Optional[DiscountInfo] = None

class Customer(CustomerBase):
    id: str
    createdAt: Optional[str] = None

class CustomerInfo(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    avatar: Optional[str] = None
    externalId: Optional[str] = None

class GetCustomerParams(BaseModel):
    customer_id: str = Field(..., description="ID of the customer to retrieve")

class GetCustomersParams(BaseModel):
    pass

class UpdateCustomerParams(CustomerBase):
    customer_id: str = Field(..., description="ID of the customer to update")

class DeleteCustomerParams(BaseModel):
    customer_id: str = Field(..., description="ID of the customer to delete")

# Lead tracking schemas
class LeadClickInfo(BaseModel):
    id: str = Field(..., description="Click ID to associate with the lead")

class TrackLeadParams(BaseModel):
    click: LeadClickInfo
    customer: CustomerInfo

# Sale tracking schemas
class SaleInfo(BaseModel):
    amount: int
    currency: Optional[str] = None
    paymentProcessor: Optional[str] = None
    invoiceId: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class TrackSaleParams(BaseModel):
    eventName: Optional[str] = None
    customer: CustomerInfo
    sale: SaleInfo

# Tag management schemas
class CreateTagParams(BaseModel):
    name: str
    color: TagColor

class GetTagsParams(BaseModel):
    pass

class UpdateTagParams(BaseModel):
    tag_id: str = Field(..., description="ID of the tag to update")
    name: Optional[str] = None
    color: Optional[TagColor] = None

# Response schemas for lists
class CustomerList(BaseModel):
    items: List[Customer]

class TagList(BaseModel):
    items: List[Tag]

# Update ApiResponse for the new types
class ApiResponse(BaseModel):
    data: Union[
        Link, LinkList, str, LinkCount, BulkDeleteResponse, Analytics, 
        EventList, Customer, CustomerList, Tag, TagList
    ]
    component: Optional[Dict[str, Any]] = None

# Domain schema definitions
class RegisteredDomain(BaseModel):
    id: Optional[str] = None
    createdAt: Optional[str] = None
    expiresAt: Optional[str] = None

class DomainBase(BaseModel):
    slug: Optional[str] = None
    verified: Optional[bool] = None
    primary: Optional[bool] = None
    archived: Optional[bool] = None
    placeholder: Optional[str] = None
    expiredUrl: Optional[str] = None
    notFoundUrl: Optional[str] = None
    logo: Optional[str] = None
    registeredDomain: Optional[RegisteredDomain] = None

class Domain(DomainBase):
    id: Optional[str] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None

class CreateDomainParams(DomainBase):
    slug: str = Field(..., description="Domain slug (e.g., acme.com)")

class UpdateDomainParams(DomainBase):
    domain_slug: str = Field(..., description="Slug of the domain to update")

class DeleteDomainParams(BaseModel):
    domain_slug: str = Field(..., description="Slug of the domain to delete")

class GetDomainsParams(BaseModel):
    pass

# Workspace schema definitions
class WorkspaceUser(BaseModel):
    role: str

class WorkspaceDomain(BaseModel):
    slug: str
    primary: bool
    verified: bool

class WorkspaceBase(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    logo: Optional[str] = None
    inviteCode: Optional[str] = None
    plan: Optional[str] = None
    stripeId: Optional[str] = None
    billingCycleStart: Optional[int] = None
    paymentFailedAt: Optional[str] = None
    stripeConnectId: Optional[str] = None
    conversionEnabled: Optional[bool] = None
    dotLinkClaimed: Optional[bool] = None
    partnersEnabled: Optional[bool] = None
    flags: Optional[Dict[str, Any]] = None
    store: Optional[Dict[str, Any]] = None
    allowedHostnames: Optional[List[str]] = None

class Workspace(WorkspaceBase):
    id: str
    totalLinks: Optional[int] = None
    usage: Optional[int] = None
    usageLimit: Optional[int] = None
    linksUsage: Optional[int] = None
    linksLimit: Optional[int] = None
    salesUsage: Optional[int] = None
    salesLimit: Optional[int] = None
    domainsLimit: Optional[int] = None
    tagsLimit: Optional[int] = None
    foldersUsage: Optional[int] = None
    foldersLimit: Optional[int] = None
    usersLimit: Optional[int] = None
    aiUsage: Optional[int] = None
    aiLimit: Optional[int] = None
    createdAt: Optional[str] = None
    users: Optional[List[WorkspaceUser]] = None
    domains: Optional[List[WorkspaceDomain]] = None

class GetWorkspaceParams(BaseModel):
    id_or_slug: str = Field(..., description="ID or slug of the workspace to retrieve")

class UpdateWorkspaceParams(WorkspaceBase):
    id_or_slug: str = Field(..., description="ID or slug of the workspace to update")

# Response schemas for lists
class DomainList(BaseModel):
    items: List[Domain]

# Update ApiResponse
class ApiResponse(BaseModel):
    data: Union[
        Link, LinkList, str, LinkCount, BulkDeleteResponse, Analytics, 
        EventList, Customer, CustomerList, Tag, TagList,
        Domain, DomainList, Workspace
    ]
    component: Optional[Dict[str, Any]] = None