from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union, Literal

# Input schema
class SearchOneWayParams(BaseModel):
    fromEntityId: str = Field(
        ...,
        description="From location (e.g., 'PARI' for Paris)"
    )
    toEntityId: Optional[str] = Field(
        None,
        description="To location (default: everywhere)"
    )
    departDate: Optional[str] = Field(
        None,
        description="Depart date in YYYY-MM-DD format (default: anytime)"
    )
    wholeMonthDepart: Optional[str] = Field(
        None,
        description="Whole month depart in YYYY-MM format"
    )
    market: Optional[str] = Field(
        "US",
        description="Market (e.g., 'US')"
    )
    locale: Optional[str] = Field(
        "en-US",
        description="Locale (e.g., 'en-US')"
    )
    currency: Optional[str] = Field(
        "USD",
        description="Currency (e.g., 'USD')"
    )
    stops: Optional[str] = Field(
        None,
        description="Stops filter (e.g., 'direct,1stop')"
    )
    children: Optional[int] = Field(
        0,
        ge=0,
        description="Number of children (2-12 years)"
    )
    infants: Optional[int] = Field(
        0,
        ge=0,
        description="Number of infants (under 2 years)"
    )
    cabinClass: Optional[Literal["economy", "premium_economy", "business", "first"]] = Field(
        "economy",
        description="Cabin class"
    )
    adults: Optional[int] = Field(
        1,
        ge=1,
        description="Number of adults (12+ years)"
    )
    sort: Optional[str] = Field(
        None,
        description="Sort order (e.g., 'cheapest_first')"
    )
    airlines: Optional[str] = Field(
        None,
        description="Airline filter (comma-separated airline IDs)"
    )

class SearchRoundtripParams(BaseModel):
    fromEntityId: str = Field(
        ...,
        description="From location (e.g., 'PARI' for Paris)"
    )
    toEntityId: Optional[str] = Field(
        None,
        description="To location (default: everywhere)"
    )
    departDate: Optional[str] = Field(
        None,
        description="Depart date in YYYY-MM-DD format (default: anytime)"
    )
    returnDate: Optional[str] = Field(
        None,
        description="Return date in YYYY-MM-DD format (default: anytime)"
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
        description="Market (e.g., 'US')"
    )
    locale: Optional[str] = Field(
        "en-US",
        description="Locale (e.g., 'en-US')"
    )
    currency: Optional[str] = Field(
        "USD",
        description="Currency (e.g., 'USD')"
    )
    stops: Optional[str] = Field(
        None,
        description="Stops filter (e.g., 'direct,1stop')"
    )
    adults: Optional[int] = Field(
        1,
        ge=1,
        description="Number of adults (12+ years)"
    )
    children: Optional[int] = Field(
        0,
        ge=0,
        description="Number of children (2-12 years)"
    )
    infants: Optional[int] = Field(
        0,
        ge=0,
        description="Number of infants (under 2 years)"
    )
    cabinClass: Optional[Literal["economy", "premium_economy", "business", "first"]] = Field(
        "economy",
        description="Cabin class"
    )
    sort: Optional[str] = Field(
        None,
        description="Sort order (e.g., 'cheapest_first')"
    )
    airlines: Optional[str] = Field(
        None,
        description="Airline filter (comma-separated airline IDs)"
    )

class FlightLeg(BaseModel):
    fromEntityId: str = Field(
        ...,
        description="Origin location ID"
    )
    toEntityId: str = Field(
        ...,
        description="Destination location ID"
    )
    departDate: str = Field(
        ...,
        description="Departure date in YYYY-MM-DD format"
    )

