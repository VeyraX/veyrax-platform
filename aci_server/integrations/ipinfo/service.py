from typing import Dict, Any, Union, List, Optional
from .client import IpInfoClient
from .schema import (
    IpInfoParams, 
    BulkIpInfoParams, 
    AsnInfoParams,
    IpInfoResponse, 
    BulkIpInfoResponse, 
    AsnInfoResponse, 
    ApiResponse
)
import os
from ..common.component_handler import load_components, prepare_components_auto

class IpInfoService:
    def __init__(self, client: IpInfoClient):
        self.client = client
        self.components_data = self._load_components()
        
    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
        
    def prepare_response(self, data: Union[IpInfoResponse, BulkIpInfoResponse, AsnInfoResponse], component_name: str = None) -> ApiResponse:
        tool_name = "ipinfo"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)

    def get_ip_info(self, params: IpInfoParams) -> ApiResponse:
        response = self.client.get_ip_info(params.ip_address)
        ip_info = IpInfoResponse(**response)
        return self.prepare_response(ip_info, "IpInfoView")

    def get_bulk_info(self, params: BulkIpInfoParams) -> ApiResponse:
        response = self.client.get_bulk_info(params.ip_addresses)
        bulk_info = BulkIpInfoResponse(items=response)
        return self.prepare_response(bulk_info, "IpInfoBulkView")

    def get_asn_info(self, params: AsnInfoParams) -> ApiResponse:
        response = self.client.get_asn_info(params.asn)
        asn_info = AsnInfoResponse(**response)
        return self.prepare_response(asn_info, "IpInfoAsnView") 