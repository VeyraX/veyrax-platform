from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from enum import Enum

class SearchPersonParams(BaseModel):
    q_person_name: Optional[str] = Field(
        None,
        description="Person name to search for"
    )
    q_company_name: Optional[str] = Field(
        None,
        description="Search for people matching a company name"
    )
    q_company_website_domains: Optional[list] = Field(
        None,
        description="Search for employees working at a company with these website domains",
    )
    q_keywords: Optional[list] = Field(
        None,
        description="Search for people with these keywords in their profile"
    )
    q_titles: Optional[list] = Field(
        None,
        description="Search for people having these specific titles"
    )
    q_title_keywords: Optional[list] = Field(
        None,
        description="Search for people with these keywords in their titles"
    )
    page: Optional[int] = Field(
        1,
        description="Page number"
    )
    not_organization_ids: Optional[str] = Field(
        None,
        description="Comma-separated IDs of organizations to exclude"
    )
    organization_ids: Optional[str] = Field(
        None, 
        description="Comma-separated IDs of organizations to filter by"
    )
    person_past_organization_ids: Optional[str] = Field(
        None,
        description="Comma-separated IDs of organizations the person used to work at"
    )
    person_titles: Optional[str] = Field(
        None,
        description="Job titles to filter by"
    )
    person_past_titles: Optional[str] = Field(
        None,
        description="Past job titles to filter by"
    )
    person_not_titles: Optional[str] = Field(
        None,
        description="Job titles to exclude"
    )
    person_locations: Optional[str] = Field(
        None,
        description="Locations to filter by (comma-separated)"
    )
    zip_code: Optional[str] = Field(
        None,
        description="ZIP code to filter by"
    )
    person_location_radius: Optional[str] = Field(
        None,
        description="Radius from the location (25, 50, 100, or 300 miles)"
    )
    organization_num_employees_ranges: Optional[str] = Field(
        None,
        description="Organization size ranges to filter by"
    )
    organization_industry_tag_ids: Optional[str] = Field(
        None,
        description="Industry tags to filter by"
    )
    q_organization_keyword_tags: Optional[str] = Field(
        None,
        description="Keywords to match with the current company"
    )
    contact_email_status_v2: Optional[str] = Field(
        None,
        description="Email status to filter by"
    )

class PersonDetailsParams(BaseModel):
    person_id: str = Field(
        ...,
        description="The Apollo person ID to get details for"
    )

class OrganizationDetailsParams(BaseModel):
    organization_id: str = Field(
        ...,
        description="The Apollo organization ID to get details for"
    )

class SearchOrganizationParams(BaseModel):
    q_organization_name: Optional[str] = Field(
        None,
        description="Organization name to search for"
    )
    organization_num_employees_ranges: Optional[str] = Field(
        None,
        description="Number of employees ranges (e.g. 1-10, 11-50, 51-200, etc.)"
    )
    organization_locations: Optional[str] = Field(
        None,
        description="Comma-separated locations to filter by"
    )
    zip_code: Optional[str] = Field(
        None,
        description="ZIP code to filter by"
    )
    organization_location_radius: Optional[str] = Field(
        None,
        description="Radius from location (25, 50, 100, 300 miles)"
    )
    organization_industry_tag_ids: Optional[str] = Field(
        None,
        description="Comma-separated industry tag IDs"
    )
    q_organization_keyword_tags: Optional[str] = Field(
        None,
        description="Comma-separated keywords to match with the company name"
    )
    organization_ids: Optional[str] = Field(
        None,
        description="Comma-separated organization IDs"
    )
    page: Optional[int] = Field(
        1,
        description="Page number for pagination"
    )

class SearchPeopleViaUrlParams(BaseModel):
    apollo_url: str = Field(
        ...,
        description="The Apollo URL to search with"
    )
    page: Optional[int] = Field(
        1,
        description="Page number for results pagination"
    )

class SearchOrganizationsViaUrlParams(BaseModel):
    apollo_url: str = Field(
        ..., 
        description="The Apollo URL to search organizations with"
    )
    page: Optional[int] = Field(
        1, 
        description="Page number for results pagination"
    )

