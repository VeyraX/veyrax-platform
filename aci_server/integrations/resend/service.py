from typing import Optional, Dict, Any, List, Union
from .client import ResendClient
from .schema import (
    EmailResponse, BatchEmailResponse, SendEmailParams, 
    SendBatchEmailsParams, ApiResponse, Domain, DomainList, CreateDomainParams,
    UpdateDomainParams, ApiKeyToken, ApiKeyList, CreateApiKeyParams,
    Broadcast, BroadcastList, CreateBroadcastParams, GetBroadcastParams, SendBroadcastParams, DeleteBroadcastParams,
    Audience, AudienceList, CreateAudienceParams, GetAudienceParams, DeleteAudienceParams,
    Contact, ContactList, CreateContactParams, GetContactParams, UpdateContactParams, DeleteContactParams
)
import os
import json
from ..common.component_handler import load_components, prepare_components_auto

class ResendService:
    def __init__(self, client: ResendClient):
        self.client = client
        self.components_data = self._load_components()

    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
        
    def prepare_response(self, data: Union[EmailResponse, BatchEmailResponse, Domain, DomainList], component_name: str = None) -> ApiResponse:
        tool_name = "resend"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)

    def send_email(self, params: SendEmailParams) -> ApiResponse:
        """Send a single email through Resend API."""
        email_data = params.dict(by_alias=True, exclude_none=True)
        
        response = self.client.send_email(email_data)
        
        email_response = EmailResponse(id=response.get("id"))

        get_email_response = self.client.get_email(email_response.id)

        email_response = EmailResponse(**get_email_response)
        
        return self.prepare_response(email_response, "ResendEmailCard")

    def send_batch_emails(self, params: SendBatchEmailsParams) -> ApiResponse:
        """Send multiple emails in a batch."""
        emails_data = [email.dict(by_alias=True, exclude_none=True) for email in params.emails]
        
        response = self.client.send_batch_emails(emails_data)
        
        batch_response = BatchEmailResponse(data=response.get("data", []))
        
        return self.prepare_response(batch_response, "ResendEmailCard")

    def get_email(self, email_id: str) -> ApiResponse:
        """Retrieve details of a specific email."""
        response = self.client.get_email(email_id)
        
        email_response = EmailResponse(**response)
        
        return self.prepare_response(email_response, "ResendEmailCard")

    def update_email(self, email_id: str, scheduled_at: str) -> ApiResponse:
        """Update a scheduled email."""
        response = self.client.update_email(email_id, scheduled_at)
        
        email_response = EmailResponse(**response)

        get_email_response = self.client.get_email(email_response.id)

        email_response = EmailResponse(**get_email_response)
        
        return self.prepare_response(email_response, "ResendEmailCard")

    def cancel_email(self, email_id: str) -> ApiResponse:
        """Cancel a scheduled email."""
        response = self.client.cancel_email(email_id)
        
        email_response = EmailResponse(**response)
        
        return self.prepare_response(email_response, None)

    def create_domain(self, params: CreateDomainParams) -> ApiResponse:
        """Create a new domain."""
        domain_data = params.dict(exclude_none=True)
        
        response = self.client.create_domain(domain_data)
        
        domain_response = Domain(**response)
        
        return self.prepare_response(domain_response, "ResendDomainCard")

    def get_domain(self, domain_id: str) -> ApiResponse:
        """Retrieve details of a specific domain."""
        response = self.client.get_domain(domain_id)
        
        domain_response = Domain(**response)
        
        return self.prepare_response(domain_response, "ResendDomainCard")

    def verify_domain(self, domain_id: str) -> ApiResponse:
        """Verify a domain."""
        response = self.client.verify_domain(domain_id)
        
        return self.prepare_response(response, "ResendDomainCard")

    def update_domain(self, domain_id: str, params: UpdateDomainParams) -> ApiResponse:
        """Update a domain."""
        update_data = {k: v for k, v in params.dict().items() if k != 'domain_id' and v is not None}
        
        response = self.client.update_domain(domain_id, update_data)
        
        return self.prepare_response(response, "ResendDomainCard")

    def list_domains(self) -> ApiResponse:
        """List all domains."""
        response = self.client.list_domains()
        
        domains_response = DomainList(**response)
        
        return self.prepare_response(domains_response, "ResendDomainListCard")

    def delete_domain(self, domain_id: str) -> ApiResponse:
        """Delete a domain."""
        response = self.client.delete_domain(domain_id)
        
        return self.prepare_response(response, "ResendDomainCard")

    def create_api_key(self, params: CreateApiKeyParams) -> ApiResponse:
        """Create a new API key."""
        api_key_data = params.dict(exclude_none=True)
        
        response = self.client.create_api_key(api_key_data)
        
        api_key_response = ApiKeyToken(**response)
        
        return self.prepare_response(api_key_response, "ResendApiKeyCard")

    def list_api_keys(self) -> ApiResponse:
        """List all API keys."""
        response = self.client.list_api_keys()
        
        api_keys_response = ApiKeyList(**response)
        
        return self.prepare_response(api_keys_response, "ResendApiKeyListCard")

    def delete_api_key(self, api_key_id: str) -> ApiResponse:
        """Delete an API key."""
        response = self.client.delete_api_key(api_key_id)
        
        return self.prepare_response(response, "ResendApiKeyCard")

    def create_broadcast(self, params: CreateBroadcastParams) -> ApiResponse:
        """Create a new broadcast."""
        broadcast_data = params.dict(by_alias=True, exclude_none=True)
        
        response = self.client.create_broadcast(broadcast_data)
        
        # Get audience details to populate audience_name
        audience_response = self.client.get_audience(params.audience_id)
        
        broadcast_response = Broadcast(
            id=response["id"],
            audience_id=params.audience_id,
            audience_name=audience_response.get("name"),
            status="draft",
            created_at=response.get("created_at"),
            name=params.name,
            from_email=params.from_email,
            subject=params.subject,
            reply_to=params.reply_to,
            object="broadcast"
        )
        
        return self.prepare_response(broadcast_response, "ResendBroadcastCard")

    def get_broadcast(self, broadcast_id: str) -> ApiResponse:
        """Retrieve details of a specific broadcast."""
        response = self.client.get_broadcast(broadcast_id)
        
        broadcast_response = Broadcast(**response)
        
        return self.prepare_response(broadcast_response, "ResendBroadcastCard")

    def send_broadcast(self, broadcast_id: str, scheduled_at: Optional[str] = None) -> ApiResponse:
        """Send a broadcast."""
        send_data = {}
        if scheduled_at:
            send_data["scheduled_at"] = scheduled_at
        
        response = self.client.send_broadcast(broadcast_id, send_data)
        
        return self.prepare_response(response, "ResendBroadcastCard")

    def delete_broadcast(self, broadcast_id: str) -> ApiResponse:
        """Delete a broadcast."""
        response = self.client.delete_broadcast(broadcast_id)
        
        return self.prepare_response(response, None)

    def list_broadcasts(self) -> ApiResponse:
        """List all broadcasts."""
        response = self.client.list_broadcasts()
        
        broadcasts_response = BroadcastList(**response)
        
        return self.prepare_response(broadcasts_response, "ResendBroadcastCard")

    def create_audience(self, params: CreateAudienceParams) -> ApiResponse:
        """Create a new audience."""
        audience_data = params.dict(exclude_none=True)
        
        response = self.client.create_audience(audience_data)

        response["url"] = f"https://resend.com/audiences/{response['id']}"
        
        audience_response = Audience(**response)
        
        return self.prepare_response(audience_response, "ResendAudienceCard")

    def get_audience(self, audience_id: str) -> ApiResponse:
        """Retrieve details of a specific audience."""
        response = self.client.get_audience(audience_id)
        
        response["url"] = f"https://resend.com/audiences/{response['id']}"

        audience_response = Audience(**response)

        
        
        return self.prepare_response(audience_response, "ResendAudienceCard")

    def delete_audience(self, audience_id: str) -> ApiResponse:
        """Delete an audience."""
        response = self.client.delete_audience(audience_id)
        
        return self.prepare_response(response, None)

    def list_audiences(self) -> ApiResponse:
        """List all audiences."""
        response = self.client.list_audiences()
        
        # Create proper Audience instances with URL
        audience_list = [
            Audience(
                **audience_data,
                url=f"https://resend.com/audiences/{audience_data['id']}"
            )
            for audience_data in response.get('data', [])
        ]
        
        audiences_response = AudienceList(data=audience_list)
        
        return self.prepare_response(audiences_response, "ResendAudienceCard")

    def create_contact(self, params: CreateContactParams) -> ApiResponse:
        """Create a new contact in an audience."""
        audience_id = params.audience_id
        
        contact_data = {
            "email": params.email,
            "first_name": params.first_name,
            "last_name": params.last_name,
            "unsubscribed": params.unsubscribed
        }
        contact_data = {k: v for k, v in contact_data.items() if v is not None}
        
        response = self.client.create_contact(audience_id, contact_data)
        
        return self.prepare_response(response, "ResendContactCard")

    def get_contact(self, audience_id: str, contact_id: str) -> ApiResponse:
        """Retrieve details of a specific contact."""
        response = self.client.get_contact(audience_id, contact_id)
        
        contact_response = Contact(**response)
        
        return self.prepare_response(contact_response, "ResendContactCard")

    def update_contact(self, params: UpdateContactParams) -> ApiResponse:
        """Update a contact."""
        audience_id = params.audience_id
        
        contact_identifier = params.contact_id if params.contact_id else params.email
        if not contact_identifier:
            raise ValueError("Either contact_id or email must be provided")
        
        update_data = {
            "first_name": params.first_name,
            "last_name": params.last_name,
            "unsubscribed": params.unsubscribed
        }
        update_data = {k: v for k, v in update_data.items() if v is not None}
        
        response = self.client.update_contact(audience_id, contact_identifier, update_data)

        get_contact_response = self.client.get_contact(audience_id, contact_identifier)

        contact_response = Contact(**get_contact_response)
        
        return self.prepare_response(contact_response, "ResendContactCard")

    def delete_contact(self, params: DeleteContactParams) -> ApiResponse:
        """Delete a contact."""
        audience_id = params.audience_id
        
        contact_identifier = params.contact_id if params.contact_id else params.email
        if not contact_identifier:
            raise ValueError("Either contact_id or email must be provided")
        
        response = self.client.delete_contact(audience_id, contact_identifier)
        
        return self.prepare_response(response, None)

    def list_contacts(self, audience_id: str) -> ApiResponse:
        """List all contacts in an audience."""
        response = self.client.list_contacts(audience_id)
        
        contacts_response = ContactList(**response)
        
        return self.prepare_response(contacts_response, "ResendContactCard")
