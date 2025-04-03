from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from enum import Enum
import base64

class EnvelopeStatus(str, Enum):
    sent = "sent"
    delivered = "delivered"
    completed = "completed"
    declined = "declined"
    voided = "voided"

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
    routing_order: int = Field(1, description="Order of signing")
    client_user_id: Optional[str] = Field(None, description="IMPORTANT: client_user_id is REQUIRED for embedded signing! If you plan to use embedded signing or create a signing form, you MUST provide this field when creating the envelope. Without it, you won't be able to create a recipient view for signing.")

class Document(BaseModel):
    name: str = Field(..., description="Document name")
    file_extension: str = Field(..., description="IMPORTANT: For text documents (using document_content) file_extension MUST be 'txt'. For PDF documents (using document_base64) file_extension MUST be 'pdf'")
    document_base64: Optional[str] = Field(None, description="Base64 encoded document content. Use this for PDF files only with file_extension='pdf'")
    document_content: Optional[str] = Field(None, description="Plain text document content. Use this for text documents only with file_extension='txt'")
    document_id: Optional[str] = Field(None, description="Document ID - this ID is assigned when creating the envelope and should be used for subsequent operations like getting form data")

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
            return base64.b64decode(self.document_base64).decode('utf-8')
        else:
            raise ValueError("Either document_base64 or document_content must be provided")

class CreateEnvelopeParams(BaseModel):
    documents: List[Document] = Field(..., description="List of documents to sign")
    signers: List[Signer] = Field(..., description="List of signers")
    email_subject: str = Field(..., description="Email subject")
    email_body: str = Field(..., description="Email body")

class GetEnvelopeParams(BaseModel):
    envelope_id: str = Field(..., description="ID of the envelope to retrieve")

class GetDocumentParams(BaseModel):
    envelope_id: str = Field(..., description="ID of the envelope containing the document")
    document_id: str = Field(..., description="ID of the document to retrieve. This ID is assigned when envelope is created, usually starts from '1' for the first document")
    return_format: str = Field("base64", description="Format to return document in: 'base64' or 'text'")

class GetFormDataParams(BaseModel):
    envelope_id: str = Field(..., description="ID of the envelope to get form data from")

class GetEnvelopesParams(BaseModel):
    from_date: str = Field(..., description="Filter by date (YYYY-MM-DDThh:mm:ssZ), defaults to last 30 days if not specified")
    status: Optional[EnvelopeStatus] = Field(None, description="Filter by status (sent, delivered, completed, declined, voided)")
    folder_ids: Optional[List[str]] = Field(None, description="List of folder IDs to filter by")
    transaction_ids: Optional[List[str]] = Field(None, description="List of transaction IDs to filter by")
    envelope_ids: Optional[List[str]] = Field(None, description="List of envelope IDs to filter by")

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
    client_user_id: str = Field(..., description="IMPORTANT: Must match the client_user_id that was used when creating the envelope for this signer")

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
    component: Optional[Dict[str, Any]] = None

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
    data: Union[EnvelopeInfo, EnvelopeList, Document, RecipientViewResponse, FormData, UserInfo, EnvelopesResponse]
    component: Optional[Dict[str, Any]] = None
