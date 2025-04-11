from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any, Union

class SearchPeopleParams(BaseModel):
    q_person_name: Optional[str] = Field(
        None,
        description="Name of the person to search for"
    )
    page: int = Field(
        1,
        description="Page number to fetch"
    )
    organization_ids: Optional[str] = Field(
        None,
        description="Comma-separated list of organization IDs to filter results"
    )
    not_organization_ids: Optional[str] = Field(
        None,
        description="Comma-separated list of organization IDs to exclude from results"
    )
    person_titles: Optional[str] = Field(
        None,
        description="Job titles to filter results by"
    )
    person_locations: Optional[str] = Field(
        None,
        description="Locations to filter results by (comma-separated)"
    )
    person_location_radius: Optional[str] = Field(
        None,
        description="Radius to search within (can be 25, 50, 100, 300 miles)"
    )

class GetPersonDetailsParams(BaseModel):
    person_id: str = Field(
        ...,
        description="Apollo ID of the person to fetch details for"
    )

class SearchPeopleByUrlParams(BaseModel):
    url: str = Field(
        ...,
        description="Apollo.io search URL to use for fetching people"
    )
    page: int = Field(
        1,
        description="Page number to fetch"
    )

class SearchOrganizationsParams(BaseModel):
    q_organization_name: Optional[str] = Field(
        None,
        description="Name of the organization to search for"
    )
    page: int = Field(
        1,
        description="Page number to fetch"
    )
    organization_num_employees_ranges: Optional[str] = Field(
        None,
        description="Comma-separated ranges for number of employees (e.g., '1-10,11-50,51-200')"
    )
    organization_locations: Optional[str] = Field(
        None,
        description="Locations to filter organizations by (comma-separated)"
    )
    zip_code: Optional[str] = Field(
        None,
        description="ZIP code to filter organizations by location"
    )
    organization_location_radius: Optional[str] = Field(
        None,
        description="Radius to search within (can be 25, 50, 100, 300 miles)"
    )
    organization_industry_tag_ids: Optional[str] = Field(
        None,
        description="Comma-separated list of industry tag IDs to filter by"
    )
    q_organization_keyword_tags: Optional[str] = Field(
        None,
        description="Keywords to match with company names (comma-separated)"
    )
    organization_ids: Optional[str] = Field(
        None,
        description="Comma-separated list of Apollo organization IDs to search for"
    )

class SearchOrganizationsByUrlParams(BaseModel):
    url: str = Field(
        ...,
        description="Apollo.io search URL to use for fetching organizations"
    )
    page: int = Field(
        1,
        description="Page number to fetch"
    )

class EmploymentHistory(BaseModel):
    id: str
    title: str
    organization_name: str
    organization_id: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    current: Optional[bool] = None

class GetOrganizationDetailsParams(BaseModel):
    organization_id: str = Field(
        ...,
        description="Apollo ID of the organization to fetch details for"
    )

class EmployeeMetric(BaseModel):
    start_date: Optional[str] = None
    departments: Optional[List[Dict[str, Any]]] = None
    functions: Optional[Any] = None
    new: Optional[int] = None
    retained: Optional[int] = None
    churned: Optional[int] = None

