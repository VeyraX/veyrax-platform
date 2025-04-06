from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union, Literal

# Input schema classes
class PropertyParams(BaseModel):
    zpid: Optional[int] = Field(
        None,
        description="Unique ID that Zillow gives to each property"
    )
    property_url: Optional[str] = Field(
        None,
        description="Full page URL - https://www.zillow.com/homedetails/address-zipcode/zpid/"
    )
    address: Optional[str] = Field(
        None,
        description="Property address"
    )

class ZestimateParams(BaseModel):
    zpid: Optional[str] = Field(
        None,
        description="Unique ID that Zillow gives to each property"
    )
    property_url: Optional[str] = Field(
        None,
        description="Property page full URL"
    )
    address: Optional[str] = Field(
        None,
        description="Property address"
    )

class ZestimateHistoryParams(BaseModel):
    zpid: Optional[int] = Field(
        None,
        description="Unique ID that Zillow gives to each property"
    )
    property_url: Optional[str] = Field(
        None,
        description="Property page full URL"
    )
    address: Optional[str] = Field(
        None,
        description="Property address"
    )

class PriceAndTaxHistoryParams(BaseModel):
    zpid: Optional[str] = Field(
        None,
        description="Unique ID that Zillow gives to each property"
    )
    property_url: Optional[str] = Field(
        None,
        description="Property page full URL"
    )

class PropertyCompsParams(BaseModel):
    zpid: Optional[int] = Field(
        None,
        description="Unique ID that Zillow gives to each property"
    )
    property_url: Optional[str] = Field(
        None,
        description="Property page full URL"
    )
    address: Optional[str] = Field(
        None,
        description="Property address"
    )

class SimilarPropertiesParams(BaseModel):
    zpid: Optional[int] = Field(
        None,
        description="Unique ID that Zillow gives to each property"
    )
    property_url: Optional[str] = Field(
        None,
        description="Property page full URL - https://www.zillow.com/homedetails/address-zipcode/zpid/"
    )

class SimilarSalesParams(BaseModel):
    zpid: Optional[int] = Field(
        None,
        description="Unique ID that Zillow gives to each property"
    )
    property_url: Optional[str] = Field(
        None,
        description="Property page full URL - https://www.zillow.com/homedetails/address-zipcode/zpid/"
    )

class SimilarRentalsParams(BaseModel):
    zpid: Optional[int] = Field(
        None,
        description="Unique ID that Zillow gives to each property"
    )
    property_url: Optional[str] = Field(
        None,
        description="Property page full URL - https://www.zillow.com/homedetails/address-zipcode/zpid/"
    )

class PropertySearchParams(BaseModel):
    location: Optional[str] = Field(
        None,
        description="Location details (address, county, neighborhood or Zip code). Max 5 locations separated by ;"
    )
    page: Optional[int] = Field(
        None,
        description="Page number, max value is 20"
    )
    status_type: Optional[str] = Field(
        "ForSale",
        description="Status type: ForSale, ForRent, RecentlySold"
    )
    home_type: Optional[str] = Field(
        None,
        description="Property types: Houses, Townhomes, Apartments_Condos_Co-ops, Multi-family, Manufactured, Condos, LotsLand"
    )
    sort: Optional[str] = Field(
        None,
        description="Sort order for results"
    )
    polygon: Optional[str] = Field(
        None,
        description="Geographic polygon format: lon lat,lon1 lat1,lon2 lat2"
    )
    minPrice: Optional[int] = Field(
        None,
        description="Minimum price for ForSale or RecentlySold"
    )
    maxPrice: Optional[int] = Field(
        None,
        description="Maximum price for ForSale or RecentlySold"
    )
    rentMinPrice: Optional[int] = Field(
        None,
        description="Minimum rent price for ForRent"
    )
    rentMaxPrice: Optional[int] = Field(
        None,
        description="Maximum rent price for ForRent"
    )
    bathsMin: Optional[float] = Field(
        None,
        description="Minimum number of bathrooms"
    )
    bathsMax: Optional[float] = Field(
        None,
        description="Maximum number of bathrooms"
    )
    bedsMin: Optional[int] = Field(
        None,
        description="Minimum number of bedrooms"
    )
    bedsMax: Optional[int] = Field(
        None,
        description="Maximum number of bedrooms"
    )
    sqftMin: Optional[int] = Field(
        None,
        description="Minimum square feet"
    )
    sqftMax: Optional[int] = Field(
        None,
        description="Maximum square feet"
    )
    buildYearMin: Optional[int] = Field(
        None,
        description="Minimum year built"
    )
    buildYearMax: Optional[int] = Field(
        None,
        description="Maximum year built"
    )
    daysOn: Optional[str] = Field(
        None,
        description="Days on Zillow, values: 1,7,14,30,90,6m,12m,24m,36m"
    )
    soldInLast: Optional[str] = Field(
        None,
        description="Sold in last, values: 1,7,14,30,90,6m,12m,24m,36m"
    )
    keywords: Optional[str] = Field(
        None,
        description="Filter with keywords"
    )
    lotSizeMin: Optional[str] = Field(
        None,
        description="Minimum lot size"
    )
    lotSizeMax: Optional[str] = Field(
        None,
        description="Maximum lot size"
    )
    hoa: Optional[int] = Field(
        None,
        description="Maximum HOA fee"
    )
    coordinates: Optional[str] = Field(
        None,
        description="Format: lon lat,diameter. Diameter in miles from 1 to 99"
    )

