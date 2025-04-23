from typing import Dict, Any, List, Optional
import os
from .client import ZillowClient
from .schema import (
    PropertyParams,
    PropertySearchParams,
    ZestimateParams,
    ZestimateHistoryParams,
    PriceAndTaxHistoryParams,
    PropertyCompsParams,
    PropertyValueRangeParams,
    SimilarPropertiesParams,
    SimilarSalesParams,
    SimilarRentalsParams,
    MarketLocationParams,
    MarketDataParams,
    Property,
    PropertyList,
    PropertySearchResponse,
    PropertySearchResultList,
    PropertySearchResult,
    Zestimate,
    ZestimateHistoryPoint,
    ZestimateHistoryList,
    PriceAndTaxHistory,
    PriceAndTaxHistoryList,
    PropertyComps,
    PropertyCompsList,
    SimilarPropertyList,
    PropertyValueRange,
    PropertyValueRangeList,
    PropertyResponse,
    PropertiesResponse,
    PropertySearchResponseModel,
    ZestimateResponse,
    ZestimateHistoryResponse,
    PriceAndTaxHistoryResponse,
    PropertyCompsResponse,
    SimilarPropertyResponse,
    SimilarSalesResponse,
    SimilarRentalsResponse,
    PropertyValueRangeResponse,
    MarketLocation,
    MarketLocationList,
    MarketLocationResponse,
    MarketData,
    MarketDataResponse,
    ApiResponse
)
from ..common.component_handler import load_components, prepare_components_auto