class Person(BaseModel):
    id: str
    first_name: str
    last_name: str
    name: str
    linkedin_url: Optional[str] = None
    title: Optional[str] = None
    email_status: Optional[str] = None
    photo_url: Optional[str] = None
    twitter_url: Optional[str] = None
    github_url: Optional[str] = None
    facebook_url: Optional[str] = None
    headline: Optional[str] = None
    email: Optional[str] = None
    organization_id: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    is_likely_to_engage: Optional[bool] = None
    departments: Optional[List[str]] = None
    subdepartments: Optional[List[str]] = None
    seniority: Optional[str] = None
    functions: Optional[List[str]] = None
    revealed_for_current_team: Optional[bool] = None

class Organization(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    website_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    twitter_url: Optional[str] = None
    facebook_url: Optional[str] = None
    blog_url: Optional[str] = None
    angellist_url: Optional[str] = None
    phone: Optional[str] = None
    primary_domain: Optional[str] = None
    logo_url: Optional[str] = None
    founded_year: Optional[int] = None
    primary_phone: Optional[Dict[str, Any]] = None
    alexa_ranking: Optional[int] = None
    linkedin_uid: Optional[str] = None
    publicly_traded_symbol: Optional[str] = None
    publicly_traded_exchange: Optional[str] = None
    sanitized_phone: Optional[str] = None
    market_cap: Optional[str] = None
    owned_by_organization_id: Optional[str] = None
    owned_by_organization: Optional[Dict[str, Any]] = None
    organization_revenue_printed: Optional[str] = None
    organization_revenue: Optional[int] = None
    intent_strength: Optional[Any] = None
    show_intent: Optional[bool] = None
    has_intent_signal_account: Optional[bool] = None
    intent_signal_account: Optional[Any] = None
    estimated_num_employees: Optional[int] = None
    industry: Optional[str] = None
    keywords: Optional[List[str]] = None
    industries: Optional[List[str]] = None
    secondary_industries: Optional[List[str]] = None
    current_technologies: Optional[List[Dict[str, Any]]] = None
    technology_names: Optional[List[str]] = None
    street_address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None

class Employment(BaseModel):
    id: str
    title: Optional[str] = None
    current: Optional[bool] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    organization_id: Optional[str] = None
    organization_name: Optional[str] = None

class PhoneNumber(BaseModel):
    raw_number: Optional[str] = None
    sanitized_number: Optional[str] = None
    type: Optional[str] = None

class Pagination(BaseModel):
    page: int
    per_page: int
    total_entries: int
    total_pages: int

class PersonWithDetails(Person):
    employment_history: Optional[List[Employment]] = None
    organization: Optional[Organization] = None
    phone_numbers: Optional[List[PhoneNumber]] = None

class OrganizationWithDetails(Organization):
    suborganizations: Optional[List[Dict[str, Any]]] = None
    num_suborganizations: Optional[int] = None
    employee_metrics: Optional[List[Dict[str, Any]]] = None
    annual_revenue: Optional[int] = None
    annual_revenue_printed: Optional[str] = None
    raw_address: Optional[str] = None
    detail_view_loaded: Optional[bool] = None

class PeopleList(BaseModel):
    people: List[PersonWithDetails]
    pagination: Pagination

class PersonData(BaseModel):
    data: PeopleList

class PersonDetailData(BaseModel):
    data: PersonWithDetails

class OrganizationDetailData(BaseModel):
    data: OrganizationWithDetails

class SearchPersonResponse(BaseModel):
    data: PersonData

class OrganizationList(BaseModel):
    organizations: List[Organization]
    pagination: Pagination

class OrganizationData(BaseModel):
    data: OrganizationList

class SearchOrganizationResponse(BaseModel):
    data: OrganizationData

class PersonDetailResponse(BaseModel):
    data: PersonDetailData

class OrganizationDetailResponse(BaseModel):
    data: OrganizationDetailData

# API Response
class ApiResponse(BaseModel):
    data: Union[PersonData, OrganizationData, PersonDetailData, OrganizationDetailData]
    component: Optional[Dict[str, Any]] = None