# Response schema classes for individual models
class Address(BaseModel):
    city: Optional[str] = None
    neighborhood: Optional[str] = None
    state: Optional[str] = None
    streetAddress: Optional[str] = None
    zipcode: Optional[str] = None

class Phone(BaseModel):
    prefix: Optional[str] = None
    areacode: Optional[str] = None
    number: Optional[str] = None

class ContactRecipient(BaseModel):
    agent_reason: Optional[int] = None
    zpro: Optional[Any] = None
    recent_sales: Optional[int] = None
    review_count: Optional[int] = None
    display_name: Optional[str] = None
    zuid: Optional[str] = None
    rating_average: Optional[float] = None
    badge_type: Optional[str] = None
    phone: Optional[Phone] = None
    image_url: Optional[str] = None

class ListedBy(BaseModel):
    agent_reason: Optional[int] = None
    zpro: Optional[bool] = None
    recent_sales: Optional[int] = None
    review_count: Optional[int] = None
    display_name: Optional[str] = None
    badge_type: Optional[str] = None
    business_name: Optional[str] = None
    rating_average: Optional[float] = None
    phone: Optional[Phone] = None
    zuid: Optional[str] = None
    image_url: Optional[str] = None

class MortgageRates(BaseModel):
    arm5Rate: Optional[float] = None
    fifteenYearFixedRate: Optional[float] = None
    thirtyYearFixedRate: Optional[float] = None

class NearbyHome(BaseModel):
    zpid: Optional[int] = None
    longitude: Optional[float] = None
    address: Optional[Address] = None
    price: Optional[int] = None
    homeType: Optional[str] = None
    homeStatus: Optional[str] = None
    currency: Optional[str] = None
    latitude: Optional[float] = None

class School(BaseModel):
    link: Optional[str] = None
    rating: Optional[int] = None
    totalCount: Optional[int] = None
    distance: Optional[float] = None
    assigned: Optional[Any] = None
    name: Optional[str] = None
    studentsPerTeacher: Optional[int] = None
    isAssigned: Optional[bool] = None
    size: Optional[int] = None
    level: Optional[str] = None
    grades: Optional[str] = None
    type: Optional[str] = None

# Main property information model
class Property(BaseModel):
    zpid: Optional[int] = None
    streetAddress: Optional[str] = None
    zipcode: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    price: Optional[int] = None
    homeStatus: Optional[str] = None
    homeType: Optional[str] = None
    livingArea: Optional[int] = None
    livingAreaUnits: Optional[str] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    yearBuilt: Optional[int] = None
    url: Optional[str] = None
    imgSrc: Optional[str] = None
    description: Optional[str] = None
    timeOnZillow: Optional[str] = None
    monthlyHoaFee: Optional[int] = None
    currency: Optional[str] = None
    address: Optional[Address] = None
    listed_by: Optional[ListedBy] = None
    mortgageRates: Optional[MortgageRates] = None
    propertyTaxRate: Optional[float] = None
    contact_recipients: Optional[List[ContactRecipient]] = None
    nearbyHomes: Optional[List[NearbyHome]] = None
    schools: Optional[List[School]] = None
    favoriteCount: Optional[int] = None
    pageViewCount: Optional[int] = None

class PropertySearchResult(BaseModel):
    zpid: Optional[str] = None
    address: Optional[str] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    price: Optional[int] = None
    homeStatus: Optional[str] = None
    homeType: Optional[str] = None
    livingArea: Optional[int] = None
    lotAreaValue: Optional[float] = None
    lotAreaUnit: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    imgSrc: Optional[str] = None
    hasImage: Optional[bool] = None
    currency: Optional[str] = None
    country: Optional[str] = None
    dateSold: Optional[str] = None
    daysOnZillow: Optional[int] = None
    propertyType: Optional[str] = None
    listingStatus: Optional[str] = None

class Zestimate(BaseModel):
    value: int

class ZestimateHistoryPoint(BaseModel):
    t: int  # Timestamp
    v: int  # Value

class PropertySearchResponse(BaseModel):
    props: List[PropertySearchResult]
    resultsPerPage: int
    totalPages: int
    totalResultCount: int
    currentPage: int

