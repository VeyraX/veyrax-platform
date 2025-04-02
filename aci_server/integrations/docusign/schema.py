from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from enum import Enum
import base64

class EnvelopeStatus(str, Enum):
    SENT = "sent"
    DELIVERED = "delivered"
    COMPLETED = "completed"
    DECLINED = "declined"
    VOIDED = "voided"

class DocuSignAccount(BaseModel):
    account_id: str = Field(..., description="DocuSign account ID")
    account_name: str = Field(..., description="Account name")
    base_uri: str = Field(..., description="Base URI for API calls")
    is_default: bool = Field(..., description="Whether this is the default account")

class UserInfo(BaseModel):
    sub: str = Field(..., description="User ID")
    name: str = Field(..., description="Full name")
    given_name: str = Field(..., description="First name")
    family_name: str = Field(..., description="Last name")
    email: str = Field(..., description="Email address")
    created: str = Field(..., description="Account creation date")
    accounts: List[DocuSignAccount] = Field(..., description="List of DocuSign accounts")

class Signer(BaseModel):
    email: str = Field(..., description="Signer's email address")
    name: str = Field(..., description="Signer's full name")
    role_name: Optional[str] = Field(None, description="Role name for the signer")
    routing_order: Optional[int] = Field(1, description="Order of signing")
    client_user_id: Optional[str] = Field(None, description="Client User ID for embedded signing")

class Document(BaseModel):
    document_base64: Optional[str] = Field(None, description="Base64 encoded document content")
    document_content: Optional[str] = Field(None, description="Plain text document content")
    name: str = Field(..., description="Document name")
    file_extension: str = Field(..., description="Document file extension (pdf, doc, etc)")
    document_id: Optional[str] = Field(None, description="Document ID")

    @property
    def get_document_base64(self) -> str:
        """Returns base64 content, converting text content if necessary"""
        if self.document_base64:
            return self.document_base64
        elif self.document_content:
            # Simple text to base64 conversion
            return base64.b64encode(self.document_content.encode('utf-8')).decode('utf-8')
        else:
            raise ValueError("Either document_base64 or document_content must be provided")

    @property
    def get_document_content(self) -> str:
        """Returns text content, converting base64 if necessary"""
        if self.document_content:
            return self.document_content
        elif self.document_base64:
            # Simple base64 to text conversion
            return base64.b64decode(self.document_base64).decode('utf-8')
        else:
            raise ValueError("Either document_base64 or document_content must be provided")

class CreateEnvelopeParams(BaseModel):
    documents: List[Document] = Field(..., description="List of documents to sign")
    signers: List[Signer] = Field(..., description="List of signers")
    email_subject: Optional[str] = Field("Please sign this document", description="Email subject")
    email_body: Optional[str] = Field("Please sign this document", description="Email body")

class GetEnvelopeParams(BaseModel):
    envelope_id: str = Field(..., description="ID of the envelope to retrieve")

class GetDocumentParams(BaseModel):
    envelope_id: str = Field(..., description="ID of the envelope containing the document")
    document_id: str = Field(..., description="ID of the document to retrieve")
    return_format: Optional[str] = Field("base64", description="Format to return document in: 'base64' or 'text'")

class GetFormDataParams(BaseModel):
    envelope_id: str = Field(..., description="ID of the envelope to get form data from")

class EnvelopeInfo(BaseModel):
    envelope_id: str
    status: EnvelopeStatus
    created_datetime: str
    sent_datetime: Optional[str] = None
    completed_datetime: Optional[str] = None
    declined_datetime: Optional[str] = None
    voided_datetime: Optional[str] = None

class RecipientViewRequest(BaseModel):
    return_url: str = Field(..., description="URL to redirect after signing")
    email: str = Field(..., description="Signer's email")
    name: str = Field(..., description="Signer's name")

class RecipientViewResponse(BaseModel):
    url: str = Field(..., description="URL for embedded signing")

class FormData(BaseModel):
    form_data: Dict[str, Any] = Field(..., description="Form data from envelope")

class EnvelopeList(BaseModel):
    envelopes: List[EnvelopeInfo]

class DocumentList(BaseModel):
    documents: List[Document]

class FormDataResponse(BaseModel):
    data: FormData

class EnvelopeResponse(BaseModel):
    data: EnvelopeInfo

class EnvelopesResponse(BaseModel):
    data: EnvelopeList

class DocumentResponse(BaseModel):
    document_base64: Optional[str] = Field(None, description="Base64 encoded document content")
    document_content: Optional[str] = Field(None, description="Plain text document content")
    name: str = Field(..., description="Document name")
    file_extension: str = Field(..., description="Document file extension")
    document_id: Optional[str] = Field(None, description="Document ID")

class RecipientViewUrlResponse(BaseModel):
    data: RecipientViewResponse

class UserInfoResponse(BaseModel):
    data: UserInfo

# API Response
class ApiResponse(BaseModel):
    data: Union[EnvelopeInfo, EnvelopeList, Document, RecipientViewResponse, FormData, UserInfo]
    component: Optional[Dict[str, Any]] = None
