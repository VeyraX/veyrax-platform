from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union

class IpInfoParams(BaseModel):
    ip_address: Optional[str] = Field(
        None, 
        description="IP address to lookup (if not provided, uses the caller's IP)"
    )

class BulkIpInfoParams(BaseModel):
    ip_addresses: List[str] = Field(
        ...,
        description="List of IP addresses to lookup (max 1000 for paid plans)"
    )

class AsnInfoParams(BaseModel):
    asn: str = Field(
        ...,
        description="ASN to lookup, format: AS1234"
    )

class GeoLocation(BaseModel):
    latitude: float
    longitude: float

class IpInfoResponse(BaseModel):
    ip: str
    hostname: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    loc: Optional[str] = None
    org: Optional[str] = None
    postal: Optional[str] = None
    timezone: Optional[str] = None
    asn: Optional[Dict[str, Any]] = None
    company: Optional[Dict[str, Any]] = None
    carrier: Optional[Dict[str, Any]] = None
    privacy: Optional[Dict[str, Any]] = None
    abuse: Optional[Dict[str, Any]] = None
    domains: Optional[Dict[str, Any]] = None

class BulkIpInfoResponse(BaseModel):
    items: Dict[str, IpInfoResponse]

class AsnInfoResponse(BaseModel):
    asn: str
    name: Optional[str] = None
    country: Optional[str] = None
    domain: Optional[str] = None
    routes: Optional[int] = None
    type: Optional[str] = None
    prefixes: Optional[List[Dict[str, Any]]] = None

class ApiResponse(BaseModel):
    data: Union[IpInfoResponse, BulkIpInfoResponse, AsnInfoResponse]
    component: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None

# Response schema classes
class IpInfoResponseSchema(BaseModel):
    data: IpInfoResponse
    message: Optional[str] = None

class BulkIpInfoResponseSchema(BaseModel):
    data: BulkIpInfoResponse
    message: Optional[str] = None

class AsnInfoResponseSchema(BaseModel):
    data: AsnInfoResponse
    message: Optional[str] = None 