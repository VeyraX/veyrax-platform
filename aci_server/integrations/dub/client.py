import requests
from typing import Dict, Any, List, Optional

class DubClient:
    BASE_URL = "https://api.dub.co"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

    def create_link(self, params: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.post(
            f"{self.BASE_URL}/links",
            headers=self.headers,
            json=params
        )
        response.raise_for_status()
        return response.json()

    def update_link(self, link_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.patch(
            f"{self.BASE_URL}/links/{link_id}",
            headers=self.headers,
            json=params
        )
        response.raise_for_status()
        return response.json()

    def upsert_link(self, params: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.put(
            f"{self.BASE_URL}/links/upsert",
            headers=self.headers,
            json=params
        )
        response.raise_for_status()
        return response.json()

    def delete_link(self, link_id: str) -> Dict[str, Any]:
        response = requests.delete(
            f"{self.BASE_URL}/links/{link_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def get_link_info(self, link_id: str = None) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/links/info"
        if link_id:
            url = f"{self.BASE_URL}/links/{link_id}"
        
        response = requests.get(
            url,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def get_links(self) -> List[Dict[str, Any]]:
        response = requests.get(
            f"{self.BASE_URL}/links",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def get_links_count(self) -> Dict[str, int]:
        response = requests.get(
            f"{self.BASE_URL}/links/count",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def bulk_create_links(self, links: List[Dict[str, Any]]) -> Dict[str, Any]:
        response = requests.post(
            f"{self.BASE_URL}/links/bulk",
            headers=self.headers,
            json=links
        )
        response.raise_for_status()
        return response.json()

    def bulk_update_links(self, links: List[Dict[str, Any]]) -> Dict[str, Any]:
        response = requests.patch(
            f"{self.BASE_URL}/links/bulk",
            headers=self.headers,
            json=links
        )
        response.raise_for_status()
        return response.json()

    def bulk_delete_links(self, link_ids: List[str]) -> Dict[str, int]:
        response = requests.delete(
            f"{self.BASE_URL}/links/bulk?linkIds={','.join(link_ids)}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def get_qr_code(self, link_id: str = None) -> str:
        url = f"{self.BASE_URL}/qr"
        if link_id:
            url = f"{url}?linkId={link_id}"
        
        response = requests.get(
            url,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def get_analytics(self) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/analytics",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def get_events(self) -> List[Dict[str, Any]]:
        response = requests.get(
            f"{self.BASE_URL}/events",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    # Customer management endpoints
    def get_customer(self, customer_id: str) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/customers/{customer_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_customers(self) -> List[Dict[str, Any]]:
        response = requests.get(
            f"{self.BASE_URL}/customers",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def update_customer(self, customer_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.patch(
            f"{self.BASE_URL}/customers/{customer_id}",
            headers=self.headers,
            json=params
        )
        response.raise_for_status()
        return response.json()
    
    def delete_customer(self, customer_id: str) -> Dict[str, Any]:
        response = requests.delete(
            f"{self.BASE_URL}/customers/{customer_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    # Tracking endpoints
    def track_lead(self, params: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.post(
            f"{self.BASE_URL}/track/lead",
            headers=self.headers,
            json=params
        )
        response.raise_for_status()
        return response.json()
    
    def track_sale(self, params: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.post(
            f"{self.BASE_URL}/track/sale",
            headers=self.headers,
            json=params
        )
        response.raise_for_status()
        return response.json()
    
    # Tags management endpoints
    def create_tag(self, params: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.post(
            f"{self.BASE_URL}/tags",
            headers=self.headers,
            json=params
        )
        response.raise_for_status()
        return response.json()
    
    def get_tags(self) -> List[Dict[str, Any]]:
        response = requests.get(
            f"{self.BASE_URL}/tags",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def update_tag(self, tag_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.patch(
            f"{self.BASE_URL}/tags/{tag_id}",
            headers=self.headers,
            json=params
        )
        response.raise_for_status()
        return response.json()

    # Domain management endpoints
    def create_domain(self, params: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.post(
            f"{self.BASE_URL}/domains",
            headers=self.headers,
            json=params
        )
        response.raise_for_status()
        return response.json()
    
    def update_domain(self, slug: str, params: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.patch(
            f"{self.BASE_URL}/domains/{slug}",
            headers=self.headers,
            json=params
        )
        response.raise_for_status()
        return response.json()
    
    def delete_domain(self, slug: str) -> Dict[str, Any]:
        response = requests.delete(
            f"{self.BASE_URL}/domains/{slug}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_domains(self) -> List[Dict[str, Any]]:
        response = requests.get(
            f"{self.BASE_URL}/domains",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    # Workspace management endpoints
    def get_workspace(self, id_or_slug: str) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/workspaces/{id_or_slug}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def update_workspace(self, id_or_slug: str, params: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.patch(
            f"{self.BASE_URL}/workspaces/{id_or_slug}",
            headers=self.headers,
            json=params
        )
        response.raise_for_status()
        return response.json()