# List container model (to avoid direct List in ApiResponse)
class PropertyList(BaseModel):
    properties: List[Property]

class PropertySearchResultList(BaseModel):
    results: PropertySearchResponse

class ZestimateHistoryList(BaseModel):
    history: List[ZestimateHistoryPoint]

# Response models for endpoints
class PropertyResponse(BaseModel):
    data: Property

class PropertiesResponse(BaseModel):
    data: PropertyList

class PropertySearchResponseModel(BaseModel):
    data: PropertySearchResultList

class ZestimateResponse(BaseModel):
    data: Zestimate

class ZestimateHistoryResponse(BaseModel):
    data: ZestimateHistoryList

class AttributeSource(BaseModel):
    infoString1: Optional[str] = None
    infoString2: Optional[str] = None
    infoString3: Optional[str] = None

class Agent(BaseModel):
    name: Optional[str] = None
    photo: Optional[str] = None
    profileUrl: Optional[str] = None

class PriceHistoryItem(BaseModel):
    priceChangeRate: Optional[float] = None
    date: Optional[str] = None
    source: Optional[str] = None
    postingIsRental: Optional[bool] = None
    time: Optional[int] = None
    sellerAgent: Optional[Agent] = None
    showCountyLink: Optional[bool] = None
    attributeSource: Optional[AttributeSource] = None
    pricePerSquareFoot: Optional[float] = None
    buyerAgent: Optional[Agent] = None
    event: Optional[str] = None
    price: Optional[float] = None

class TaxHistoryItem(BaseModel):
    time: Optional[int] = None
    valueIncreaseRate: Optional[float] = None
    taxIncreaseRate: Optional[float] = None
    taxPaid: Optional[float] = None
    value: Optional[float] = None

class PriceAndTaxHistory(BaseModel):
    priceHistory: List[PriceHistoryItem]
    taxHistory: List[TaxHistoryItem]

class PriceAndTaxHistoryList(BaseModel):
    priceAndTaxHistory: PriceAndTaxHistory

class PriceAndTaxHistoryResponse(BaseModel):
    data: PriceAndTaxHistoryList

class FormattedChipLocation(BaseModel):
    fullValue: Optional[str] = None

class FormattedChip(BaseModel):
    location: Optional[List[FormattedChipLocation]] = None

class ParentRegion(BaseModel):
    name: Optional[str] = None

class AttributionInfo(BaseModel):
    agentPhoneNumber: Optional[str] = None
    trueStatus: Optional[str] = None
    providerLogo: Optional[str] = None
    mlsId: Optional[str] = None
    brokerName: Optional[str] = None
    mlsName: Optional[str] = None
    brokerPhoneNumber: Optional[str] = None
    agentName: Optional[str] = None

class ListingSubType(BaseModel):
    is_FSBA: Optional[bool] = None
    is_forAuction: Optional[bool] = None
    is_comingSoon: Optional[bool] = None
    is_foreclosure: Optional[bool] = None
    is_bankOwned: Optional[bool] = None
    is_newHome: Optional[bool] = None
    is_FSBO: Optional[bool] = None

class ListingMetadata(BaseModel):
    comminglingCategoryIsRulesApplicable: Optional[bool] = None

class MiniCardPhoto(BaseModel):
    url: Optional[str] = None

class CompProperty(BaseModel):
    bathrooms: Optional[float] = None
    newConstructionType: Optional[str] = None
    lotAreaUnits: Optional[str] = None
    formattedChip: Optional[FormattedChip] = None
    isPremierBuilder: Optional[bool] = None
    isShowcaseListing: Optional[bool] = None
    hdpUrl: Optional[str] = None
    lotAreaValue: Optional[float] = None
    parentRegion: Optional[ParentRegion] = None
    address: Optional[Address] = None
    state: Optional[str] = None
    attributionInfo: Optional[AttributionInfo] = None
    latitude: Optional[float] = None
    homeStatus: Optional[str] = None
    listing_sub_type: Optional[ListingSubType] = None
    price: Optional[float] = None
    listingMetadata: Optional[ListingMetadata] = None
    bedrooms: Optional[int] = None
    propertyTypeDimension: Optional[str] = None
    listingTypeDimension: Optional[str] = None
    lotSize: Optional[float] = None
    miniCardPhotos: Optional[List[MiniCardPhoto]] = None
    zpid: Optional[int] = None
    hdpTypeDimension: Optional[str] = None
    livingArea: Optional[float] = None
    longitude: Optional[float] = None
    livingAreaUnitsShort: Optional[str] = None
    providerListingID: Optional[str] = None
    homeType: Optional[str] = None
    currency: Optional[str] = None
    livingAreaUnits: Optional[str] = None
    livingAreaValue: Optional[float] = None

class PropertyComps(BaseModel):
    comps: List[CompProperty]

