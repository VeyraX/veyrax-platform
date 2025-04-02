import requests
from typing import Dict, Any, Optional
import json

class DocuSignClient:
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

    def get_user_info(self) -> Dict[str, Any]:
        """Get user information to validate token"""
        url = "https://account.docusign.com/oauth/userinfo"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def create_envelope(self, account_id: str, envelope_definition: Dict[str, Any]) -> Dict[str, Any]:
        """Create and send an envelope"""
        url = f"https://demo.docusign.net/restapi/v2.1/accounts/{account_id}/envelopes"
        response = requests.post(url, headers=self.headers, json=envelope_definition)
        response.raise_for_status()
        return response.json()

    def get_envelope(self, account_id: str, envelope_id: str) -> Dict[str, Any]:
        """Get envelope information"""
        url = f"https://demo.docusign.net/restapi/v2.1/accounts/{account_id}/envelopes/{envelope_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_document(self, account_id: str, envelope_id: str, document_id: str) -> bytes:
        """Download a document from an envelope"""
        url = f"https://demo.docusign.net/restapi/v2.1/accounts/{account_id}/envelopes/{envelope_id}/documents/{document_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.content

    def create_recipient_view(self, account_id: str, envelope_id: str, view_request: Dict[str, Any]) -> Dict[str, Any]:
        """Create a recipient view (embedded signing)"""
        url = f"https://demo.docusign.net/restapi/v2.1/accounts/{account_id}/envelopes/{envelope_id}/views/recipient"
        response = requests.post(url, headers=self.headers, json=view_request)
        response.raise_for_status()
        return response.json()

    def get_form_data(self, account_id: str, envelope_id: str) -> Dict[str, Any]:
        """Get form data from an envelope"""
        url = f"https://demo.docusign.net/restapi/v2.1/accounts/{account_id}/envelopes/{envelope_id}/form_data"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def _clean_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Clean parameters before sending to API"""
        return {k: v for k, v in params.items() if v is not None}
