from typing import Dict, Any, Optional, List
import logging
import os
from .client import AirbnbClient
from .schema import (
    AirbnbSearchParams,
    AirbnbListingDetailsParams,
    AirbnbListing,
    AirbnbListingDetail,
    AirbnbSearchData,
    AirbnbListingDetailsData,
    ApiResponse
)
from ..common.component_handler import load_components, prepare_components_auto

logger = logging.getLogger(__name__)

class AirbnbService:
    """Service for interacting with Airbnb"""
    
    def __init__(self, client: AirbnbClient = None):
        self.client = client or AirbnbClient()
        self.components_data = self._load_components()
    
    def _load_components(self):
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            return load_components(current_dir)
        except Exception as e:
            logger.warning(f"Failed to load components: {str(e)}")
            return {}
    
    def prepare_response(self, data: Any, component_name: str = None) -> ApiResponse:
        tool_name = "airbnb"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)
    
    def _clean_object(self, obj: Any) -> None:
        """Remove __typename and null/empty values from objects"""
        if isinstance(obj, dict):
            keys_to_delete = []
            for key, value in obj.items():
                if not value or key == "__typename":
                    keys_to_delete.append(key)
                elif isinstance(value, (dict, list)):
                    self._clean_object(value)
            
            for key in keys_to_delete:
                del obj[key]
        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, (dict, list)):
                    self._clean_object(item)
    
    def _pick_by_schema(self, obj: Any, schema: Dict[str, Any]) -> Any:
        """Extract data from an object based on a schema"""
        if not isinstance(obj, dict) or obj is None:
            return obj
        
        # If the object is an array, process each item
        if isinstance(obj, list):
            return [self._pick_by_schema(item, schema) for item in obj]
        
        result = {}
        for key, rule in schema.items():
            if key in obj:
                # If the rule is True, copy the value as-is
                if rule is True:
                    result[key] = obj[key]
                # If the rule is an object, apply the schema recursively
                elif isinstance(rule, dict):
                    result[key] = self._pick_by_schema(obj[key], rule)
        
        return result
    
    def _flatten_arrays_in_object(self, input_obj: Any, in_array: bool = False) -> Any:
        """Flatten arrays in an object to strings"""
        if isinstance(input_obj, list):
            # Process each item in the array with in_array=True
            flat_items = [self._flatten_arrays_in_object(item, True) for item in input_obj]
            return ", ".join(str(item) for item in flat_items if item is not None)
        elif isinstance(input_obj, dict):
            if in_array:
                # When inside an array, ignore the keys and flatten the object's values
                values = [self._flatten_arrays_in_object(value, True) for value in input_obj.values()]
                return ": ".join(str(value) for value in values if value is not None)
            else:
                # When not in an array, process each property recursively
                result = {}
                for key, value in input_obj.items():
                    result[key] = self._flatten_arrays_in_object(value, False)
                return result
        else:
            # For primitives, simply return the value
            return input_obj
    
    def _process_search_results(self, raw_result: Dict[str, Any]) -> AirbnbSearchData:
        """Process raw search results into AirbnbSearchData"""
        search_url = raw_result.get("search_url", "")
        raw_data = raw_result.get("raw_data")
        
        listings = []
        pagination_info = None
        
        if raw_data:
            try:
                results = raw_data["data"]["presentation"]["staysSearch"]["results"]
                
                # Clean the results object
                self._clean_object(results)
                
                # Schema for filtering search results
                allow_search_result_schema = {
                    "listing": {
                        "id": True,
                        "name": True,
                        "title": True,
                        "coordinate": True,
                        "structuredContent": {
                            "mapCategoryInfo": {
                                "body": True
                            },
                            "mapSecondaryLine": {
                                "body": True
                            },
                            "primaryLine": {
                                "body": True
                            },
                            "secondaryLine": {
                                "body": True
                            },
                        }
                    },
                    "avgRatingA11yLabel": True,
                    "listingParamOverrides": True,
                    "structuredDisplayPrice": {
                        "primaryLine": {
                            "accessibilityLabel": True,
                        },
                        "secondaryLine": {
                            "accessibilityLabel": True,
                        },
                        "explanationData": {
                            "title": True,
                            "priceDetails": {
                                "items": {
                                    "description": True,
                                    "priceString": True
                                }
                            }
                        }
                    }
                }
                
                # Extract search results
                search_results = results["searchResults"]
                pagination_info = results["paginationInfo"]
                
                for result in search_results:
                    # Apply schema and flatten arrays
                    filtered_result = self._pick_by_schema(result, allow_search_result_schema)
                    
                    # Get listing data
                    listing_data = filtered_result.get("listing", {})
                    listing_id = listing_data.get("id", "")
                    
                    # Create structured Airbnb listing
                    airbnb_listing = AirbnbListing(
                        id=listing_id,
                        name=listing_data.get("name", ""),
                        title=listing_data.get("title", ""),
                        url=f"{self.client.BASE_URL}/rooms/{listing_id}",
                        coordinate=listing_data.get("coordinate"),
                        structured_content=listing_data.get("structuredContent"),
                        avg_rating=filtered_result.get("avgRatingA11yLabel"),
                        price_info=filtered_result.get("structuredDisplayPrice")
                    )
                    
                    listings.append(airbnb_listing)
            except Exception as e:
                logger.error(f"Error processing search results: {str(e)}")
        
        # Create and return the search data
        return AirbnbSearchData(
            search_url=search_url,
            listings=listings,
            pagination_info=pagination_info
        )
    
    def _process_listing_details(self, raw_result: Dict[str, Any]) -> AirbnbListingDetailsData:
        """Process raw listing details into AirbnbListingDetailsData"""
        listing_url = raw_result.get("listing_url", "")
        raw_data = raw_result.get("raw_data")
        
        details = []
        
        if raw_data:
            try:
                sections = raw_data["data"]["presentation"]["stayProductDetailPage"]["sections"]["sections"]
                
                # Schema for filtering listing details
                allow_section_schema = {
                    "LOCATION_DEFAULT": {
                        "lat": True,
                        "lng": True,
                        "subtitle": True,
                        "title": True
                    },
                    "POLICIES_DEFAULT": {
                        "title": True,
                        "houseRulesSections": {
                            "title": True,
                            "items": {
                                "title": True
                            }
                        }
                    },
                    "HIGHLIGHTS_DEFAULT": {
                        "highlights": {
                            "title": True
                        }
                    },
                    "DESCRIPTION_DEFAULT": {
                        "htmlDescription": {
                            "htmlText": True
                        }
                    },
                    "AMENITIES_DEFAULT": {
                        "title": True,
                        "seeAllAmenitiesGroups": {
                            "title": True,
                            "amenities": {
                                "title": True
                            }
                        }
                    }
                }
                
                # Process each section
                for section in sections:
                    self._clean_object(section)
                    
                    section_id = section.get("sectionId", "")
                    
                    if section_id in allow_section_schema:
                        # Filter section data based on schema
                        filtered_content = self._pick_by_schema(
                            section.get("section", {}), 
                            allow_section_schema[section_id]
                        )
                        
                        # Create structured listing detail
                        listing_detail = AirbnbListingDetail(
                            id=section_id,
                            type=section_id.replace("_DEFAULT", "").lower(),
                            content=filtered_content
                        )
                        
                        details.append(listing_detail)
            except Exception as e:
                logger.error(f"Error processing listing details: {str(e)}")
        
        # Create and return the listing details data
        return AirbnbListingDetailsData(
            listing_url=listing_url,
            details=details
        )
    
    async def search(self, params: AirbnbSearchParams) -> ApiResponse:
        """
        Search for Airbnb listings with various filters
        """
        try:
            # Get raw search results from client
            raw_result = self.client.search(
                location=params.location,
                place_id=params.place_id,
                checkin=params.checkin,
                checkout=params.checkout,
                adults=params.adults,
                children=params.children,
                infants=params.infants,
                pets=params.pets,
                min_price=params.min_price,
                max_price=params.max_price,
                cursor=params.cursor
            )
            
            # Process and transform the data
            search_data = self._process_search_results(raw_result)
            
            # Return data with component info
            return self.prepare_response(search_data, "AirbnbSearchResults")
            
        except Exception as e:
            logger.error(f"Error searching Airbnb: {str(e)}")
            raise
    
    async def get_listing_details(self, params: AirbnbListingDetailsParams) -> ApiResponse:
        """
        Get detailed information about a specific Airbnb listing
        """
        try:
            # Get raw listing details from client
            raw_result = self.client.get_listing_details(
                id=params.id,
                checkin=params.checkin,
                checkout=params.checkout,
                adults=params.adults,
                children=params.children,
                infants=params.infants,
                pets=params.pets
            )
            
            # Process and transform the data
            listing_data = self._process_listing_details(raw_result)
            
            # Return data with component info
            return self.prepare_response(listing_data, "AirbnbListingDetails")
            
        except Exception as e:
            logger.error(f"Error getting Airbnb listing details: {str(e)}")
            raise
