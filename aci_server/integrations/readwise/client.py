import requests
from typing import Dict, Any, List, Optional

class ReadwiseClient:
    BASE_URL = "https://readwise.io/api/v3"
    AUTH_URL = "https://readwise.io/api/v2/auth/"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Token {api_key}"
        }

    def validate_token(self) -> bool:
        response = requests.get(
            self.AUTH_URL,
            headers=self.headers
        )
        return response.status_code == 204

    def save_document(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Save a new document to Reader"""
        response = requests.post(
            f"{self.BASE_URL}/save/",
            headers=self.headers,
            json=params
        )
        response.raise_for_status()
        return response.json()

    def list_documents(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """List documents with optional filtering"""
        response = requests.get(
            f"{self.BASE_URL}/list/",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()

    def update_document(self, document_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update a document"""
        response = requests.patch(
            f"{self.BASE_URL}/update/{document_id}/",
            headers=self.headers,
            json=params
        )
        response.raise_for_status()
        return response.json()

    def delete_document(self, document_id: str) -> None:
        """Delete a document"""
        response = requests.delete(
            f"{self.BASE_URL}/delete/{document_id}/",
            headers=self.headers
        )
        response.raise_for_status()
        return None