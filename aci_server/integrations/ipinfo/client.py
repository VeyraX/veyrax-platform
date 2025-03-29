import requests
from typing import Dict, Any, Optional

class IpInfoClient:
    BASE_URL = "https://ipinfo.io"
    
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.headers = {
            "content-type": "application/json"
        }

    def get_ip_info(self, ip_address: Optional[str] = None) -> Dict[str, Any]:
        """Get information about an IP address"""
        endpoint = f"{self.BASE_URL}/{ip_address}" if ip_address else self.BASE_URL
        params = {"token": self.api_token}
        
        response = requests.get(
            endpoint,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()

    def get_bulk_info(self, ip_addresses: list[str]) -> Dict[str, Any]:
        """Get information about multiple IP addresses"""
        endpoint = f"{self.BASE_URL}/batch"
        params = {"token": self.api_token}
        data = ip_addresses
        
        response = requests.post(
            endpoint,
            headers=self.headers,
            params=params,
            json=data
        )
        response.raise_for_status()
        return response.json()

    def get_asn_info(self, asn: str) -> Dict[str, Any]:
        """Get information about an ASN (Autonomous System Number)"""
        endpoint = f"{self.BASE_URL}/{asn}"
        params = {"token": self.api_token}
        
        response = requests.get(
            endpoint,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json() 