class SearchMultiCityParams(BaseModel):
    flights: List[FlightLeg] = Field(
        ...,
        description="List of flight legs for multi-city itinerary",
        min_items=2
    )
    market: Optional[str] = Field(
        "US",
        description="Market (e.g., 'US')"
    )
    locale: Optional[str] = Field(
        "en-US",
        description="Locale (e.g., 'en-US')"
    )
    currency: Optional[str] = Field(
        "USD",
        description="Currency (e.g., 'USD')"
    )
    adults: Optional[int] = Field(
        1,
        ge=1,
        description="Number of adults (12+ years)"
    )
    children: Optional[int] = Field(
        0,
        ge=0,
        description="Number of children (2-12 years)"
    )
    infants: Optional[int] = Field(
        0,
        ge=0,
        description="Number of infants (under 2 years)"
    )
    cabinClass: Optional[Literal["economy", "premium_economy", "business", "first"]] = Field(
        "economy",
        description="Cabin class"
    )
    stops: Optional[List[str]] = Field(
        None,
        description="Stops filter as list (e.g., ['direct', '1stop', '2stops'])"
    )
    sort: Optional[str] = Field(
        None,
        description="Sort order (e.g., 'cheapest_first')"
    )
    airlines: Optional[List[int]] = Field(
        None,
        description="Airline filter as list of airline IDs"
    )
    cookie: Optional[str] = Field(
        "",
        description="Cookie for handling captcha errors"
    )

class PriceCalendarParams(BaseModel):
    fromEntityId: str = Field(
        ...,
        description="From location (e.g., 'CDG' for Paris Charles de Gaulle)"
    )
    departDate: Optional[str] = Field(
        None,
        description="Depart date in YYYY-MM-DD format"
    )
    toEntityId: Optional[str] = Field(
        None,
        description="To location (e.g., 'JFK' for New York John F. Kennedy)"
    )
    market: Optional[str] = Field(
        "US",
        description="Market (e.g., 'US')"
    )
    locale: Optional[str] = Field(
        "en-US",
        description="Locale (e.g., 'en-US')"
    )
    currency: Optional[str] = Field(
        "USD",
        description="Currency (e.g., 'USD')"
    )
    cookie: Optional[str] = Field(
        None,
        description="Cookie for handling captcha errors"
    )

class PriceCalendarReturnParams(BaseModel):
    fromEntityId: str = Field(
        ...,
        description="From location (e.g., 'CDG' for Paris Charles de Gaulle)"
    )
    departDate: Optional[str] = Field(
        None,
        description="Depart date in YYYY-MM-DD format"
    )
    returnDate: Optional[str] = Field(
        None,
        description="Return date in YYYY-MM-DD format"
    )
    toEntityId: Optional[str] = Field(
        None,
        description="To location (e.g., 'JFK' for New York John F. Kennedy)"
    )
    market: Optional[str] = Field(
        "US",
        description="Market (e.g., 'US')"
    )
    locale: Optional[str] = Field(
        "en-US",
        description="Locale (e.g., 'en-US')"
    )
    currency: Optional[str] = Field(
        "USD",
        description="Currency (e.g., 'USD')"
    )
    cookie: Optional[str] = Field(
        None,
        description="Cookie for handling captcha errors"
    )

class FlightDetailsParams(BaseModel):
    token: str = Field(
        ...,
        description="Token from search results"
    )
    itineraryId: str = Field(
        ...,
        description="Itinerary ID from search results"
    )
    market: Optional[str] = Field(
        "US",
        description="Market (e.g., 'US')"
    )
    locale: Optional[str] = Field(
        "en-US",
        description="Locale (e.g., 'en-US')"
    )
    currency: Optional[str] = Field(
        "USD",
        description="Currency (e.g., 'USD')"
    )

class CheapestOneWayParams(BaseModel):
    fromEntityId: str = Field(
        ...,
        description="From location (e.g., 'CDG' for Paris Charles de Gaulle)"
    )
    toEntityId: str = Field(
        ...,
        description="To location (e.g., 'JFK' for New York John F. Kennedy)"
    )
    departDate: Optional[str] = Field(
        None,
        description="Depart date in YYYY-MM-DD format"
    )
    market: Optional[str] = Field(
        "US",
        description="Market (e.g., 'US')"
    )
    locale: Optional[str] = Field(
        "en-US",
        description="Locale (e.g., 'en-US')"
    )
    currency: Optional[str] = Field(
        "USD",
        description="Currency (e.g., 'USD')"
    )
    cookie: Optional[str] = Field(
        None,
        description="Cookie for handling captcha errors"
    )

# Output schema
class Airport(BaseModel):
    id: str
    name: str

class City(BaseModel):
    city: str
    airports: List[Airport]

class Carrier(BaseModel):
    id: int
    logoUrl: str
    name: str

