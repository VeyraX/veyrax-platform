from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union, Literal

# Input schema for Search One-Way endpoint
class SearchOneWayParams(BaseModel):
    fromEntityId: str = Field(
        ...,
        description="From location ID that can be retrieved from auto-complete or airports endpoints"
    )
    toEntityId: Optional[str] = Field(
        None,
        description="To location ID (if not provided, will search everywhere)"
    )
    departDate: Optional[str] = Field(
        None,
        description="Depart date in YYYY-MM-DD format (if not provided, will search anytime)"
    )
    wholeMonthDepart: Optional[str] = Field(
        None,
        description="Whole month depart in YYYY-MM format"
    )
    market: Optional[str] = Field(
        "US",
        description="Market (country code)"
    )
    locale: Optional[str] = Field(
        "en-US",
        description="Locale for response language"
    )
    currency: Optional[str] = Field(
        "USD",
        description="Currency for prices"
    )
    stops: Optional[str] = Field(
        None,
        description="Comma-separated list of stops (direct, 1stop, 2stops)"
    )
    adults: Optional[int] = Field(
        1,
        description="Number of adults (12+ years)"
    )
    children: Optional[int] = Field(
        0,
        description="Number of children (2-12 years)"
    )
    infants: Optional[int] = Field(
        0,
        description="Number of infants (under 2 years)"
    )
    cabinClass: Optional[Literal["economy", "premium_economy", "business", "first"]] = Field(
        "economy",
        description="Cabin class"
    )
    airlines: Optional[str] = Field(
        None,
        description="Comma-separated list of airline IDs"
    )
    sort: Optional[str] = Field(
        "cheapest_first",
        description="Sort order (e.g., cheapest_first)"
    )
    maxResult: int = Field(
        5,
        description="Maximum number of results (default: 5)"
    )

# Input schema for Search Everywhere endpoint
class SearchEverywhereParams(BaseModel):
    fromEntityId: str = Field(
        ...,
        description="Origin location ID (e.g., 'NYCA' for New York)"
    )
    type: Optional[str] = Field(
        "oneway",
        description="Flight type (oneway or roundtrip)"
    )
    departDate: Optional[str] = Field(
        None,
        description="Departure date in YYYY-MM-DD format (default: anytime)"
    )
    returnDate: Optional[str] = Field(
        None,
        description="Return date for roundtrip in YYYY-MM-DD format"
    )
    cabinClass: Optional[Literal["economy", "premium_economy", "business", "first"]] = Field(
        "economy",
        description="Cabin class"
    )
    adults: Optional[int] = Field(
        1,
        description="Number of adults"
    )
    maxResult: int = Field(
        5,
        description="Maximum number of results (default: 5)"
    )

# Input schema for Search Roundtrip endpoint
class SearchRoundtripParams(BaseModel):
    fromEntityId: str = Field(
        ...,
        description="From location ID that can be retrieved from auto-complete or airports endpoints"
    )
    toEntityId: Optional[str] = Field(
        None,
        description="To location ID (if not provided, will search everywhere)"
    )
    departDate: Optional[str] = Field(
        None,
        description="Depart date in YYYY-MM-DD format (if not provided, will search anytime)"
    )
    returnDate: Optional[str] = Field(
        None,
        description="Return date in YYYY-MM-DD format (if not provided, will search anytime)"
    )
    wholeMonthDepart: Optional[str] = Field(
        None,
        description="Whole month depart in YYYY-MM format"
    )
    wholeMonthReturn: Optional[str] = Field(
        None,
        description="Whole month return in YYYY-MM format"
    )
    market: Optional[str] = Field(
        "US",
        description="Market (country code)"
    )
    locale: Optional[str] = Field(
        "en-US",
        description="Locale for response language"
    )
    currency: Optional[str] = Field(
        "USD",
        description="Currency for prices"
    )
    stops: Optional[str] = Field(
        None,
        description="Comma-separated list of stops (direct, 1stop, 2stops)"
    )
    adults: Optional[int] = Field(
        1,
        description="Number of adults (12+ years)"
    )
    children: Optional[int] = Field(
        0,
        description="Number of children (2-12 years)"
    )
    infants: Optional[int] = Field(
        0,
        description="Number of infants (under 2 years)"
    )
    cabinClass: Optional[Literal["economy", "premium_economy", "business", "first"]] = Field(
        "economy",
        description="Cabin class"
    )
    airlines: Optional[str] = Field(
        None,
        description="Comma-separated list of airline IDs"
    )
    sort: Optional[str] = Field(
        "cheapest_first",
        description="Sort order (e.g., cheapest_first)"
    )
    maxResult: int = Field(
        5,
        description="Maximum number of results (default: 5)"
    )

