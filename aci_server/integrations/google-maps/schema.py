from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union, Literal


# Input schema models
class GeocodeParams(BaseModel):
    address: str = Field(..., description="The address to geocode")


class ReverseGeocodeParams(BaseModel):
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")


class LocationCoordinates(BaseModel):
    latitude: float
    longitude: float


class SearchPlacesParams(BaseModel):
    query: str = Field(..., description="Search query")
    location: Optional[LocationCoordinates] = Field(
        None, description="Optional center point for the search"
    )
    radius: Optional[int] = Field(
        None, description="Search radius in meters (max 50000)"
    )


class PlaceDetailsParams(BaseModel):
    place_id: str = Field(..., description="The place ID to get details for")


class DistanceMatrixParams(BaseModel):
    origins: List[str] = Field(..., description="Array of origin addresses or coordinates")
    destinations: List[str] = Field(
        ..., description="Array of destination addresses or coordinates"
    )
    mode: Optional[Literal["driving", "walking", "bicycling", "transit"]] = Field(
        "driving", description="Travel mode (driving, walking, bicycling, transit)"
    )


class ElevationParams(BaseModel):
    locations: List[LocationCoordinates] = Field(
        ..., description="Array of locations to get elevation for"
    )


class DirectionsParams(BaseModel):
    origin: str = Field(..., description="Starting point address or coordinates")
    destination: str = Field(..., description="Ending point address or coordinates")
    mode: Optional[Literal["driving", "walking", "bicycling", "transit"]] = Field(
        "driving", description="Travel mode (driving, walking, bicycling, transit)"
    )


# Output models
class Location(BaseModel):
    lat: float
    lng: float


class GeocodeResult(BaseModel):
    location: Location
    formatted_address: str
    place_id: str


class AddressComponent(BaseModel):
    long_name: str
    short_name: str
    types: List[str]


class ReverseGeocodeResult(BaseModel):
    formatted_address: str
    place_id: str
    address_components: List[AddressComponent]


class Place(BaseModel):
    name: str
    formatted_address: str
    location: Location
    place_id: str
    rating: Optional[float] = None
    types: Optional[List[str]] = None


class PlaceList(BaseModel):
    places: List[Place]


class PlaceReview(BaseModel):
    author_name: str
    rating: float
    text: str
    time: int


class OpeningHours(BaseModel):
    weekday_text: Optional[List[str]] = None
    open_now: Optional[bool] = None


class PlaceDetail(BaseModel):
    name: str
    formatted_address: str
    location: Location
    formatted_phone_number: Optional[str] = None
    website: Optional[str] = None
    rating: Optional[float] = None
    reviews: Optional[List[PlaceReview]] = None
    opening_hours: Optional[OpeningHours] = None


class DistanceInfo(BaseModel):
    text: str
    value: int


class DurationInfo(BaseModel):
    text: str
    value: int


class DistanceMatrixElement(BaseModel):
    status: str
    distance: Optional[DistanceInfo] = None
    duration: Optional[DurationInfo] = None


class DistanceMatrixResultRow(BaseModel):
    elements: List[DistanceMatrixElement]


class DistanceMatrixResult(BaseModel):
    origin_addresses: List[str]
    destination_addresses: List[str]
    results: List[DistanceMatrixResultRow]


class ElevationPoint(BaseModel):
    elevation: float
    location: Location
    resolution: float


class ElevationList(BaseModel):
    results: List[ElevationPoint]


class DirectionStep(BaseModel):
    instructions: str
    distance: DistanceInfo
    duration: DurationInfo
    travel_mode: str


class DirectionRoute(BaseModel):
    summary: str
    distance: DistanceInfo
    duration: DurationInfo
    steps: List[DirectionStep]


class DirectionsList(BaseModel):
    routes: List[DirectionRoute]


# Response models
class GeocodeResponse(BaseModel):
    data: GeocodeResult


class ReverseGeocodeResponse(BaseModel):
    data: ReverseGeocodeResult


class SearchPlacesResponse(BaseModel):
    data: PlaceList


class PlaceDetailsResponse(BaseModel):
    data: PlaceDetail


class DistanceMatrixResponse(BaseModel):
    data: DistanceMatrixResult


class ElevationResponse(BaseModel):
    data: ElevationList


class DirectionsResponse(BaseModel):
    data: DirectionsList


# API Response
class ApiResponse(BaseModel):
    data: Union[
        GeocodeResult,
        ReverseGeocodeResult,
        PlaceList,
        PlaceDetail,
        DistanceMatrixResult,
        ElevationList,
        DirectionsList,
    ]
    component: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None