class ZillowService:
    def __init__(self, client: ZillowClient):
        self.client = client
        self.components_data = self._load_components()

    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
        
    def prepare_response(self, data: Any, component_name: str = None) -> ApiResponse:
        tool_name = "zillow"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)

    def get_property(self, params: PropertyParams) -> ApiResponse:
        processed_params = self._process_property_params(params)
        response = self.client.get_property(processed_params)        
        # Fix listed_by.phone if it's a string instead of a Phone object
        if isinstance(response, dict) and 'listed_by' in response and isinstance(response['listed_by'], dict):
            if 'phone' in response['listed_by'] and isinstance(response['listed_by']['phone'], str):
                # Create an empty Phone object
                response['listed_by']['phone'] = {
                    'prefix': None,
                    'areacode': None,
                    'number': None
                }
                
        property_data = Property(**response)
        return self.prepare_response(property_data, "PropertyDetails")

    def search_properties(self, params: PropertySearchParams) -> ApiResponse:
        processed_params = self._process_search_params(params)
        response = self.client.search_properties(processed_params)

        # Case 1: Response is a list of properties
        if isinstance(response, list):
            # Convert list of properties to PropertySearchResult objects
            props = []
            for item in response:
                if isinstance(item, dict) and 'zpid' in item:
                    props.append(PropertySearchResult(
                        zpid=str(item.get('zpid')),
                        address=item.get('address')
                    ))
            
            search_response = PropertySearchResponse(
                props=props,
                resultsPerPage=len(props),
                totalPages=1,
                totalResultCount=len(props),
                currentPage=1
            )
        # Case 2: Simple zpid response
        elif isinstance(response, dict) and 'zpid' in response and len(response.keys()) <= 2:
            # Create a minimal response with the single property
            search_result = PropertySearchResult(zpid=str(response.get('zpid')))
            search_response = PropertySearchResponse(
                props=[search_result],
                resultsPerPage=1,
                totalPages=1,
                totalResultCount=1,
                currentPage=1
            )
        # Case 3: Response without props field
        elif isinstance(response, dict) and 'props' not in response:
            # Create an empty props list but keep other metadata
            search_response = PropertySearchResponse(
                props=[],
                resultsPerPage=response.get('resultsPerPage', 0),
                totalPages=response.get('totalPages', 0),
                totalResultCount=response.get('totalResultCount', 0),
                currentPage=response.get('currentPage', 1)
            )
        # Case 4: Normal response
        else:
            search_response = PropertySearchResponse(**response)
            
        search_result_list = PropertySearchResultList(results=search_response)
        return self.prepare_response(search_result_list, "PropertySearchResults")

    def get_zestimate(self, params: ZestimateParams) -> ApiResponse:
        processed_params = self._process_zestimate_params(params)
        response = self.client.get_zestimate(processed_params)
        zestimate_data = Zestimate(**response)
        return self.prepare_response(zestimate_data, "ZestimateCard")

    def get_zestimate_history(self, params: ZestimateHistoryParams) -> ApiResponse:
        processed_params = self._process_zestimate_history_params(params)
        response = self.client.get_zestimate_history(processed_params)
        # The response is a list of history points
        history_points = [ZestimateHistoryPoint(**point) for point in response]
        history_list = ZestimateHistoryList(history=history_points)
        return self.prepare_response(history_list, "ZestimateHistoryChart")

    def get_price_and_tax_history(self, params: PriceAndTaxHistoryParams) -> ApiResponse:
        processed_params = self._process_price_tax_history_params(params)
        response = self.client.get_price_and_tax_history(processed_params)
        price_tax_history = PriceAndTaxHistory(**response)
        price_tax_history_list = PriceAndTaxHistoryList(priceAndTaxHistory=price_tax_history)
        return self.prepare_response(price_tax_history_list, "PriceAndTaxHistoryChart")

    def get_property_comps(self, params: PropertyCompsParams) -> ApiResponse:
        processed_params = self._process_property_comps_params(params)
        response = self.client.get_property_comps(processed_params)
        property_comps = PropertyComps(**response)
        property_comps_list = PropertyCompsList(propertyComps=property_comps)
        return self.prepare_response(property_comps_list, "PropertyCompsGrid")
        
    def get_property_value_range(self, params: PropertyValueRangeParams) -> ApiResponse:
        processed_params = self._process_property_value_range_params(params)
        response = self.client.get_property_value_range(processed_params)
        value_range = PropertyValueRange(**response)
        value_range_list = PropertyValueRangeList(valueRange=value_range)
        return self.prepare_response(value_range_list, "PropertyValueRangeCard")

    def get_similar_properties(self, params: SimilarPropertiesParams) -> ApiResponse:
        processed_params = self._process_similar_properties_params(params)
        response = self.client.get_similar_properties(processed_params)
        # Ensure response is a list to match our schema
        property_list = response if isinstance(response, list) else []
        similar_properties = SimilarPropertyList(similarProperties=property_list)
        return self.prepare_response(similar_properties, "SimilarPropertiesGrid")
        
    def get_similar_sales(self, params: SimilarSalesParams) -> ApiResponse:
        processed_params = self._process_similar_sales_params(params)
        response = self.client.get_similar_sales(processed_params)
        # Ensure response is a list to match our schema
        sales_list = response if isinstance(response, list) else []
        similar_sales = SimilarPropertyList(similarProperties=sales_list)
        return self.prepare_response(similar_sales, "SimilarSalesGrid")
        
    def get_similar_rentals(self, params: SimilarRentalsParams) -> ApiResponse:
        processed_params = self._process_similar_rentals_params(params)
        response = self.client.get_similar_rentals(processed_params)
        # Ensure response is a list to match our schema
        rentals_list = response if isinstance(response, list) else []
        similar_rentals = SimilarPropertyList(similarProperties=rentals_list)
        return self.prepare_response(similar_rentals, "SimilarRentalsGrid")

    def get_market_location(self, params: MarketLocationParams) -> ApiResponse:
        processed_params = self._process_market_location_params(params)
        response = self.client.get_market_location(processed_params)
        
        # Process the response which comes in the data array
        locations = []
        if isinstance(response, dict) and 'data' in response and isinstance(response['data'], list):
            for location in response['data']:
                locations.append(MarketLocation(**location))
        
        market_locations = MarketLocationList(marketLocations=locations)
        return self.prepare_response(market_locations, "MarketLocationList")

    def get_market_data(self, params: MarketDataParams) -> ApiResponse:
        processed_params = self._process_market_data_params(params)
        response = self.client.get_market_data(processed_params)
        
        # Create market data object
        market_data = MarketData(**response)
        return self.prepare_response(market_data, "MarketDataChart")

    def _process_property_params(self, params: PropertyParams) -> Dict[str, Any]:
        return params.model_dump(exclude_none=True)

    def _process_search_params(self, params: PropertySearchParams) -> Dict[str, Any]:
        return params.model_dump(exclude_none=True)

    def _process_zestimate_params(self, params: ZestimateParams) -> Dict[str, Any]:
        return params.model_dump(exclude_none=True)

    def _process_zestimate_history_params(self, params: ZestimateHistoryParams) -> Dict[str, Any]:
        return params.model_dump(exclude_none=True)
        
    def _process_price_tax_history_params(self, params: PriceAndTaxHistoryParams) -> Dict[str, Any]:
        return params.model_dump(exclude_none=True)
        
    def _process_property_comps_params(self, params: PropertyCompsParams) -> Dict[str, Any]:
        return params.model_dump(exclude_none=True)
        
    def _process_property_value_range_params(self, params: PropertyValueRangeParams) -> Dict[str, Any]:
        return params.model_dump(exclude_none=True)
        
    def _process_similar_properties_params(self, params: SimilarPropertiesParams) -> Dict[str, Any]:
        return params.model_dump(exclude_none=True)
        
    def _process_similar_sales_params(self, params: SimilarSalesParams) -> Dict[str, Any]:
        return params.model_dump(exclude_none=True)
        
    def _process_similar_rentals_params(self, params: SimilarRentalsParams) -> Dict[str, Any]:
        return params.model_dump(exclude_none=True)

    def _process_market_location_params(self, params: MarketLocationParams) -> Dict[str, Any]:
        return params.model_dump(exclude_none=True)

    def _process_market_data_params(self, params: MarketDataParams) -> Dict[str, Any]:
        return params.model_dump(exclude_none=True)