# Simplified response schema (only important fields)
class FlightQuote(BaseModel):
    price: str
    direct: bool

class FlightQuotes(BaseModel):
    cheapest: FlightQuote
    direct: Optional[FlightQuote] = None

class LocationInfo(BaseModel):
    id: str
    skyCode: str
    name: str
    type: str

class LocationContent(BaseModel):
    location: LocationInfo
    flightQuotes: FlightQuotes
    image: Optional[Dict[str, str]] = None

class LocationResult(BaseModel):
    id: str
    type: str
    content: LocationContent

class ContextInfo(BaseModel):
    status: str
    sessionId: str
    totalResults: int

# Simple response schema with optional fields
class SearchEverywhereData(BaseModel):
    data: Optional[Dict[str, Any]] = None
    status: Optional[bool] = None
    message: Optional[str] = None
    everywhereDestination: Optional[Dict[str, Any]] = None
    context: Optional[Dict[str, Any]] = None

# Roundtrip search response schema
class SearchRoundtripData(BaseModel):
    data: Optional[Dict[str, Any]] = None
    status: Optional[bool] = None
    message: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    itineraries: Optional[List[Dict[str, Any]]] = None
    messages: Optional[List[Dict[str, Any]]] = None
    filterStats: Optional[Dict[str, Any]] = None
    flightsSessionId: Optional[str] = None
    destinationImageUrl: Optional[str] = None
    token: Optional[str] = None

# One-way search response schema
class SearchOneWayData(BaseModel):
    data: Optional[Dict[str, Any]] = None
    status: Optional[bool] = None
    message: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    itineraries: Optional[List[Dict[str, Any]]] = None
    messages: Optional[List[Dict[str, Any]]] = None
    filterStats: Optional[Dict[str, Any]] = None
    flightsSessionId: Optional[str] = None
    destinationImageUrl: Optional[str] = None
    token: Optional[str] = None

# Input schema for Flight Detail endpoint
class FlightDetailParams(BaseModel):
    token: str = Field(
        ...,
        description="Token from search results (data->token)"
    )
    itineraryId: str = Field(
        ...,
        description="Itinerary ID from search results (data->itineraries->id)"
    )
    market: Optional[str] = Field(
        "US",
        description="Market (country code)"
    )
    locale: Optional[str] = Field(
        "en-US",
        description="Locale for response language"
    )
    currency: Optional[str] = Field(
        "USD",
        description="Currency for prices"
    )
    cookie: Optional[str] = Field(
        None,
        description="Use in case of captcha (403) errors or slow latency"
    )

# Flight detail response schema
class FlightDetailData(BaseModel):
    data: Optional[Dict[str, Any]] = None
    status: Optional[bool] = None
    message: Optional[str] = None
    itinerary: Optional[Dict[str, Any]] = None
    pollingCompleted: Optional[bool] = None
    bookingSessionId: Optional[str] = None

# Input schema for Price Calendar endpoint
class PriceCalendarParams(BaseModel):
    fromEntityId: str = Field(
        ...,
        description="From location ID (e.g., 'CDG' for Paris Charles de Gaulle)"
    )
    departDate: str = Field(
        ...,
        description="Departure date in YYYY-MM-DD format"
    )
    toEntityId: Optional[str] = Field(
        None,
        description="To location ID (optional if searching for all destinations)"
    )
    market: Optional[str] = Field(
        "US",
        description="Market (country code)"
    )
    locale: Optional[str] = Field(
        "en-US",
        description="Locale for response language"
    )
    currency: Optional[str] = Field(
        "USD",
        description="Currency for prices"
    )
    cookie: Optional[str] = Field(
        None,
        description="Use in case of captcha (403) errors or slow latency"
    )

# Price calendar response schema
class PriceCalendarData(BaseModel):
    data: Optional[Dict[str, Any]] = None
    status: Optional[bool] = None
    message: Optional[str] = None
    flights: Optional[Dict[str, Any]] = None
    currency: Optional[str] = None
    days: Optional[List[Dict[str, Any]]] = None
    groups: Optional[List[Dict[str, Any]]] = None

