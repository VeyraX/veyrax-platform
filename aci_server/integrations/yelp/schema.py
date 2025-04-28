from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union

# Search Businesses Parameters
class SearchBusinessesParams(BaseModel):
    location: str = Field(
        ...,
        description="Location (e.g., 'New York, NY')"
    )
    search_term: Optional[str] = Field(
        None,
        description="Search term (e.g., 'Pizza', 'Salon')"
    )
    limit: Optional[int] = Field(
        10,
        ge=1,
        le=50,
        description="Number of results to return (1-50)"
    )
    offset: Optional[int] = Field(
        0,
        ge=0,
        description="Offset for pagination"
    )
    business_details_type: Optional[str] = Field(
        "basic",
        description="Level of detail to return ('basic' or 'detailed')"
    )

# Business Details Parameters
class GetBusinessDetailsParams(BaseModel):
    business_url: Optional[str] = Field(
        None,
        description="Yelp business URL"
    )
    business_ids: Optional[str] = Field(
        None,
        description="Comma-separated list of business IDs"
    )

    class Config:
        extra = "forbid"

# Business Reviews Parameters
class GetBusinessReviewsParams(BaseModel):
    business_url: Optional[str] = Field(
        None,
        description="Yelp business URL"
    )
    business_id: Optional[str] = Field(
        None,
        description="Business ID"
    )
    reviews_per_page: Optional[int] = Field(
        20,
        ge=1,
        le=100,
        description="Number of reviews per page (1-100)"
    )

# Business Menus Parameters
class GetBusinessMenusParams(BaseModel):
    business_id: str = Field(
        ...,
        description="Business ID"
    )

# Business Models
class BusinessLocation(BaseModel):
    address1: Optional[str] = None
    address2: Optional[str] = None
    address3: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = None
    display_address: Optional[List[str]] = None

class BusinessHours(BaseModel):
    hours_type: Optional[str] = None
    is_open_now: Optional[bool] = None
    open: Optional[List[Dict[str, Any]]] = None

class BusinessCategory(BaseModel):
    alias: Optional[str] = None
    title: Optional[str] = None

class BusinessCoordinates(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class Business(BaseModel):
    id: Optional[str] = None
    alias: Optional[str] = None
    name: Optional[str] = None
    image_url: Optional[str] = None
    is_closed: Optional[bool] = None
    url: Optional[str] = None
    review_count: Optional[int] = None
    categories: Optional[List[BusinessCategory]] = None
    rating: Optional[float] = None
    coordinates: Optional[BusinessCoordinates] = None
    transactions: Optional[List[str]] = None
    price: Optional[str] = None
    location: Optional[BusinessLocation] = None
    phone: Optional[str] = None
    display_phone: Optional[str] = None
    distance: Optional[float] = None
    hours: Optional[List[BusinessHours]] = None
    photos: Optional[List[str]] = None

class BusinessSearchResults(BaseModel):
    total: int
    businesses: List[Business]
    region: Optional[Dict[str, Any]] = None

# New model for multiple business details
class BusinessDetailsList(BaseModel):
    businesses: List[Business]

# Review Models
class ReviewUser(BaseModel):
    id: Optional[str] = None
    profile_url: Optional[str] = None
    image_url: Optional[str] = None
    name: Optional[str] = None

class Review(BaseModel):
    id: Optional[str] = None
    url: Optional[str] = None
    text: Optional[str] = None
    rating: Optional[int] = None
    time_created: Optional[str] = None
    user: Optional[ReviewUser] = None

class BusinessReviewResults(BaseModel):
    total: int
    reviews: List[Review]
    possible_languages: Optional[List[str]] = None

# Menu Models
class MenuItem(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[str] = None

class MenuSection(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    items: Optional[List[MenuItem]] = None

class Menu(BaseModel):
    name: Optional[str] = None
    sections: Optional[List[MenuSection]] = None

class BusinessMenus(BaseModel):
    menus: List[Menu]

# API Response Models
class BusinessSearchResponse(BaseModel):
    data: BusinessSearchResults
    component: Optional[Dict[str, Any]] = None

class BusinessDetailsResponse(BaseModel):
    data: Business
    component: Optional[Dict[str, Any]] = None

class BusinessDetailsListResponse(BaseModel):
    data: BusinessDetailsList
    component: Optional[Dict[str, Any]] = None

class BusinessReviewsResponse(BaseModel):
    data: BusinessReviewResults
    component: Optional[Dict[str, Any]] = None

class BusinessMenusResponse(BaseModel):
    data: BusinessMenus
    component: Optional[Dict[str, Any]] = None

class ApiResponse(BaseModel):
    data: Union[
        BusinessSearchResults,
        Business,
        BusinessReviewResults,
        BusinessMenus,
        BusinessDetailsList
    ]
    component: Optional[Dict[str, Any]] = None 