from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union

# Domain Search Models
class DomainSearchParams(BaseModel):
    domain: Optional[str] = Field(None, description="Domain name to search for email addresses")
    company: Optional[str] = Field(None, description="Company name to search for email addresses")
    limit: Optional[int] = Field(10, description="Maximum number of email addresses to return", ge=1, le=100)
    offset: Optional[int] = Field(0, description="Number of email addresses to skip")
    type: Optional[str] = Field(None, description="Filter by email type: 'personal' or 'generic'")
    seniority: Optional[str] = Field(None, description="Filter by seniority level: 'junior', 'senior', or 'executive'")
    department: Optional[str] = Field(None, description="Filter by department: 'executive', 'it', 'finance', etc.")
    required_field: Optional[str] = Field(None, description="Only return email addresses with these fields: 'full_name', 'position', 'phone_number'")

class EmailSource(BaseModel):
    domain: str
    uri: str
    extracted_on: str
    last_seen_on: str
    still_on_page: bool

class EmailVerification(BaseModel):
    date: Optional[str] = None
    status: Optional[str] = None

class Email(BaseModel):
    value: str
    type: str
    confidence: int
    sources: List[EmailSource]
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    position: Optional[str] = None
    position_raw: Optional[str] = None
    seniority: Optional[str] = None
    department: Optional[str] = None
    linkedin: Optional[str] = None
    twitter: Optional[str] = None
    phone_number: Optional[str] = None
    verification: Optional[EmailVerification] = None

class DomainSearchResult(BaseModel):
    domain: str
    disposable: bool
    webmail: bool
    accept_all: bool
    pattern: Optional[str] = None
    organization: Optional[str] = None
    description: Optional[str] = None
    industry: Optional[str] = None
    twitter: Optional[str] = None
    facebook: Optional[str] = None
    linkedin: Optional[str] = None
    instagram: Optional[str] = None
    youtube: Optional[str] = None
    technologies: Optional[List[str]] = None
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    street: Optional[str] = None
    headcount: Optional[str] = None
    company_type: Optional[str] = None
    emails: List[Email]
    linked_domains: List[str]

class DomainSearchMeta(BaseModel):
    results: int
    limit: int
    offset: int
    params: Dict[str, Any]

class DomainSearchResponse(BaseModel):
    data: DomainSearchResult
    meta: DomainSearchMeta

# Email Finder Models
class EmailFinderParams(BaseModel):
    domain: Optional[str] = Field(None, description="Domain name to find email address")
    company: Optional[str] = Field(None, description="Company name to find email address")
    first_name: Optional[str] = Field(None, description="First name of the person")
    last_name: Optional[str] = Field(None, description="Last name of the person")
    full_name: Optional[str] = Field(None, description="Full name of the person")
    max_duration: Optional[int] = Field(None, description="Maximum duration of the request in seconds", ge=3, le=20)

class EmailFinderResult(BaseModel):
    first_name: str
    last_name: str
    email: str
    score: int
    domain: str
    accept_all: bool
    position: Optional[str] = None
    twitter: Optional[str] = None
    linkedin_url: Optional[str] = None
    phone_number: Optional[str] = None
    company: Optional[str] = None
    sources: Optional[List[EmailSource]] = None
    verification: Optional[EmailVerification] = None

class EmailFinderMeta(BaseModel):
    params: Dict[str, Any]

class EmailFinderResponse(BaseModel):
    data: EmailFinderResult
    meta: EmailFinderMeta

# Email Verifier Models
class EmailVerifierParams(BaseModel):
    email: str = Field(..., description="Email address to verify")

class EmailVerifierResult(BaseModel):
    status: str
    result: Optional[str] = None
    score: int
    email: str
    regexp: bool
    gibberish: bool
    disposable: bool
    webmail: bool
    mx_records: bool
    smtp_server: bool
    smtp_check: bool
    accept_all: bool
    block: bool
    sources: Optional[List[EmailSource]] = None

class EmailVerifierMeta(BaseModel):
    params: Dict[str, Any]

class EmailVerifierResponse(BaseModel):
    data: EmailVerifierResult
    meta: EmailVerifierMeta

# Email Count Models
class EmailCountParams(BaseModel):
    domain: Optional[str] = Field(None, description="Domain name to count email addresses")
    company: Optional[str] = Field(None, description="Company name to count email addresses")
    type: Optional[str] = Field(None, description="Count only 'personal' or 'generic' email addresses")

class DepartmentCount(BaseModel):
    executive: int
    it: int
    finance: int
    management: int
    sales: int
    legal: int
    support: int
    hr: int
    marketing: int
    communication: int
    education: int
    design: int
    health: int
    operations: int

class SeniorityCount(BaseModel):
    junior: int
    senior: int
    executive: int

class EmailCountResult(BaseModel):
    total: int
    personal_emails: int
    generic_emails: int
    department: DepartmentCount
    seniority: SeniorityCount

class EmailCountMeta(BaseModel):
    params: Dict[str, Any]

class EmailCountResponse(BaseModel):
    data: EmailCountResult
    meta: EmailCountMeta

# Email Enrichment Models
class EmailEnrichmentParams(BaseModel):
    email: str = Field(..., description="Email address to enrich")
    clearbit_format: Optional[bool] = Field(False, description="Format response according to Clearbit's schema")

class NameInfo(BaseModel):
    fullName: Optional[str] = None
    givenName: Optional[str] = None
    familyName: Optional[str] = None

class GeoInfo(BaseModel):
    city: Optional[str] = None
    state: Optional[str] = None
    stateCode: Optional[str] = None
    country: Optional[str] = None
    countryCode: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None

class EmploymentInfo(BaseModel):
    domain: Optional[str] = None
    name: Optional[str] = None
    title: Optional[str] = None
    role: Optional[str] = None
    subRole: Optional[str] = None
    seniority: Optional[str] = None

