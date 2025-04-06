from fastapi import APIRouter, Body, Depends, HTTPException
from starlette.requests import Request as FastAPIRequest
from typing import Dict, Any

from .schema import (
    GeocodeParams,
    ReverseGeocodeParams,
    SearchPlacesParams,
    PlaceDetailsParams,
    DistanceMatrixParams,
    ElevationParams,
    DirectionsParams,
    GeocodeResponse,
    ReverseGeocodeResponse,
    SearchPlacesResponse,
    PlaceDetailsResponse,
    DistanceMatrixResponse,
    ElevationResponse,
    DirectionsResponse,
    ApiResponse
)
from .service import GoogleMapsService
from .client import GoogleMapsClient
from ..common.auth import validate_provider_api_key
from ..common.input_schema_decorator import schema
from ..common.utils import apply_error_handler_to_service, apply_error_handler_to_router, apply_error_handler_to_client
from ..common.examples_handler import ExamplesLoader

router = APIRouter(prefix="/google-maps", tags=["google-maps"])
examples = ExamplesLoader()

async def get_google_maps_service(request: FastAPIRequest):
    try:
        api_key = await validate_provider_api_key(request, "google-maps")
        client = GoogleMapsClient(api_key)
        apply_error_handler_to_client(client)
        service = GoogleMapsService(client)
        
        apply_error_handler_to_service(service)
        
        return service
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Failed to initialize Google Maps service: {str(e)}"
        )

@router.post("/get_geocode", response_model=ApiResponse)
@schema(
    input_schema_class=GeocodeParams,
    output_schema_class=GeocodeResponse,
    examples=examples["/google-maps/get_geocode"]
)
async def geocode(
    params: Dict[str, Any] = Body(...),
    service: GoogleMapsService = Depends(get_google_maps_service)
):
    validated_params = GeocodeParams(**params)
    return service.geocode(validated_params)

@router.post("/get_reverse_geocode", response_model=ApiResponse)
@schema(
    input_schema_class=ReverseGeocodeParams,
    output_schema_class=ReverseGeocodeResponse,
    examples=examples["/google-maps/get_reverse_geocode"]
)
async def reverse_geocode(
    params: Dict[str, Any] = Body(...),
    service: GoogleMapsService = Depends(get_google_maps_service)
):
    validated_params = ReverseGeocodeParams(**params)
    return service.reverse_geocode(validated_params)

@router.post("/search_places", response_model=ApiResponse)
@schema(
    input_schema_class=SearchPlacesParams,
    output_schema_class=SearchPlacesResponse,
    examples=examples["/google-maps/search_places"]
)
async def search_places(
    params: Dict[str, Any] = Body(...),
    service: GoogleMapsService = Depends(get_google_maps_service)
):
    validated_params = SearchPlacesParams(**params)
    return service.search_places(validated_params)

@router.post("/get_place_details", response_model=ApiResponse)
@schema(
    input_schema_class=PlaceDetailsParams,
    output_schema_class=PlaceDetailsResponse,
    examples=examples["/google-maps/get_place_details"]
)
async def place_details(
    params: Dict[str, Any] = Body(...),
    service: GoogleMapsService = Depends(get_google_maps_service)
):
    validated_params = PlaceDetailsParams(**params)
    return service.place_details(validated_params)

@router.post("/calculate_distance_matrix", response_model=ApiResponse)
@schema(
    input_schema_class=DistanceMatrixParams,
    output_schema_class=DistanceMatrixResponse,
    examples=examples["/google-maps/calculate_distance_matrix"]
)
async def distance_matrix(
    params: Dict[str, Any] = Body(...),
    service: GoogleMapsService = Depends(get_google_maps_service)
):
    validated_params = DistanceMatrixParams(**params)
    return service.distance_matrix(validated_params)

@router.post("/get_elevation", response_model=ApiResponse)
@schema(
    input_schema_class=ElevationParams,
    output_schema_class=ElevationResponse,
    examples=examples["/google-maps/get_elevation"]
)
async def elevation(
    params: Dict[str, Any] = Body(...),
    service: GoogleMapsService = Depends(get_google_maps_service)
):
    validated_params = ElevationParams(**params)
    return service.elevation(validated_params)

@router.post("/get_directions", response_model=ApiResponse)
@schema(
    input_schema_class=DirectionsParams,
    output_schema_class=DirectionsResponse,
    examples=examples["/google-maps/get_directions"]
)
async def directions(
    params: Dict[str, Any] = Body(...),
    service: GoogleMapsService = Depends(get_google_maps_service)
):
    validated_params = DirectionsParams(**params)
    return service.directions(validated_params)


@router.post("/validate_key")
async def validate_key(
    params: Dict[str, Any] = Body(...),
):
    try:
        api_key = params.get("api_key")
        if not api_key:
            return {"valid": False, "message": "API key is required"}
        
        client = GoogleMapsClient(api_key)
        test_response = client.geocode("1600 Amphitheatre Parkway, Mountain View, CA")
        
        if test_response["status"] == "OK":
            return {"valid": True, "message": "API key is valid"}
        else:
            return {"valid": False, "message": f"API key validation failed: {test_response['status']}"}
    except Exception as e:
        return {"valid": False, "message": f"Invalid API key: {str(e)}"}

apply_error_handler_to_router(router)
