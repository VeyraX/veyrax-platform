from typing import Dict, Any, List, Optional, Tuple, Union
import os
from .client import GoogleMapsClient
from .schema import (
    GeocodeParams,
    ReverseGeocodeParams,
    SearchPlacesParams,
    PlaceDetailsParams,
    DistanceMatrixParams,
    ElevationParams,
    DirectionsParams,
    GeocodeResult,
    ReverseGeocodeResult,
    PlaceList,
    PlaceDetail,
    DistanceMatrixResult,
    ElevationList,
    DirectionsList,
    Location,
    Place,
    DistanceMatrixResultRow,
    DistanceMatrixElement,
    DirectionRoute,
    DirectionStep,
    ElevationPoint,
    ApiResponse,
)
from ..common.component_handler import load_components, prepare_components_auto


class GoogleMapsService:
    def __init__(self, client: GoogleMapsClient):
        self.client = client
        self.components_data = self._load_components()
    
    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
    
    def prepare_response(self, data: Any, component_name: str = None) -> ApiResponse:
        tool_name = "google-maps"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)
    
    def geocode(self, params: GeocodeParams) -> ApiResponse:
        response = self.client.geocode(params.address)
        
        if response["status"] != "OK" or not response["results"]:
            raise ValueError(f"Geocoding failed: {response.get('error_message', response['status'])}")
        
        result = response["results"][0]
        geocode_result = GeocodeResult(
            location=Location(
                lat=result["geometry"]["location"]["lat"],
                lng=result["geometry"]["location"]["lng"]
            ),
            formatted_address=result["formatted_address"],
            place_id=result["place_id"]
        )
        
        return self.prepare_response(geocode_result, "GeocodeResult")
    
    def reverse_geocode(self, params: ReverseGeocodeParams) -> ApiResponse:
        response = self.client.reverse_geocode(params.latitude, params.longitude)
        
        if response["status"] != "OK" or not response["results"]:
            raise ValueError(f"Reverse geocoding failed: {response.get('error_message', response['status'])}")
        
        result = response["results"][0]
        reverse_geocode_result = ReverseGeocodeResult(
            formatted_address=result["formatted_address"],
            place_id=result["place_id"],
            address_components=[
                {
                    "long_name": component["long_name"],
                    "short_name": component["short_name"],
                    "types": component["types"]
                }
                for component in result["address_components"]
            ]
        )
        
        return self.prepare_response(reverse_geocode_result, "ReverseGeocodeResult")
    
    def search_places(self, params: SearchPlacesParams) -> ApiResponse:
        location = None
        if params.location:
            location = (params.location.latitude, params.location.longitude)
        
        response = self.client.search_places(params.query, location, params.radius)
        
        if response["status"] != "OK":
            raise ValueError(f"Place search failed: {response.get('error_message', response['status'])}")
        
        places = [
            Place(
                name=place["name"],
                formatted_address=place["formatted_address"],
                location=Location(
                    lat=place["geometry"]["location"]["lat"],
                    lng=place["geometry"]["location"]["lng"]
                ),
                place_id=place["place_id"],
                rating=place.get("rating"),
                types=place.get("types")
            )
            for place in response["results"]
        ]
        
        place_list = PlaceList(places=places)
        return self.prepare_response(place_list, "PlaceList")
    
    def place_details(self, params: PlaceDetailsParams) -> ApiResponse:
        response = self.client.place_details(params.place_id)
        
        if response["status"] != "OK":
            raise ValueError(f"Place details request failed: {response.get('error_message', response['status'])}")
        
        result = response["result"]
        
        reviews = None
        if "reviews" in result:
            reviews = [
                {
                    "author_name": review["author_name"],
                    "rating": review["rating"],
                    "text": review["text"],
                    "time": review["time"]
                }
                for review in result["reviews"]
            ]
        
        opening_hours = None
        if "opening_hours" in result:
            opening_hours = {
                "weekday_text": result["opening_hours"].get("weekday_text"),
                "open_now": result["opening_hours"].get("open_now")
            }
        
        place_detail = PlaceDetail(
            name=result["name"],
            formatted_address=result["formatted_address"],
            location=Location(
                lat=result["geometry"]["location"]["lat"],
                lng=result["geometry"]["location"]["lng"]
            ),
            formatted_phone_number=result.get("formatted_phone_number"),
            website=result.get("website"),
            rating=result.get("rating"),
            reviews=reviews,
            opening_hours=opening_hours
        )
        
        return self.prepare_response(place_detail, "PlaceDetail")
    
    def distance_matrix(self, params: DistanceMatrixParams) -> ApiResponse:
        response = self.client.distance_matrix(params.origins, params.destinations, params.mode)
        
        if response["status"] != "OK":
            raise ValueError(f"Distance matrix request failed: {response.get('error_message', response['status'])}")
        
        result_rows = []
        for row in response["rows"]:
            elements = []
            for element in row["elements"]:
                element_dict = {"status": element["status"]}
                
                if element["status"] == "OK":
                    element_dict["duration"] = {
                        "text": element["duration"]["text"],
                        "value": element["duration"]["value"]
                    }
                    element_dict["distance"] = {
                        "text": element["distance"]["text"],
                        "value": element["distance"]["value"]
                    }
                
                elements.append(DistanceMatrixElement(**element_dict))
            
            result_rows.append(DistanceMatrixResultRow(elements=elements))
        
        matrix_result = DistanceMatrixResult(
            origin_addresses=response["origin_addresses"],
            destination_addresses=response["destination_addresses"],
            results=result_rows
        )
        
        return self.prepare_response(matrix_result, "DistanceMatrixResult")
    
    def elevation(self, params: ElevationParams) -> ApiResponse:
        locations = [(loc.latitude, loc.longitude) for loc in params.locations]
        response = self.client.elevation(locations)
        
        if response["status"] != "OK":
            raise ValueError(f"Elevation request failed: {response.get('error_message', response['status'])}")
        
        elevation_points = [
            ElevationPoint(
                elevation=result["elevation"],
                location=Location(
                    lat=result["location"]["lat"],
                    lng=result["location"]["lng"]
                ),
                resolution=result["resolution"]
            )
            for result in response["results"]
        ]
        
        elevation_list = ElevationList(results=elevation_points)
        return self.prepare_response(elevation_list, "ElevationList")
    
    def directions(self, params: DirectionsParams) -> ApiResponse:
        response = self.client.directions(params.origin, params.destination, params.mode)
        
        if response["status"] != "OK":
            raise ValueError(f"Directions request failed: {response.get('error_message', response['status'])}")
        
        routes = []
        for route in response["routes"]:
            leg = route["legs"][0]
            
            steps = [
                DirectionStep(
                    instructions=step["html_instructions"],
                    distance={
                        "text": step["distance"]["text"],
                        "value": step["distance"]["value"]
                    },
                    duration={
                        "text": step["duration"]["text"],
                        "value": step["duration"]["value"]
                    },
                    travel_mode=step["travel_mode"]
                )
                for step in leg["steps"]
            ]
            
            routes.append(DirectionRoute(
                summary=route["summary"],
                distance={
                    "text": leg["distance"]["text"],
                    "value": leg["distance"]["value"]
                },
                duration={
                    "text": leg["duration"]["text"],
                    "value": leg["duration"]["value"]
                },
                steps=steps
            ))
        
        directions_list = DirectionsList(routes=routes)
        return self.prepare_response(directions_list, "DirectionsList")
