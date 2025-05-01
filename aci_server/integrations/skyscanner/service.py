import os
from typing import Dict, Any
from .client import SkyscannerClient
from .schema import (
    SearchEverywhereParams,
    SearchEverywhereData,
    SearchRoundtripParams,
    SearchRoundtripData,
    SearchOneWayParams,
    SearchOneWayData,
    FlightDetailParams,
    FlightDetailData,
    PriceCalendarParams,
    PriceCalendarData,
    PriceCalendarReturnParams,
    CheapestOneWayParams,
    CheapestOneWayData,
    HotelSearchParams,
    HotelSearchData,
    HotelDetailParams,
    HotelDetailData,
    HotelPricesParams,
    HotelPricesData,
    HotelReviewsParams,
    HotelReviewsData,
    ApiResponse
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

    def search_everywhere(self, params: SearchEverywhereParams) -> ApiResponse:
        processed_params = params.model_dump(exclude_none=True)
        
        response = self.client.search_everywhere(processed_params)
        
        if 'everywhereDestination' in response and 'results' in response['everywhereDestination']:
            results = response['everywhereDestination']['results']
            if len(results) > params.maxResult:
                response['everywhereDestination']['results'] = results[:params.maxResult]
                if 'context' in response['everywhereDestination']:
                    response['everywhereDestination']['context']['totalResults'] = params.maxResult
        
        validated_data = SearchEverywhereData(**response)
        
        return self.prepare_response(validated_data, "FlightEverywhereResults")
        
    def search_roundtrip(self, params: SearchRoundtripParams) -> ApiResponse:
        processed_params = params.model_dump(exclude_none=True)
        
        response = self.client.search_roundtrip(processed_params)
        
        if 'data' in response and response['data'] is not None and 'itineraries' in response['data'] and response['data']['itineraries'] is not None:
            itineraries = response['data']['itineraries']
            if isinstance(itineraries, list) and len(itineraries) > params.maxResult:
                response['data']['itineraries'] = itineraries[:params.maxResult]
                if 'context' in response['data'] and response['data']['context'] is not None:
                    response['data']['context']['totalResults'] = params.maxResult
        
        validated_data = SearchRoundtripData(**response)
        
        return self.prepare_response(validated_data, "FlightRoundtripResults")
        
    def search_one_way(self, params: SearchOneWayParams) -> ApiResponse:
        processed_params = params.model_dump(exclude_none=True)
        
        response = self.client.search_one_way(processed_params)
        
        if 'data' in response and 'itineraries' in response['data']:
            itineraries = response['data']['itineraries']
            if len(itineraries) > params.maxResult:
                response['data']['itineraries'] = itineraries[:params.maxResult]
                if 'context' in response['data']:
                    response['data']['context']['totalResults'] = params.maxResult
        
        validated_data = SearchOneWayData(**response)
        
        return self.prepare_response(validated_data, "FlightOneWayResults")
        
    def get_flight_detail(self, params: FlightDetailParams) -> ApiResponse:
        processed_params = params.model_dump(exclude_none=True)
        
        response = self.client.get_flight_detail(processed_params)
        
        validated_data = FlightDetailData(**response)
        
        return self.prepare_response(validated_data, "FlightDetailResults")
        
    def get_price_calendar(self, params: PriceCalendarParams) -> ApiResponse:
        processed_params = params.model_dump(exclude_none=True)
        
        response = self.client.get_price_calendar(processed_params)
        
        validated_data = PriceCalendarData(**response)
        
        return self.prepare_response(validated_data, "PriceCalendarResults")

    def get_price_calendar_return(self, params: PriceCalendarReturnParams) -> ApiResponse:
        processed_params = params.model_dump(exclude_none=True)
        
        response = self.client.get_price_calendar_return(processed_params)
        
        validated_data = PriceCalendarData(**response)
        
        return self.prepare_response(validated_data, "PriceCalendarReturnResults")

    def get_cheapest_one_way(self, params: CheapestOneWayParams) -> ApiResponse:
        processed_params = params.model_dump(exclude_none=True)
        
        response = self.client.get_cheapest_one_way(processed_params)
        
        validated_data = CheapestOneWayData(**response)
        
        return self.prepare_response(validated_data, "CheapestOneWayResults")

    def search_hotels(self, params: HotelSearchParams) -> ApiResponse:
        processed_params = params.model_dump(exclude_none=True)
        
        # Remove maxResult from API call params but keep for limiting results
        max_results = processed_params.pop('maxResult', 5) if 'maxResult' in processed_params else 5
        
        response = self.client.search_hotels(processed_params)
        
        # Limit results if needed
        if 'data' in response and 'results' in response['data'] and 'hotelCards' in response['data']['results']:
            hotel_cards = response['data']['results']['hotelCards']
            if len(hotel_cards) > max_results:
                response['data']['results']['hotelCards'] = hotel_cards[:max_results]
                # Update searchSummary if present
                if 'searchSummary' in response['data']['results']:
                    if 'filteredTotal' in response['data']['results']['searchSummary']:
                        response['data']['results']['searchSummary']['filteredTotal'] = max_results
                    if 'resultsSummary' in response['data']['results']['searchSummary']:
                        response['data']['results']['searchSummary']['resultsSummary'] = f"{max_results} places to stay"
        
        validated_data = HotelSearchData(**response)
        
        return self.prepare_response(validated_data, "HotelSearchResults")

    def get_hotel_detail(self, params: HotelDetailParams) -> ApiResponse:
        processed_params = params.model_dump(exclude_none=True)
        
        response = self.client.get_hotel_detail(processed_params)
        
        validated_data = HotelDetailData(**response)
        
        return self.prepare_response(validated_data, "HotelDetailResults")

    def get_hotel_prices(self, params: HotelPricesParams) -> ApiResponse:
        processed_params = params.model_dump(exclude_none=True)
        
        response = self.client.get_hotel_prices(processed_params)
        
        validated_data = HotelPricesData(**response)
        
        return self.prepare_response(validated_data, "HotelPricesResults")

    def get_hotel_reviews(self, params: HotelReviewsParams) -> ApiResponse:
        processed_params = params.model_dump(exclude_none=True)
        
        response = self.client.get_hotel_reviews(processed_params)
        
        validated_data = HotelReviewsData(**response)
        
        return self.prepare_response(validated_data, "HotelReviewsResults")
