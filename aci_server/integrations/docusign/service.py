from typing import Dict, Any, List, Optional
import os
import base64
import io
from PyPDF2 import PdfReader
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
                    "documentBase64": doc.get_document_base64,
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
                        "roleName": signer.role_name,
                        "clientUserId": signer.client_user_id
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

    def get_document(self, envelope_id: str, document_id: str, return_format: str = "base64") -> ApiResponse:
        """Get document from envelope with specified format"""
        document_content = self.client.get_document(self.account_id, envelope_id, document_id)
        
        response_data = {
            "name": f"document_{document_id}.pdf",
            "file_extension": "pdf",
            "document_id": document_id
        }

        if return_format == "text":
            try:
                if document_content.startswith(b'%PDF'):
                    pdf_file = io.BytesIO(document_content)
                    pdf_reader = PdfReader(pdf_file)
                    text_content = ""
                    for page in pdf_reader.pages:
                        text_content += page.extract_text() + "\n"
                    response_data["document_content"] = text_content
                else:
                    try:
                        text_content = document_content.decode('utf-8')
                    except UnicodeDecodeError:
                        text_content = document_content.decode('latin-1')
                    response_data["document_content"] = text_content
            except Exception as e:
                response_data["document_base64"] = base64.b64encode(document_content).decode('utf-8')
                response_data["document_content"] = f"Failed to extract text: {str(e)}"
        else:
            response_data["document_base64"] = base64.b64encode(document_content).decode('utf-8')

        return self.prepare_response(response_data)

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

    def get_user_info(self) -> ApiResponse:
        """Get user information to validate token"""
        response = self.client.get_user_info()
        user_info = {
            "sub": response["sub"],
            "name": response["name"],
            "given_name": response["given_name"],
            "family_name": response["family_name"],
            "email": response["email"],
            "created": response["created"],
            "accounts": [{
                "account_id": account["account_id"],
                "account_name": account["account_name"],
                "base_uri": account["base_uri"],
                "is_default": account["is_default"]
            } for account in response["accounts"]]
        }
        return self.prepare_response(user_info, "user_info")