class PropertyCompsList(BaseModel):
    propertyComps: PropertyComps

class PropertyCompsResponse(BaseModel):
    data: PropertyCompsList

class SimilarPropertyList(BaseModel):
    similarProperties: List[CompProperty]

class SimilarPropertyResponse(BaseModel):
    data: SimilarPropertyList

class SimilarSalesResponse(BaseModel):
    data: SimilarPropertyList

class SimilarRentalsResponse(BaseModel):
    data: SimilarPropertyList

class PropertyValueRangeParams(BaseModel):
    address: Optional[str] = Field(
        None,
        description="Property address"
    )
    lat: Optional[float] = Field(
        None,
        description="Latitude coordinate"
    )
    long: Optional[float] = Field(
        None,
        description="Longitude coordinate"
    )
    d: Optional[float] = Field(
        0.5,
        description="Diameter in miles (0.05-1.5, default 0.5)"
    )
    propertyType: Optional[str] = Field(
        "SingleFamily",
        description="Property type (SingleFamily, MultiFamily, Condo, etc.)"
    )
    beds: Optional[int] = Field(
        None,
        description="Number of bedrooms"
    )
    baths: Optional[float] = Field(
        None,
        description="Number of bathrooms"
    )
    sqftMin: Optional[str] = Field(
        None,
        description="Minimum square footage"
    )
    sqftMax: Optional[str] = Field(
        None,
        description="Maximum square footage"
    )

class PropertyValueRange(BaseModel):
    percentile_25: Optional[float] = None
    skippedRecords: Optional[int] = None
    lowValue: Optional[float] = None
    lat: Optional[float] = None
    long: Optional[float] = None
    highValue: Optional[float] = None
    comparableProperties: Optional[int] = None
    percentile_75: Optional[float] = None
    median: Optional[float] = None

class PropertyValueRangeList(BaseModel):
    valueRange: PropertyValueRange

class MarketLocationParams(BaseModel):
    location: str = Field(
        ...,
        description="Location name (e.g., 'Orlando, FL')"
    )

class MarketDataParams(BaseModel):
    resourceId: str = Field(
        ...,
        description="Resource ID from the marketLocation endpoint"
    )
    beds: Optional[int] = Field(
        None,
        description="Number of bedrooms: 0 (Studio), 1, 2, 3, 4plus"
    )
    propertyTypes: Optional[str] = Field(
        None,
        description="Property type, e.g., house, apartment, condo"
    )

class MarketLocation(BaseModel):
    longName: Optional[str] = None
    resourceId: Optional[str] = None
    areaId: Optional[str] = None
    type: Optional[str] = None

class MarketLocationList(BaseModel):
    marketLocations: List[MarketLocation]

class MarketLocationResponse(BaseModel):
    data: MarketLocationList

class PricePoint(BaseModel):
    price: Optional[float] = None
    year: Optional[str] = None
    month: Optional[str] = None

class PriceHistogram(BaseModel):
    maxPrice: Optional[float] = None
    minPrice: Optional[float] = None
    priceAndCount: Optional[List[Dict[str, Any]]] = None

class RentCompare(BaseModel):
    medianRent: Optional[float] = None
    areaName: Optional[str] = None

class AreaInfo(BaseModel):
    city: Optional[str] = None
    resourceName: Optional[str] = None
    areaType: Optional[str] = None
    name: Optional[str] = None
    areaId: Optional[int] = None
    state: Optional[str] = None

class MarketTemperature(BaseModel):
    temperature: Optional[str] = None
    areaName: Optional[str] = None

class MarketSummary(BaseModel):
    monthlyChange: Optional[float] = None
    yearlyChange: Optional[float] = None
    avgDaysOnMarket: Optional[int] = None
    availableRentals: Optional[int] = None
    medianRent: Optional[float] = None

class MarketData(BaseModel):
    medianRentPriceOverTime: Optional[Dict[str, Any]] = None
    zipcodesInCity: Optional[List[AreaInfo]] = None
    date: Optional[str] = None
    areaType: Optional[str] = None
    rentHistogram: Optional[PriceHistogram] = None
    rentCompare: Optional[RentCompare] = None
    nearByAreas: Optional[List[AreaInfo]] = None
    zillowRentalsSrpUrl: Optional[str] = None
    marketTemperature: Optional[MarketTemperature] = None
    summary: Optional[MarketSummary] = None

class MarketDataResponse(BaseModel):
    data: MarketData

class PropertyValueRangeResponse(BaseModel):
    data: PropertyValueRangeList

# Generic API Response
class ApiResponse(BaseModel):
    data: Union[Property, PropertyList, PropertySearchResultList, Zestimate, ZestimateHistoryList, PriceAndTaxHistoryList, PropertyCompsList, PropertyValueRangeList, SimilarPropertyList, MarketLocationList, MarketData]
    component: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None