# Input schema for Price Calendar Return endpoint
class PriceCalendarReturnParams(BaseModel):
    fromEntityId: str = Field(
        ...,
        description="From location ID (e.g., 'CDG' for Paris Charles de Gaulle)"
    )
    departDate: str = Field(
        ...,
        description="Departure date in YYYY-MM-DD format"
    )
    returnDate: str = Field(
        ...,
        description="Return date in YYYY-MM-DD format"
    )
    toEntityId: Optional[str] = Field(
        None,
        description="To location ID (optional if searching for all destinations)"
    )
    market: Optional[str] = Field(
        "US",
        description="Market (country code)"
    )
    locale: Optional[str] = Field(
        "en-US",
        description="Locale for response language"
    )
    currency: Optional[str] = Field(
        "USD",
        description="Currency for prices"
    )
    cookie: Optional[str] = Field(
        None,
        description="Use in case of captcha (403) errors or slow latency"
    )

# Input schema for Cheapest One-way endpoint
class CheapestOneWayParams(BaseModel):
    fromEntityId: str = Field(
        ...,
        description="From location ID (e.g., 'CDG' for Paris Charles de Gaulle)"
    )
    toEntityId: str = Field(
        ...,
        description="To location ID (e.g., 'JFK' for New York John F. Kennedy)"
    )
    departDate: str = Field(
        ...,
        description="Departure date in YYYY-MM-DD format"
    )
    market: Optional[str] = Field(
        "US",
        description="Market (country code)"
    )
    locale: Optional[str] = Field(
        "en-US",
        description="Locale for response language"
    )
    currency: Optional[str] = Field(
        "USD",
        description="Currency for prices"
    )

# Cheapest One-way response schema
class CheapestOneWayData(BaseModel):
    data: List[Dict[str, Any]]
    status: Optional[bool] = None
    message: Optional[str] = None

# Input schema for Hotel Search endpoint
class HotelSearchParams(BaseModel):
    entityId: str = Field(
        ...,
        description="Location entity ID (e.g., '27537542' for New York)"
    )
    checkin: str = Field(
        ...,
        description="Check-in date in YYYY-MM-DD format"
    )
    checkout: str = Field(
        ...,
        description="Check-out date in YYYY-MM-DD format"
    )
    resultsPerPage: Optional[int] = Field(
        25,
        description="Total number of records per API call"
    )
    page: Optional[int] = Field(
        1,
        description="The page index for pagination"
    )
    rooms: Optional[int] = Field(
        1,
        description="Number of rooms"
    )
    adults: Optional[int] = Field(
        1,
        description="Number of adults"
    )
    childrenAges: Optional[str] = Field(
        None,
        description="Children ages separated by commas (e.g., '0,11,17')"
    )
    market: Optional[str] = Field(
        "US",
        description="Market (country code)"
    )
    locale: Optional[str] = Field(
        "en-US",
        description="Locale for response language"
    )
    currency: Optional[str] = Field(
        "USD",
        description="Currency for prices"
    )
    sorting: Optional[str] = Field(
        "-relevance",
        description="Sorting method (e.g., '-price', 'price', '-rating')"
    )
    priceType: Optional[str] = Field(
        "PRICE_PER_NIGHT",
        description="Price type (PRICE_PER_NIGHT or PRICE_TOTAL)"
    )
    minPrice: Optional[str] = Field(
        None,
        description="Minimum price"
    )
    maxPrice: Optional[str] = Field(
        None,
        description="Maximum price"
    )
    maxResult: int = Field(
        5,
        description="Maximum number of results to return (default: 5)"
    )
    confidentType: Optional[str] = Field(
        None,
        description="Book with peace of mind options (comma-separated)"
    )
    stars: Optional[str] = Field(
        None,
        description="Star rating filter (comma-separated)"
    )
    mealPlan: Optional[str] = Field(
        None,
        description="Meal plan options (comma-separated)"
    )
    rating: Optional[str] = Field(
        None,
        description="Guest rating filter (comma-separated)"
    )
    guestType: Optional[str] = Field(
        None,
        description="Popular with specific guests (comma-separated)"
    )
    chain: Optional[str] = Field(
        None,
        description="Hotel chain filter (comma-separated)"
    )
    cancellation: Optional[str] = Field(
        None,
        description="Cancellation policy filter (comma-separated)"
    )
    amenities: Optional[str] = Field(
        None,
        description="Amenities filter (comma-separated)"
    )
    propertyType: Optional[str] = Field(
        None,
        description="Accommodation type filter (comma-separated)"
    )
    district: Optional[str] = Field(
        None,
        description="Neighborhoods filter (comma-separated)"
    )
    discountTypes: Optional[str] = Field(
        None,
        description="Deals filter (comma-separated)"
    )

