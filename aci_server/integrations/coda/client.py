import requests
from typing import Dict, Any, Optional

class CodaClient:
    BASE_URL = "https://coda.io/apis/v1"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def list_docs(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/docs",
            headers=self.headers,
            params=self._clean_params(params or {})
        )
        response.raise_for_status()
        return response.json()

    def get_doc(self, doc_id: str) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/docs/{doc_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def list_pages(self, doc_id: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/docs/{doc_id}/pages",
            headers=self.headers,
            params=self._clean_params(params or {})
        )
        response.raise_for_status()
        return response.json()

    def get_page(self, doc_id: str, page_id: str) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/docs/{doc_id}/pages/{page_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
        
    def create_page(self, doc_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.post(
            f"{self.BASE_URL}/docs/{doc_id}/pages",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
        
    def update_page(self, doc_id: str, page_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.put(
            f"{self.BASE_URL}/docs/{doc_id}/pages/{page_id}",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
        
    def delete_page(self, doc_id: str, page_id: str) -> Dict[str, Any]:
        response = requests.delete(
            f"{self.BASE_URL}/docs/{doc_id}/pages/{page_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
        
    def export_page(self, doc_id: str, page_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.post(
            f"{self.BASE_URL}/docs/{doc_id}/pages/{page_id}/export",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
        
    def get_export_status(self, doc_id: str, page_id: str, request_id: str) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/docs/{doc_id}/pages/{page_id}/export/{request_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def _clean_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        cleaned = {}
        for k, v in params.items():
            if v is None:
                continue
            if isinstance(v, bool):
                cleaned[k] = str(v).lower()
            elif isinstance(v, list):
                cleaned[k] = ",".join(map(str, v))
            else:
                cleaned[k] = v
        return cleaned

    # Table methods
    def list_tables(self, doc_id: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/docs/{doc_id}/tables",
            headers=self.headers,
            params=self._clean_params(params or {})
        )
        response.raise_for_status()
        return response.json()
    
    def get_table(self, doc_id: str, table_id: str) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/docs/{doc_id}/tables/{table_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    # Column methods
    def list_columns(self, doc_id: str, table_id: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/docs/{doc_id}/tables/{table_id}/columns",
            headers=self.headers,
            params=self._clean_params(params or {})
        )
        response.raise_for_status()
        return response.json()
    
    def get_column(self, doc_id: str, table_id: str, column_id: str) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/docs/{doc_id}/tables/{table_id}/columns/{column_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    # Row methods
    def list_rows(self, doc_id: str, table_id: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/docs/{doc_id}/tables/{table_id}/rows",
            headers=self.headers,
            params=self._clean_params(params or {})
        )
        response.raise_for_status()
        return response.json()
    
    def get_row(self, doc_id: str, table_id: str, row_id: str) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/docs/{doc_id}/tables/{table_id}/rows/{row_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def create_rows(self, doc_id: str, table_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.post(
            f"{self.BASE_URL}/docs/{doc_id}/tables/{table_id}/rows",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def update_row(self, doc_id: str, table_id: str, row_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.put(
            f"{self.BASE_URL}/docs/{doc_id}/tables/{table_id}/rows/{row_id}",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def delete_rows(self, doc_id: str, table_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.delete(
            f"{self.BASE_URL}/docs/{doc_id}/tables/{table_id}/rows",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def delete_row(self, doc_id: str, table_id: str, row_id: str) -> Dict[str, Any]:
        response = requests.delete(
            f"{self.BASE_URL}/docs/{doc_id}/tables/{table_id}/rows/{row_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def push_button(self, doc_id: str, table_id: str, row_id: str, column_id: str) -> Dict[str, Any]:
        response = requests.post(
            f"{self.BASE_URL}/docs/{doc_id}/tables/{table_id}/rows/{row_id}/buttons/{column_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    # Formula methods
    def list_formulas(self, doc_id: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/docs/{doc_id}/formulas",
            headers=self.headers,
            params=self._clean_params(params or {})
        )
        response.raise_for_status()
        return response.json()
    
    def get_formula(self, doc_id: str, formula_id: str) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/docs/{doc_id}/formulas/{formula_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    # Control methods
    def list_controls(self, doc_id: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/docs/{doc_id}/controls",
            headers=self.headers,
            params=self._clean_params(params or {})
        )
        response.raise_for_status()
        return response.json()
    
    def get_control(self, doc_id: str, control_id: str) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/docs/{doc_id}/controls/{control_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    # User methods
    def get_whoami(self) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/whoami",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
