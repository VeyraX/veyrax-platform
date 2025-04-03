import requests
from typing import Dict, Any, Optional, List
import json
import time
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, delay_seconds: int = 30):
        self.delay_seconds = delay_seconds
        self.last_request_time = None

    def wait_if_needed(self):
        now = datetime.now().timestamp()
        if self.last_request_time is not None:
            elapsed = now - self.last_request_time
            if elapsed < self.delay_seconds:
                time.sleep(self.delay_seconds - elapsed)
        self.last_request_time = datetime.now().timestamp()

class DocuSignClient:
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        self.rate_limiter = RateLimiter(delay_seconds=30)

    def _make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Make a rate-limited request to DocuSign API"""
        self.rate_limiter.wait_if_needed()
        response = requests.request(method, url, headers=self.headers, **kwargs)
        response.raise_for_status()
        return response

    def get_user_info(self) -> Dict[str, Any]:
        """Get user information to validate token"""
        url = "https://account-d.docusign.com/oauth/userinfo"
        response = self._make_request("GET", url)
        return response.json()

    def create_envelope(self, account_id: str, envelope_definition: Dict[str, Any]) -> Dict[str, Any]:
        """Create and send an envelope"""
        url = f"https://demo.docusign.net/restapi/v2.1/accounts/{account_id}/envelopes"
        response = self._make_request("POST", url, json=envelope_definition)
        return response.json()

    def get_envelope(self, account_id: str, envelope_id: str) -> Dict[str, Any]:
        """Get envelope information"""
        url = f"https://demo.docusign.net/restapi/v2.1/accounts/{account_id}/envelopes/{envelope_id}"
        response = self._make_request("GET", url)
        return response.json()

    def get_document(self, account_id: str, envelope_id: str, document_id: str) -> bytes:
        """Download a document from an envelope"""
        url = f"https://demo.docusign.net/restapi/v2.1/accounts/{account_id}/envelopes/{envelope_id}/documents/{document_id}"
        response = self._make_request("GET", url)
        return response.content

    def create_recipient_view(self, account_id: str, envelope_id: str, view_request: Dict[str, Any]) -> Dict[str, Any]:
        """Create a recipient view (embedded signing)"""
        url = f"https://demo.docusign.net/restapi/v2.1/accounts/{account_id}/envelopes/{envelope_id}/views/recipient"
        response = self._make_request("POST", url, json=view_request)
        return response.json()

    def get_form_data(self, account_id: str, envelope_id: str) -> Dict[str, Any]:
        """Get form data from an envelope"""
        url = f"https://demo.docusign.net/restapi/v2.1/accounts/{account_id}/envelopes/{envelope_id}/form_data"
        response = self._make_request("GET", url)
        return response.json()

    def get_envelopes(
        self, 
        account_id: str, 
        from_date: Optional[str] = None,
        status: Optional[str] = None,
        folder_ids: Optional[List[str]] = None,
        transaction_ids: Optional[List[str]] = None,
        envelope_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        url = f"https://demo.docusign.net/restapi/v2.1/accounts/{account_id}/envelopes"
        
        # If from_date not provided, use last 30 days
        if not from_date:
            from_date = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
            
        params = self._clean_params({
            "from_date": from_date,
            "status": status,
            "folder_ids": ','.join(folder_ids) if folder_ids else None,
            "transaction_ids": ','.join(transaction_ids) if transaction_ids else None,
            "envelope_ids": ','.join(envelope_ids) if envelope_ids else None
        })
        
        response = self._make_request("GET", url, params=params)
        return response.json()

    def _clean_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Clean parameters before sending to API"""
        return {k: v for k, v in params.items() if v is not None}