class PriceInfo(BaseModel):
    isPresent: bool
    formattedPrice: Optional[str] = None

class StopPrices(BaseModel):
    direct: Dict[str, Any]
    one: Optional[PriceInfo] = None
    twoOrMore: Optional[PriceInfo] = None

class DurationStats(BaseModel):
    min: int
    max: int
    multiCityMin: int
    multiCityMax: int

class FilterStats(BaseModel):
    duration: DurationStats
    airports: List[City]
    carriers: List[Carrier]
    stopPrices: StopPrices

class ItineraryList(BaseModel):
    items: List[Dict[str, Any]]

class SearchContext(BaseModel):
    status: str
    sessionId: str
    totalResults: int
    itineraries: ItineraryList
    messages: List[Any]
    filterStats: FilterStats
    flightsSessionId: str
    destinationImageUrl: Optional[str] = None
    token: str

class SearchOneWayData(BaseModel):
    context: SearchContext
    status: bool
    message: str

class SearchRoundtripData(BaseModel):
    context: SearchContext
    status: bool
    message: str

class SearchMultiCityData(BaseModel):
    context: SearchContext
    status: bool
    message: str

class PriceGroup(BaseModel):
    id: str
    label: str

class PriceDay(BaseModel):
    day: str
    group: str
    price: float

class PriceCalendarFlights(BaseModel):
    noPriceLabel: str
    groups: List[PriceGroup]
    days: List[PriceDay]
    currency: str

class PriceCalendarData(BaseModel):
    flights: PriceCalendarFlights
    status: bool
    message: str

class PriceCalendarReturnData(BaseModel):
    flights: PriceCalendarFlights
    status: bool
    message: str

class AirportDetail(BaseModel):
    id: str
    name: str
    displayCode: str
    city: str

