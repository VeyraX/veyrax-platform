from typing import Dict, Any, List, Optional
import os
from .client import DocuSignClient
from .schema import (
    CreateEnvelopeParams,
    EnvelopeInfo,
    RecipientViewRequest,
    RecipientViewResponse,
    Document,
    FormData,
    ApiResponse
)
from ..common.component_handler import load_components, prepare_components_auto

class DocuSignService:
    def __init__(self, client: DocuSignClient, account_id: str):
        self.client = client
        self.account_id = account_id
        self.components_data = self._load_components()

    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)

    def prepare_response(self, data: Any, component_name: str = None) -> ApiResponse:
        tool_name = "docusign"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)

    def create_envelope(self, params: CreateEnvelopeParams) -> ApiResponse:
        envelope_definition = {
            "emailSubject": params.email_subject,
            "emailBlurb": params.email_body,
            "documents": [
                {
                    "documentBase64": doc.document_base64,
                    "name": doc.name,
                    "fileExtension": doc.file_extension,
                    "documentId": str(i + 1)
                } for i, doc in enumerate(params.documents)
            ],
            "recipients": {
                "signers": [
                    {
                        "email": signer.email,
                        "name": signer.name,
                        "recipientId": str(i + 1),
                        "routingOrder": signer.routing_order,
                        "roleName": signer.role_name
                    } for i, signer in enumerate(params.signers)
                ]
            },
            "status": "sent"
        }

        response = self.client.create_envelope(self.account_id, envelope_definition)
        envelope_info = EnvelopeInfo(
            envelope_id=response["envelopeId"],
            status=response["status"],
            created_datetime=response["statusDateTime"]
        )
        return self.prepare_response(envelope_info)

    def get_envelope(self, envelope_id: str) -> ApiResponse:
        response = self.client.get_envelope(self.account_id, envelope_id)
        envelope_info = EnvelopeInfo(
            envelope_id=response["envelopeId"],
            status=response["status"],
            created_datetime=response["createdDateTime"],
            sent_datetime=response.get("sentDateTime"),
            completed_datetime=response.get("completedDateTime"),
            declined_datetime=response.get("declinedDateTime"),
            voided_datetime=response.get("voidedDateTime")
        )
        return self.prepare_response(envelope_info)

    def get_document(self, envelope_id: str, document_id: str) -> ApiResponse:
        document_content = self.client.get_document(self.account_id, envelope_id, document_id)
        document = Document(
            document_base64=document_content,
            name=f"document_{document_id}.pdf",
            file_extension="pdf",
            document_id=document_id
        )
        return self.prepare_response(document)

    def create_recipient_view(self, envelope_id: str, view_request: RecipientViewRequest) -> ApiResponse:
        request_body = {
            "returnUrl": view_request.return_url,
            "authenticationMethod": "none",
            "email": view_request.email,
            "userName": view_request.name,
            "clientUserId": "1"
        }

        response = self.client.create_recipient_view(self.account_id, envelope_id, request_body)
        view_response = RecipientViewResponse(url=response["url"])
        return self.prepare_response(view_response)

    def get_form_data(self, envelope_id: str) -> ApiResponse:
        response = self.client.get_form_data(self.account_id, envelope_id)
        form_data = FormData(form_data=response)
        return self.prepare_response(form_data)

    def get_user_info(self) -> Dict[str, Any]:
        """Get user information to validate token"""
        return self.client.get_user_info()