# Hotel search response schema
class HotelSearchData(BaseModel):
    data: Optional[Dict[str, Any]] = None
    meta: Optional[Dict[str, Any]] = None
    status: Optional[bool] = None
    message: Optional[str] = None

# Input schema for Hotel Detail endpoint
class HotelDetailParams(BaseModel):
    id: str = Field(
        ...,
        description="Hotel ID from search results (data->results->hotelCards->id)"
    )
    market: Optional[str] = Field(
        "US",
        description="Market (country code)"
    )
    locale: Optional[str] = Field(
        "en-US",
        description="Locale for response language"
    )
    currency: Optional[str] = Field(
        "USD",
        description="Currency for prices"
    )

# Hotel detail response schema
class HotelDetailData(BaseModel):
    data: Optional[Dict[str, Any]] = None
    status: Optional[bool] = None
    message: Optional[str] = None

# Input schema for Hotel Prices endpoint
class HotelPricesParams(BaseModel):
    hotelId: str = Field(
        ...,
        description="Hotel ID from search results (data->results->hotelCards->hotelId)"
    )
    checkin: str = Field(
        ...,
        description="Check-in date in YYYY-MM-DD format"
    )
    checkout: str = Field(
        ...,
        description="Check-out date in YYYY-MM-DD format"
    )
    rooms: Optional[int] = Field(
        1,
        description="Number of rooms"
    )
    adults: Optional[int] = Field(
        1,
        description="Number of adults"
    )
    childrenAges: Optional[str] = Field(
        None,
        description="Children ages separated by commas (e.g., '0,11,17')"
    )
    market: Optional[str] = Field(
        "US",
        description="Market (country code)"
    )
    locale: Optional[str] = Field(
        "en-US",
        description="Locale for response language"
    )
    currency: Optional[str] = Field(
        "USD",
        description="Currency for prices"
    )
    cookie: Optional[str] = Field(
        None,
        description="Cookie for handling captcha or slow latency"
    )

# Hotel prices response schema
class HotelPricesData(BaseModel):
    data: Optional[Dict[str, Any]] = None
    status: Optional[bool] = None
    message: Optional[str] = None

# Input schema for Hotel Reviews endpoint
class HotelReviewsParams(BaseModel):
    hotelId: str = Field(
        ...,
        description="Hotel ID from search results (data->results->hotelCards->hotelId)"
    )
    page: Optional[int] = Field(
        1,
        description="The page index for pagination"
    )
    sort: Optional[str] = Field(
        "recommended",
        description="Sort order (e.g., 'recommended', 'rating_desc', 'rating_asc', 'LAST_TWELVE_MONTHS')"
    )
    market: Optional[str] = Field(
        "US",
        description="Market (country code)"
    )
    locale: Optional[str] = Field(
        "en-US",
        description="Locale for response language"
    )
    currency: Optional[str] = Field(
        "USD",
        description="Currency for prices"
    )
    guestType: Optional[str] = Field(
        None,
        description="Traveler type filter (e.g., 'business', 'couple', 'group')"
    )
    filterLocale: Optional[str] = Field(
        None,
        description="Language filter (e.g., 'en-GB', 'fr-FR')"
    )
    tags: Optional[str] = Field(
        None,
        description="Tags filter (e.g., 'room', 'location', 'service')"
    )

# Hotel reviews response schema
class HotelReviewsData(BaseModel):
    data: Optional[Dict[str, Any]] = None
    status: Optional[bool] = None
    message: Optional[str] = None

# API Response
class ApiResponse(BaseModel):
    data: Union[SearchEverywhereData, SearchRoundtripData, SearchOneWayData, FlightDetailData, PriceCalendarData, CheapestOneWayData, HotelSearchData, HotelDetailData, HotelPricesData, HotelReviewsData]
    component: Optional[Dict[str, Any]] = None