class Carrier(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    logoUrl: Optional[str] = None

class Segment(BaseModel):
    id: str
    origin: AirportDetail
    destination: AirportDetail
    duration: int
    dayChange: int
    flightNumber: str
    departure: str
    arrival: str
    marketingCarrier: Carrier
    operatingCarrier: Optional[Carrier] = None
    goodToKnowItems: List[Dict[str, Any]] = []

class Layover(BaseModel):
    segmentId: str
    origin: AirportDetail
    destination: AirportDetail
    duration: int

class Leg(BaseModel):
    id: str
    origin: AirportDetail
    destination: AirportDetail
    segments: List[Segment]
    layovers: List[Layover] = []
    duration: int
    stopCount: int
    departure: str
    arrival: str
    dayChange: int

class Agent(BaseModel):
    id: str
    name: str
    isCarrier: bool
    bookingProposition: Optional[str] = None
    url: str
    price: int
    rating: Optional[Dict[str, Any]] = None

class PricingOption(BaseModel):
    agents: List[Agent]
    transferProtection: Optional[str] = None
    isDirectDBookUrl: bool
    quoteAge: int
    totalPrice: int
    fare: Dict[str, Any]

class TransferProtectionDetails(BaseModel):
    title: str
    body: str
    url: str
    urlTitle: str

class FlightItinerary(BaseModel):
    id: str
    legs: List[Leg]
    pricingOptions: List[PricingOption]
    isTransferRequired: bool
    destinationImage: Optional[str] = None
    operatingCarrierSafetyAttributes: List[Dict[str, Any]] = []
    flexibleTicketPolicies: List[Any] = []
    transferProtectionDetails: Optional[TransferProtectionDetails] = None
    pollingCompleted: bool
    bookingSessionId: str

class FlightDetailsData(BaseModel):
    itinerary: FlightItinerary
    status: bool
    message: str

class SearchOneWayResponse(BaseModel):
    data: SearchOneWayData

class SearchRoundtripResponse(BaseModel):
    data: SearchRoundtripData

class SearchMultiCityResponse(BaseModel):
    data: SearchMultiCityData

class PriceCalendarResponse(BaseModel):
    data: PriceCalendarData

class PriceCalendarReturnResponse(BaseModel):
    data: PriceCalendarReturnData

class FlightDetailsResponse(BaseModel):
    data: FlightDetailsData

class CheapestOneWayData(BaseModel):
    flights: PriceCalendarFlights
    status: bool
    message: str

class CheapestOneWayResponse(BaseModel):
    data: CheapestOneWayData

# Input Schemas
class HotelSearchParams(BaseModel):
    entityId: str = Field(..., description="Entity ID for location search, can be retrieved from auto-complete endpoint")
    checkin: str = Field(..., description="Check-in date in YYYY-MM-DD format")
    checkout: str = Field(..., description="Check-out date in YYYY-MM-DD format")
    resultsPerPage: Optional[int] = Field(25, description="Total number of records per API call")
    page: Optional[int] = Field(1, description="The page index, for paging purpose")
    rooms: Optional[int] = Field(1, description="Number of rooms")
    adults: Optional[int] = Field(1, description="Number of adults")
    childrenAges: Optional[str] = Field(None, description="Ages of children, comma-separated (e.g., '0,11,17')")
    market: Optional[str] = Field("US", description="Market code")
    locale: Optional[str] = Field("en-US", description="Locale code")
    currency: Optional[str] = Field("USD", description="Currency code")
    sorting: Optional[str] = Field("-relevance", description="Sorting option")
    priceType: Optional[str] = Field("PRICE_PER_NIGHT", description="Price type (PRICE_PER_NIGHT or PRICE_TOTAL)")
    minPrice: Optional[str] = Field(None, description="Minimum price (with max one decimal digit)")
    maxPrice: Optional[str] = Field(None, description="Maximum price (with max one decimal digit)")
    confidentType: Optional[str] = Field(None, description="Book with peace of mind options, comma-separated")
    stars: Optional[str] = Field(None, description="Star rating, comma-separated")
    mealPlan: Optional[str] = Field(None, description="Meal plan, comma-separated")
    rating: Optional[str] = Field(None, description="Guest rating, comma-separated")
    guestType: Optional[str] = Field(None, description="Popular with, comma-separated")
    chain: Optional[str] = Field(None, description="Hotel chain, comma-separated")
    cancellation: Optional[str] = Field(None, description="Cancellation policy, comma-separated")
    amenities: Optional[str] = Field(None, description="Amenities, comma-separated")
    propertyType: Optional[str] = Field(None, description="Accommodation type, comma-separated")
    district: Optional[str] = Field(None, description="Neighborhoods, comma-separated")
    discountTypes: Optional[str] = Field(None, description="Deals, comma-separated")
    cookie: Optional[str] = Field(None, description="Cookie for handling captcha errors or slow latency")

# Hotel Data Models
class Coordinates(BaseModel):
    latitude: float
    longitude: float

class EntityInfo(BaseModel):
    entityId: str
    entityType: str
    name: str
    coordinates: Optional[Coordinates] = None
    levelOfEntityType: Optional[str] = None

class LocationInfo(BaseModel):
    entityId: str
    entityType: str
    name: str

class SearchSummary(BaseModel):
    total: int
    filteredTotal: int
    inboundTotal: int
    resultsSummary: str
    sortBy: str
    entity: EntityInfo
    location: List[LocationInfo]

class MapBoundary(BaseModel):
    north: float
    east: float
    south: float
    west: float

class HotelsRegion(BaseModel):
    latitude: float
    longitude: float
    longitudeDelta: float
    latitudeDelta: float

class HotelPrice(BaseModel):
    price: str
    rawPrice: int
    partnerId: str
    partnerType: str
    partnerName: str
    partnerLogo: str
    isOfficial: bool
    funnelType: str
    cug: Optional[Any] = None
    discount: Optional[Any] = None
    amenities: List[Any]

class HotelCard(BaseModel):
    id: str
    name: str
    stars: str
    distance: str
    relevantPoiDistance: Optional[str] = None
    coordinates: Coordinates
    pivot: bool
    images: List[str]
    reviewsSummary: Dict[str, Any] = {}
    confidentMessages: List[Any] = []
    minPriceDbookRoomId: Optional[Any] = None
    minPriceDbookPartnerId: Optional[Any] = None
    inbound: bool
    lowestPrice: HotelPrice
    otherPrices: List[Any] = []
    isUpSorted: bool
    hotelId: str

class SortOption(BaseModel):
    optionName: str
    type: str

class FilterOption(BaseModel):
    # Generic filter object
    pass

class HotelCoordinate(BaseModel):
    id: str
    latitude: float
    longitude: float
    price: str

class StatusInfo(BaseModel):
    completionPercentage: int
    searchId: str
    requestId: str
    fastSearchStatus: str
    finalStatus: str

class HotelSearchResults(BaseModel):
    priceType: str
    pricePolicy: str
    searchSummary: SearchSummary
    mapBoundary: MapBoundary
    hotelsRegion: HotelsRegion
    hotelCards: List[HotelCard]
    filters: List[FilterOption] = []
    hotelsCoordinates: List[HotelCoordinate]
    sortOptions: List[SortOption]
    travelInfos: List[Any] = []
    partnerList: List[str]

class MetaInfo(BaseModel):
    currentPage: int
    limit: int
    totalRecords: int
    totalPage: int

class HotelSearchData(BaseModel):
    results: HotelSearchResults
    status: StatusInfo
    error: Optional[Any] = None

class HotelSearchResponse(BaseModel):
    data: HotelSearchData
    meta: MetaInfo
    status: bool
    message: str

# Hotel Detail Input Schema
class HotelDetailParams(BaseModel):
    id: str = Field(..., description="Hotel ID from search results")
    market: Optional[str] = Field("US", description="Market code")
    locale: Optional[str] = Field("en-US", description="Locale code")
    currency: Optional[str] = Field("USD", description="Currency code")
    cookie: Optional[str] = Field(None, description="Cookie for handling captcha errors or slow latency")

# Hotel Detail Data Models
class CheckinCheckoutTime(BaseModel):
    title: str
    time: str

class RawAddress(BaseModel):
    nation: Optional[str] = None
    city: Optional[str] = None
    street_address: Optional[str] = None
    adm1: Optional[str] = None
    district: Optional[str] = None
    postcode: Optional[str] = None
    cityId: Optional[str] = None

class HotelDescription(BaseModel):
    title: str
    content: str
    image: Optional[str] = None
    translated: bool
    needTranslation: bool
    locale: str

class PolicyValue(BaseModel):
    content: str

class PolicyContent(BaseModel):
    icon: Optional[str] = None
    translated: bool
    needTranslation: bool
    locale: str
    key: str
    type: str
    values: List[PolicyValue]

class HotelPolicies(BaseModel):
    title: str
    content: List[PolicyContent]

class HotelGoodToKnow(BaseModel):
    title: str
    checkinTime: CheckinCheckoutTime
    checkoutTime: CheckinCheckoutTime
    description: HotelDescription
    policies: HotelPolicies

class HotelChildrenAndExtraBed(BaseModel):
    title: str
    content: List[Any]

class HotelLocation(BaseModel):
    title: str
    shortAddress: str
    address: str
    rawAddress: RawAddress
    coordinates: Coordinates
    cta: str

class GalleryCategory(BaseModel):
    name: str
    count: int
    displayName: str

class HotelGallery(BaseModel):
    images: List[Dict[str, Any]]
    categories: List[GalleryCategory]

class AmenityItem(BaseModel):
    icon: str
    description: str

class AmenityCategory(BaseModel):
    id: str
    category: str
    items: List[Dict[str, Any]]

class HotelAmenities(BaseModel):
    title: str
    ctaAll: str
    ctaLess: str
    content: List[AmenityItem]
    contentV2: List[AmenityCategory]

class ReviewExplanation(BaseModel):
    title: str
    content: str

class ReviewCategory(BaseModel):
    type: str
    score: str
    formatScore: str
    color: str
    name: str
    highlights: str
    description: Optional[str] = None

class HighScoreReview(BaseModel):
    type: str
    score: str
    icon: str
    text: str

class ReviewRatingSummary(BaseModel):
    scoreLogoImageUrl: str
    score: str
    formatScore: str
    totalScore: str
    count: str
    countNumber: int
    formatCountString: str
    color: str
    scoreDesc: str
    highlights: str
    categories: List[ReviewCategory]
    cleanlinessMessage: Optional[str] = None
    locationMessage: Optional[str] = None
    highScoreReviews: List[HighScoreReview]

class HotelReviews(BaseModel):
    title: str
    newTitle: str
    cta: str
    summaryDescription: str
    rating: int
    ratingDescription: str
    ratingDescriptionText: str
    numberOfReviewsLabel: str
    numberOfReviewsLabelExpanded: str
    badges: List[Any]
    guests: Dict[str, Any]
    categories: Dict[str, Any]
    explanations: List[ReviewExplanation]

class HotelGeneral(BaseModel):
    name: str
    stars: int

class HotelDetailData(BaseModel):
    general: HotelGeneral
    goodToKnow: HotelGoodToKnow
    childrenAndExtraBed: HotelChildrenAndExtraBed
    location: HotelLocation
    gallery: HotelGallery
    amenities: HotelAmenities
    reviews: HotelReviews
    distance: str
    reviewRatingSummary: ReviewRatingSummary

class HotelDetailResponse(BaseModel):
    data: HotelDetailData
    status: bool
    message: str

class HotelPricesParams(BaseModel):
    hotelId: str = Field(..., description="Hotel ID from search results")
    checkin: str = Field(..., description="Check-in date in YYYY-MM-DD format")
    checkout: str = Field(..., description="Check-out date in YYYY-MM-DD format")
    rooms: Optional[int] = Field(1, description="Number of rooms")
    adults: Optional[int] = Field(1, description="Number of adults")
    childrenAges: Optional[str] = Field(None, description="Ages of children, comma-separated (e.g., '0,11,17')")
    market: Optional[str] = Field("US", description="Market code")
    locale: Optional[str] = Field("en-US", description="Locale code")
    currency: Optional[str] = Field("USD", description="Currency code")
    cookie: Optional[str] = Field(None, description="Cookie for handling captcha errors or slow latency")

class MetaInfoRate(BaseModel):
    pass

class MetaInfo(BaseModel):
    ratesCta: str
    rates: List[MetaInfoRate] = []

class CheapestPrice(BaseModel):
    price: str
    totalWithTaxes: str
    funnelType: str
    partnerId: str
    rateAttributes: List[Any] = []
    rawPrice: int

class NoOfferPartner(BaseModel):
    partner_type: str
    logo: str
    name: str
    website_id: str
    is_dbook: bool
    is_official: bool

class HotelPricesData(BaseModel):
    metaInfo: MetaInfo
    roomTypes: List[Any] = []
    cheapestPrice: CheapestPrice
    exclusiveDeal: Optional[Any] = None
    mostPopularRates: List[Dict[str, Any]] = []
    noOfferPartners: List[NoOfferPartner] = []
    isShowMostPopularSeeAll: bool
    policyInfo: str
    otaRates: List[Dict[str, Any]] = []
    localCurrency: str
    searchId: str
    requestId: str

class HotelPricesResponse(BaseModel):
    data: HotelPricesData
    status: bool
    message: str

# Hotel Reviews Input Schema
class HotelReviewsParams(BaseModel):
    """
    Parameters for hotel reviews request
    """
    hotelId: str = Field(..., description="The ID of the hotel to get reviews for")
    filter: Optional[Dict[str, Any]] = Field(None, description="Optional filters for the reviews")
    sort: Optional[str] = Field(None, description="Optional sorting criteria for reviews")
    limit: Optional[int] = Field(None, description="Optional limit for number of reviews to return")
    offset: Optional[int] = Field(None, description="Optional offset for pagination")
    
class HotelReviewsResponse(BaseModel):
    """
    Response model for hotel reviews
    """
    data: Dict[str, Any] = Field(..., description="The response data containing reviews information")
    reviews: List[Dict[str, Any]] = Field(..., description="List of reviews for the hotel")
    searchStatus: Dict[str, Any] = Field(..., description="Status of the search request")
    title: Dict[str, Any] = Field(..., description="Title information for the reviews section")
    cta: Optional[Dict[str, Any]] = Field(None, description="Call to action information")
    filters: Dict[str, Any] = Field(..., description="Available filters for the reviews")

# API Response
class ApiResponse(BaseModel):
    data: Union[SearchOneWayData, SearchRoundtripData, SearchMultiCityData, FlightDetailsData, PriceCalendarData, PriceCalendarReturnData, CheapestOneWayData, HotelSearchResponse, HotelDetailResponse, HotelPricesResponse, HotelReviewsResponse]
    component: Optional[Dict[str, Any]] = None