class Organization(BaseModel):
    id: str
    name: str
    website_url: Optional[str] = None
    blog_url: Optional[str] = None
    angellist_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    twitter_url: Optional[str] = None
    facebook_url: Optional[str] = None
    primary_phone: Optional[Dict[str, Any]] = None
    languages: Optional[List[str]] = None
    alexa_ranking: Optional[int] = None
    phone: Optional[str] = None
    linkedin_uid: Optional[str] = None
    founded_year: Optional[int] = None
    publicly_traded_symbol: Optional[str] = None
    publicly_traded_exchange: Optional[str] = None
    logo_url: Optional[str] = None
    crunchbase_url: Optional[str] = None
    primary_domain: Optional[str] = None
    sanitized_phone: Optional[str] = None
    owned_by_organization_id: Optional[str] = None
    owned_by_organization: Optional[Dict[str, Any]] = None
    intent_strength: Optional[Any] = None
    show_intent: Optional[bool] = None
    has_intent_signal_account: Optional[bool] = None
    intent_signal_account: Optional[Dict[str, Any]] = None
    market_cap: Optional[str] = None
    organization_revenue_printed: Optional[str] = None
    organization_revenue: Optional[int] = None
    industry: Optional[str] = None
    keywords: Optional[List[str]] = None
    estimated_num_employees: Optional[int] = None
    industries: Optional[List[str]] = None
    secondary_industries: Optional[List[str]] = None
    snippets_loaded: Optional[bool] = None
    industry_tag_id: Optional[str] = None
    industry_tag_hash: Optional[Dict[str, Any]] = None
    retail_location_count: Optional[int] = None
    raw_address: Optional[str] = None
    street_address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    seo_description: Optional[str] = None
    short_description: Optional[str] = None
    suborganizations: Optional[List[Dict[str, Any]]] = None
    num_suborganizations: Optional[int] = None
    annual_revenue_printed: Optional[str] = None
    annual_revenue: Optional[int] = None
    technology_names: Optional[List[str]] = None
    current_technologies: Optional[List[Dict[str, Any]]] = None
    org_chart_root_people_ids: Optional[List[str]] = None
    org_chart_sector: Optional[str] = None
    org_chart_removed: Optional[bool] = None
    org_chart_show_department_filter: Optional[bool] = None
    employee_metrics: Optional[List[EmployeeMetric]] = None
    detail_view_loaded: Optional[bool] = None
    
    @field_validator('intent_strength', mode='before')
    @classmethod
    def validate_optional_fields(cls, v):
        if v is not None and not isinstance(v, (str, dict)):
            if isinstance(v, list):
                return {} 
            return {'value': str(v)}
        return v
        
    @field_validator('employee_metrics', mode='before')
    @classmethod
    def validate_employee_metrics(cls, v):
        if v is None:
            return None
            
        if isinstance(v, list):
            return [item if isinstance(item, dict) else {'value': str(item)} for item in v]
        
        if isinstance(v, dict):
            return [v]
            
        return [{'value': str(v)}]

class PhoneNumber(BaseModel):
    raw_number: Optional[str] = None
    sanitized_number: Optional[str] = None
    type: Optional[str] = None

class Person(BaseModel):
    id: str
    first_name: str
    last_name: str
    name: str
    linkedin_url: Optional[str] = None
    title: Optional[str] = None
    email_status: Optional[str] = None
    photo_url: Optional[str] = None
    headline: Optional[str] = None
    email: Optional[str] = None
    organization_id: Optional[str] = None
    employment_history: Optional[List[EmploymentHistory]] = None
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    organization: Optional[Organization] = None
    departments: Optional[List[str]] = None
    seniority: Optional[str] = None
    phone_numbers: Optional[List[PhoneNumber]] = None
    twitter_url: Optional[str] = None
    github_url: Optional[str] = None
    facebook_url: Optional[str] = None
    extrapolated_email_confidence: Optional[Any] = None
    restricted: Optional[bool] = None
    is_likely_to_engage: Optional[bool] = None
    position: Optional[int] = None
    status: Optional[str] = None
    dnc_status: Optional[Any] = None
    dnc_other_info: Optional[Any] = None
    dialer_flags: Optional[Any] = None
    intent_strength: Optional[Any] = None
    show_intent: Optional[bool] = None
    
    @field_validator('extrapolated_email_confidence', 'dnc_status', 'dnc_other_info', 'dialer_flags', 'intent_strength', mode='before')
    @classmethod
    def validate_optional_fields(cls, v):
        if v is not None and not isinstance(v, str):
            return str(v)
        return v

class PeopleList(BaseModel):
    people: List[Person]
    pagination: Dict[str, Any]

class OrganizationsList(BaseModel):
    organizations: List[Organization]
    pagination: Dict[str, Any]

class PersonDetails(BaseModel):
    person: Person

class SearchPeopleResponse(BaseModel):
    data: PeopleList

class SearchOrganizationsResponse(BaseModel):
    data: OrganizationsList

class OrganizationDetails(BaseModel):
    organization: Organization

class OrganizationDetailsResponse(BaseModel):
    data: OrganizationDetails

class PersonDetailsResponse(BaseModel):
    data: PersonDetails

class ApiResponse(BaseModel):
    data: Union[PeopleList, OrganizationsList, PersonDetails, OrganizationDetails]
    component: Optional[Dict[str, Any]] = Field(
        None,
        description="UI components configuration for rendering results"
    )