class SocialInfo(BaseModel):
    handle: Optional[str] = None

class EmailEnrichmentResult(BaseModel):
    id: Optional[str] = None
    name: NameInfo
    email: str
    location: Optional[str] = None
    timeZone: Optional[str] = None
    utcOffset: Optional[int] = None
    geo: Optional[GeoInfo] = None
    bio: Optional[str] = None
    site: Optional[str] = None
    avatar: Optional[str] = None
    employment: Optional[EmploymentInfo] = None
    facebook: Optional[SocialInfo] = None
    twitter: Optional[SocialInfo] = None
    linkedin: Optional[SocialInfo] = None
    emailProvider: Optional[str] = None
    indexedAt: Optional[str] = None
    phone: Optional[str] = None

class EmailEnrichmentMeta(BaseModel):
    email: str

class EmailEnrichmentResponse(BaseModel):
    data: EmailEnrichmentResult
    meta: EmailEnrichmentMeta

# Company Enrichment Models
class CompanyEnrichmentParams(BaseModel):
    domain: str = Field(..., description="Domain name to enrich")
    clearbit_format: Optional[bool] = Field(False, description="Format response according to Clearbit's schema")

class SiteInfo(BaseModel):
    phoneNumbers: Optional[List[str]] = None
    emailAddresses: Optional[List[str]] = None

class CategoryInfo(BaseModel):
    sector: Optional[str] = None
    industryGroup: Optional[str] = None
    industry: Optional[str] = None
    subIndustry: Optional[str] = None

class MetricsInfo(BaseModel):
    alexaUsRank: Optional[int] = None
    alexaGlobalRank: Optional[int] = None
    trafficRank: Optional[str] = None
    employees: Optional[str] = None
    marketCap: Optional[str] = None
    raised: Optional[str] = None
    annualRevenue: Optional[str] = None

class ParentInfo(BaseModel):
    domain: Optional[str] = None

class CompanyEnrichmentResult(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    legalName: Optional[str] = None
    domain: str
    domainAliases: Optional[List[str]] = None
    site: Optional[SiteInfo] = None
    category: Optional[CategoryInfo] = None
    tags: Optional[List[str]] = None
    description: Optional[str] = None
    foundedYear: Optional[int] = None
    location: Optional[str] = None
    timeZone: Optional[str] = None
    utcOffset: Optional[int] = None
    geo: Optional[GeoInfo] = None
    logo: Optional[str] = None
    facebook: Optional[SocialInfo] = None
    linkedin: Optional[SocialInfo] = None
    twitter: Optional[SocialInfo] = None
    type: Optional[str] = None
    phone: Optional[str] = None
    metrics: Optional[MetricsInfo] = None
    tech: Optional[List[str]] = None
    techCategories: Optional[List[str]] = None
    parent: Optional[ParentInfo] = None
    ultimateParent: Optional[ParentInfo] = None

class CompanyEnrichmentMeta(BaseModel):
    domain: str

class CompanyEnrichmentResponse(BaseModel):
    data: CompanyEnrichmentResult
    meta: CompanyEnrichmentMeta

# Combined Enrichment Models
class CombinedEnrichmentParams(BaseModel):
    email: str = Field(..., description="Email address to enrich")
    clearbit_format: Optional[bool] = Field(False, description="Format response according to Clearbit's schema")

class CombinedEnrichmentResult(BaseModel):
    person: EmailEnrichmentResult
    company: CompanyEnrichmentResult

class CombinedEnrichmentMeta(BaseModel):
    email: str

class CombinedEnrichmentResponse(BaseModel):
    data: CombinedEnrichmentResult
    meta: CombinedEnrichmentMeta

# Account Information Models
class AccountRequestsInfo(BaseModel):
    used: int
    available: int

class AccountRequests(BaseModel):
    searches: AccountRequestsInfo
    verifications: AccountRequestsInfo

class AccountCalls(BaseModel):
    _deprecation_notice: Optional[str] = None
    used: int
    available: int

class AccountInformationResult(BaseModel):
    first_name: str
    last_name: str
    email: str
    plan_name: str
    plan_level: int
    reset_date: str
    team_id: Optional[int] = None
    calls: Optional[AccountCalls] = None
    requests: Optional[AccountRequests] = None

class AccountInformationResponse(BaseModel):
    data: AccountInformationResult

# Common API Response
class ApiResponse(BaseModel):
    data: Union[
        DomainSearchResult,
        EmailFinderResult,
        EmailVerifierResult,
        EmailCountResult,
        EmailEnrichmentResult,
        CompanyEnrichmentResult,
        CombinedEnrichmentResult,
        AccountInformationResult
    ]
    component: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None

# Response Schema Classes
class DomainSearchResponseSchema(BaseModel):
    data: DomainSearchResult
    message: Optional[str] = None

class EmailFinderResponseSchema(BaseModel):
    data: EmailFinderResult
    message: Optional[str] = None

class EmailVerifierResponseSchema(BaseModel):
    data: EmailVerifierResult
    message: Optional[str] = None

class EmailCountResponseSchema(BaseModel):
    data: EmailCountResult
    message: Optional[str] = None

class EmailEnrichmentResponseSchema(BaseModel):
    data: EmailEnrichmentResult
    message: Optional[str] = None

class CompanyEnrichmentResponseSchema(BaseModel):
    data: CompanyEnrichmentResult
    message: Optional[str] = None

class CombinedEnrichmentResponseSchema(BaseModel):
    data: CombinedEnrichmentResult
    message: Optional[str] = None

class AccountInformationResponseSchema(BaseModel):
    data: AccountInformationResult
    message: Optional[str] = None 