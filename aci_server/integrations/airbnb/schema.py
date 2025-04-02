from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union


# Request models
class AirbnbSearchParams(BaseModel):
    location: str = Field(..., description="Location to search for (city, state, etc.)")
    place_id: Optional[str] = Field(None, description="Google Maps Place ID (overrides the location parameter)")
    checkin: Optional[str] = Field(None, description="Check-in date (YYYY-MM-DD)")
    checkout: Optional[str] = Field(None, description="Check-out date (YYYY-MM-DD)")
    adults: Optional[int] = Field(1, description="Number of adults")
    children: Optional[int] = Field(0, description="Number of children")
    infants: Optional[int] = Field(0, description="Number of infants")
    pets: Optional[int] = Field(0, description="Number of pets")
    min_price: Optional[int] = Field(None, description="Minimum price for the stay")
    max_price: Optional[int] = Field(None, description="Maximum price for the stay")
    cursor: Optional[str] = Field(None, description="Base64-encoded string used for Pagination")


class AirbnbListingDetailsParams(BaseModel):
    id: str = Field(..., description="The Airbnb listing ID")
    checkin: Optional[str] = Field(None, description="Check-in date (YYYY-MM-DD)")
    checkout: Optional[str] = Field(None, description="Check-out date (YYYY-MM-DD)")
    adults: Optional[int] = Field(1, description="Number of adults")
    children: Optional[int] = Field(0, description="Number of children")
    infants: Optional[int] = Field(0, description="Number of infants")
    pets: Optional[int] = Field(0, description="Number of pets")


# Data models
class AirbnbListing(BaseModel):
    id: str
    name: Optional[str] = None
    title: Optional[str] = None
    url: str
    coordinate: Optional[Dict[str, Any]] = None
    structured_content: Optional[Dict[str, Any]] = None
    avg_rating: Optional[str] = None
    price_info: Optional[Dict[str, Any]] = None


class AirbnbSearchData(BaseModel):
    search_url: str = Field(..., description="The URL used for the search")
    listings: List[AirbnbListing] = Field([], description="List of Airbnb listings")
    pagination_info: Optional[Dict[str, Any]] = Field(None, description="Pagination information")


class AirbnbListingDetail(BaseModel):
    id: str
    type: str
    content: Dict[str, Any]


class AirbnbListingDetailsData(BaseModel):
    listing_url: str = Field(..., description="The URL of the listing")
    details: List[AirbnbListingDetail] = Field(..., description="Details of the listing")


# Response models
class ApiResponse(BaseModel):
    data: Union[AirbnbSearchData, AirbnbListingDetailsData]
    component: Optional[Dict[str, Any]] = Field(None, description="UI components for rendering results")


class SearchResponse(BaseModel):
    data: AirbnbSearchData


class ListingDetailsResponse(BaseModel):
    data: AirbnbListingDetailsData
