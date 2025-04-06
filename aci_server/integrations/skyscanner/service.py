from typing import Dict, Any, List, Optional, Union
import os
from .client import SkyscannerClient
from .schema import (
    SearchOneWayParams,
    SearchRoundtripParams,
    SearchMultiCityParams,
    FlightDetailsParams,
    PriceCalendarParams,
    PriceCalendarReturnParams,
    CheapestOneWayParams,
    SearchOneWayResponse,
    SearchRoundtripResponse,
    SearchMultiCityResponse,
    FlightDetailsResponse,
    PriceCalendarResponse,
    PriceCalendarReturnResponse,
    CheapestOneWayResponse,
    ApiResponse,
    SearchOneWayData,
    SearchRoundtripData,
    SearchMultiCityData,
    FlightDetailsData,
    PriceCalendarData,
    PriceCalendarReturnData,
    CheapestOneWayData,
    HotelSearchParams,
    HotelSearchResponse,
    HotelDetailParams,
    HotelDetailResponse,
    HotelPricesParams,
    HotelPricesResponse,
    HotelReviewsParams,
    HotelReviewsResponse
)
from ..common.component_handler import load_components, prepare_components_auto

class SkyscannerService:
    def __init__(self, client: SkyscannerClient):
        self.client = client
        self.components_data = self._load_components()

    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
    
    def prepare_response(self, data: Any, component_name: str = None) -> ApiResponse:
        tool_name = "skyscanner"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)

    def search_one_way(self, params: SearchOneWayParams) -> ApiResponse:
        processed_params = self._process_search_params(params)
        response = self.client.search_one_way(processed_params)
        
        validated_data = SearchOneWayData(**response)
        
        return self.prepare_response(validated_data, "FlightSearchResults")
    
    def search_roundtrip(self, params: SearchRoundtripParams) -> ApiResponse:
        processed_params = self._process_search_params(params)
        response = self.client.search_roundtrip(processed_params)
        
        validated_data = SearchRoundtripData(**response)
        
        return self.prepare_response(validated_data, "FlightSearchResults")
    
    def search_multi_city(self, params: SearchMultiCityParams) -> ApiResponse:
        processed_params = self._process_search_params(params)
        response = self.client.search_multi_city(processed_params)
        
        validated_data = SearchMultiCityData(**response)
        
        return self.prepare_response(validated_data, "FlightSearchResults")
    
    def price_calendar(self, params: PriceCalendarParams) -> ApiResponse:
        processed_params = self._process_search_params(params)
        response = self.client.price_calendar(processed_params)
        
        validated_data = PriceCalendarData(**response)
        
        return self.prepare_response(validated_data, "PriceCalendar")
    
    def price_calendar_return(self, params: PriceCalendarReturnParams) -> ApiResponse:
        processed_params = self._process_search_params(params)
        response = self.client.price_calendar_return(processed_params)
        
        validated_data = PriceCalendarReturnData(**response)
        
        return self.prepare_response(validated_data, "PriceCalendar")
    
    def cheapest_one_way(self, params: CheapestOneWayParams) -> ApiResponse:
        processed_params = self._process_search_params(params)
        response = self.client.cheapest_one_way(processed_params)
        
        validated_data = CheapestOneWayData(**response)
        
        return self.prepare_response(validated_data, "CheapestOneWay")
    
    def flight_details(self, params: FlightDetailsParams) -> ApiResponse:
        processed_params = self._process_search_params(params)
        response = self.client.flight_details(processed_params)
        
        validated_data = FlightDetailsData(**response)
        
        return self.prepare_response(validated_data, "FlightDetails")
    
    def search_hotels(self, params: HotelSearchParams) -> ApiResponse:
        """
        Search for hotels using the Skyscanner API
        
        Args:
            params: Validated parameters for hotel search
            
        Returns:
            API response with hotel search results
        """
        # Convert params to dict and exclude None values
        processed_params = params.model_dump(exclude_none=True)
        
        # Call the client with polling
        response = self.client.search_hotels(processed_params)
        
        # Validate response against expected format
        validated_response = HotelSearchResponse(**response)
        
        # Prepare and return the API response
        return self.prepare_response(validated_response, "HotelSearchResults")
    
    def hotel_detail(self, params: HotelDetailParams) -> ApiResponse:
        processed_params = params.model_dump(exclude_none=True)
        
        # Call the client
        response = self.client.hotel_detail(processed_params)
        
        # Validate response against expected format
        validated_response = HotelDetailResponse(**response)
        
        # Prepare and return the API response
        return self.prepare_response(validated_response, "HotelDetail")
    
    def hotel_prices(self, params: HotelPricesParams) -> ApiResponse:
        """
        Get pricing information for a specific hotel
        
        Args:
            params: Validated parameters for hotel prices request
            
        Returns:
            API response with hotel pricing details
        """
        # Convert params to dict and exclude None values
        processed_params = params.model_dump(exclude_none=True)
        
        # Call the client
        response = self.client.hotel_prices(processed_params)
        
        # Validate response against expected format
        validated_response = HotelPricesResponse(**response)
        
        # Prepare and return the API response
        return self.prepare_response(validated_response, "HotelPrices")
    
    def hotel_reviews(self, params: HotelReviewsParams) -> ApiResponse:
        """
        Get reviews for a specific hotel
        
        Args:
            params: Validated parameters for hotel reviews request
            
        Returns:
            API response with hotel reviews
        """
        # Convert params to dict and exclude None values
        processed_params = params.model_dump(exclude_none=True)
        
        # Call the client
        response = self.client.hotel_reviews(processed_params)
        
        # Validate response against expected format
        validated_response = HotelReviewsResponse(**response)
        
        # Prepare and return the API response
        return self.prepare_response(validated_response, "HotelReviews")
    
    def _process_search_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return params.model_dump(exclude_none=True)
