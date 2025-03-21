import requests
from typing import Dict, Any, List, Optional, Union

class AirtableClient:
    BASE_URL = "https://api.airtable.com/v0"
    CONTENT_URL = "https://content.airtable.com/v0"
    META_URL = "https://api.airtable.com/v0/meta"
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }

    def list_records(self, base_id: str, table_id_or_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/{base_id}/{table_id_or_name}"
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_record(self, base_id: str, table_id_or_name: str, record_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/{base_id}/{table_id_or_name}/{record_id}"
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def create_records(self, base_id: str, table_id_or_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/{base_id}/{table_id_or_name}"
        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()
    
    def update_records(self, base_id: str, table_id_or_name: str, data: Dict[str, Any], is_patch: bool = True) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/{base_id}/{table_id_or_name}"
        method = requests.patch if is_patch else requests.put
        response = method(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()
    
    def update_record(self, base_id: str, table_id_or_name: str, record_id: str, data: Dict[str, Any], is_patch: bool = True) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/{base_id}/{table_id_or_name}/{record_id}"
        method = requests.patch if is_patch else requests.put
        response = method(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()
    
    def delete_records(self, base_id: str, table_id_or_name: str, record_ids: List[str]) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/{base_id}/{table_id_or_name}"
        params = {"records[]": record_ids}
        response = requests.delete(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def delete_record(self, base_id: str, table_id_or_name: str, record_id: str) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/{base_id}/{table_id_or_name}/{record_id}"
        response = requests.delete(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def upload_attachment(self, base_id: str, record_id: str, attachment_field: str, file_data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.CONTENT_URL}/{base_id}/{record_id}/{attachment_field}/uploadAttachment"
        response = requests.post(url, headers=self.headers, json=file_data)
        response.raise_for_status()
        return response.json()
    
    def sync_csv(self, base_id: str, table_id_or_name: str, api_endpoint_sync_id: str, csv_data: str) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/{base_id}/{table_id_or_name}/sync/{api_endpoint_sync_id}"
        headers = {**self.headers, "Content-Type": "text/csv"}
        response = requests.post(url, headers=headers, data=csv_data)
        response.raise_for_status()
        return response.json()
        
    # New methods for field management
    def create_field(self, base_id: str, table_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.META_URL}/bases/{base_id}/tables/{table_id}/fields"
        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()
        
    def update_field(self, base_id: str, table_id: str, column_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.META_URL}/bases/{base_id}/tables/{table_id}/fields/{column_id}"
        response = requests.patch(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

    def create_table(self, base_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.META_URL}/bases/{base_id}/tables"
        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()
    
    def update_table(self, base_id: str, table_id_or_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.META_URL}/bases/{base_id}/tables/{table_id_or_name}"
        response = requests.patch(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

    # Base management methods
    def list_bases(self, offset: Optional[str] = None) -> Dict[str, Any]:
        url = f"{self.META_URL}/bases"
        params = {}
        if offset:
            params["offset"] = offset
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    def get_base_schema(self, base_id: str, include: Optional[List[str]] = None) -> Dict[str, Any]:
        url = f"{self.META_URL}/bases/{base_id}/tables"
        params = {}
        if include:
            params["include"] = include
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    def create_base(self, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.META_URL}/bases"
        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

    # Webhook management methods
    def list_webhooks(self, base_id: str) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/bases/{base_id}/webhooks"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def create_webhook(self, base_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/bases/{base_id}/webhooks"
        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

    def delete_webhook(self, base_id: str, webhook_id: str) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/bases/{base_id}/webhooks/{webhook_id}"
        response = requests.delete(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def list_webhook_payloads(self, base_id: str, webhook_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/bases/{base_id}/webhooks/{webhook_id}/payloads"
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    # User information methods
    def get_user_info(self) -> Dict[str, Any]:
        url = f"{self.META_URL}/whoami"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
