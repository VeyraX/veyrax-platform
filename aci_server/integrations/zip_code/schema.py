from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union

class Place(BaseModel):
    place_name: str = Field(..., alias="place name")
    longitude: str
    state: str
    state_abbreviation: str = Field(..., alias="state abbreviation")
    latitude: str

class ZipCodeResponse(BaseModel):
    post_code: str = Field(..., alias="post code")
    country: str
    country_abbreviation: str = Field(..., alias="country abbreviation")
    places: List[Place]

class ZipCodeRequest(BaseModel):
    country: str = Field(..., description="Country code (e.g., 'US', 'CA', 'GB')")
    postal_code: str = Field(..., description="Postal code to lookup")

class CityRequest(BaseModel):
    country: str = Field(..., description="Country code (e.g., 'US', 'CA', 'GB')")
    state: str = Field(..., description="State code or abbreviation")
    city: str = Field(..., description="City name to lookup")

class ApiResponse(BaseModel):
    data: ZipCodeResponse
    component: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None

class ZipCodeResponseSchema(BaseModel):
    data: ZipCodeResponse
    message: Optional[str] = None 