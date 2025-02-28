import requests
from typing import Dict, Any, List, Optional, Union

class ResendClient:
    BASE_URL = "https://api.resend.com"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def send_email(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send a single email through Resend API."""
        response = requests.post(
            f"{self.BASE_URL}/emails",
            headers=self.headers,
            json=email_data
        )
        response.raise_for_status()
        return response.json()

    def send_batch_emails(self, emails_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Send multiple emails in a single batch request."""
        response = requests.post(
            f"{self.BASE_URL}/emails/batch",
            headers=self.headers,
            json=emails_data
        )
        response.raise_for_status()
        return response.json()

    def get_email(self, email_id: str) -> Dict[str, Any]:
        """Retrieve details of a specific email."""
        response = requests.get(
            f"{self.BASE_URL}/emails/{email_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def update_email(self, email_id: str, scheduled_at: str) -> Dict[str, Any]:
        """Update a scheduled email."""
        response = requests.patch(
            f"{self.BASE_URL}/emails/{email_id}",
            headers=self.headers,
            json={"scheduled_at": scheduled_at}
        )
        response.raise_for_status()
        return response.json()

    def cancel_email(self, email_id: str) -> Dict[str, Any]:
        """Cancel a scheduled email."""
        response = requests.post(
            f"{self.BASE_URL}/emails/{email_id}/cancel",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def create_domain(self, domain_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new domain."""
        response = requests.post(
            f"{self.BASE_URL}/domains",
            headers=self.headers,
            json=domain_data
        )
        response.raise_for_status()
        return response.json()

    def get_domain(self, domain_id: str) -> Dict[str, Any]:
        """Retrieve details of a specific domain."""
        response = requests.get(
            f"{self.BASE_URL}/domains/{domain_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def verify_domain(self, domain_id: str) -> Dict[str, Any]:
        """Verify a domain."""
        response = requests.post(
            f"{self.BASE_URL}/domains/{domain_id}/verify",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def update_domain(self, domain_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a domain."""
        response = requests.patch(
            f"{self.BASE_URL}/domains/{domain_id}",
            headers=self.headers,
            json=update_data
        )
        response.raise_for_status()
        return response.json()

    def list_domains(self) -> Dict[str, Any]:
        """List all domains."""
        response = requests.get(
            f"{self.BASE_URL}/domains",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def delete_domain(self, domain_id: str) -> Dict[str, Any]:
        """Delete a domain."""
        response = requests.delete(
            f"{self.BASE_URL}/domains/{domain_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def create_api_key(self, api_key_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new API key."""
        response = requests.post(
            f"{self.BASE_URL}/api-keys",
            headers=self.headers,
            json=api_key_data
        )
        response.raise_for_status()
        return response.json()

    def list_api_keys(self) -> Dict[str, Any]:
        """List all API keys."""
        response = requests.get(
            f"{self.BASE_URL}/api-keys",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def delete_api_key(self, api_key_id: str) -> Dict[str, Any]:
        """Delete an API key."""
        response = requests.delete(
            f"{self.BASE_URL}/api-keys/{api_key_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return {"id": api_key_id, "deleted": True}

    def create_broadcast(self, broadcast_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new broadcast."""
        response = requests.post(
            f"{self.BASE_URL}/broadcasts",
            headers=self.headers,
            json=broadcast_data
        )
        response.raise_for_status()
        return response.json()

    def get_broadcast(self, broadcast_id: str) -> Dict[str, Any]:
        """Retrieve details of a specific broadcast."""
        response = requests.get(
            f"{self.BASE_URL}/broadcasts/{broadcast_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def send_broadcast(self, broadcast_id: str, send_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send a broadcast."""
        response = requests.post(
            f"{self.BASE_URL}/broadcasts/{broadcast_id}/send",
            headers=self.headers,
            json=send_data
        )
        response.raise_for_status()
        return response.json()

    def delete_broadcast(self, broadcast_id: str) -> Dict[str, Any]:
        """Delete a broadcast."""
        response = requests.delete(
            f"{self.BASE_URL}/broadcasts/{broadcast_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def list_broadcasts(self) -> Dict[str, Any]:
        """List all broadcasts."""
        response = requests.get(
            f"{self.BASE_URL}/broadcasts",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def create_audience(self, audience_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new audience."""
        response = requests.post(
            f"{self.BASE_URL}/audiences",
            headers=self.headers,
            json=audience_data
        )
        response.raise_for_status()
        return response.json()

    def get_audience(self, audience_id: str) -> Dict[str, Any]:
        """Retrieve details of a specific audience."""
        response = requests.get(
            f"{self.BASE_URL}/audiences/{audience_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def delete_audience(self, audience_id: str) -> Dict[str, Any]:
        """Delete an audience."""
        response = requests.delete(
            f"{self.BASE_URL}/audiences/{audience_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def list_audiences(self) -> Dict[str, Any]:
        """List all audiences."""
        response = requests.get(
            f"{self.BASE_URL}/audiences",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def create_contact(self, audience_id: str, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new contact in an audience."""
        response = requests.post(
            f"{self.BASE_URL}/audiences/{audience_id}/contacts",
            headers=self.headers,
            json=contact_data
        )
        response.raise_for_status()
        return response.json()

    def get_contact(self, audience_id: str, contact_id: str) -> Dict[str, Any]:
        """Retrieve details of a specific contact."""
        response = requests.get(
            f"{self.BASE_URL}/audiences/{audience_id}/contacts/{contact_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def update_contact(self, audience_id: str, contact_identifier: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a contact. Contact identifier can be ID or email."""
        response = requests.patch(
            f"{self.BASE_URL}/audiences/{audience_id}/contacts/{contact_identifier}",
            headers=self.headers,
            json=update_data
        )
        response.raise_for_status()
        return response.json()

    def delete_contact(self, audience_id: str, contact_identifier: str) -> Dict[str, Any]:
        """Delete a contact. Contact identifier can be ID or email."""
        response = requests.delete(
            f"{self.BASE_URL}/audiences/{audience_id}/contacts/{contact_identifier}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def list_contacts(self, audience_id: str) -> Dict[str, Any]:
        """List all contacts in an audience."""
        response = requests.get(
            f"{self.BASE_URL}/audiences/{audience_id}/contacts",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
