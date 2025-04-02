from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from enum import Enum

class EnvelopeStatus(str, Enum):
    SENT = "sent"
    DELIVERED = "delivered"
    COMPLETED = "completed"
    DECLINED = "declined"
    VOIDED = "voided"

class Signer(BaseModel):
    email: str = Field(..., description="Signer's email address")
    name: str = Field(..., description="Signer's full name")
    role_name: Optional[str] = Field(None, description="Role name for the signer")
    routing_order: Optional[int] = Field(1, description="Order of signing")

class Document(BaseModel):
    document_base64: str = Field(..., description="Base64 encoded document content")
    name: str = Field(..., description="Document name")
    file_extension: str = Field(..., description="Document file extension (pdf, doc, etc)")
    document_id: Optional[str] = Field(None, description="Document ID")

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
    data: Document

class RecipientViewUrlResponse(BaseModel):
    data: RecipientViewResponse

# API Response
class ApiResponse(BaseModel):
    data: Union[EnvelopeInfo, EnvelopeList, Document, RecipientViewResponse, FormData]
    component: Optional[Dict[str, Any]] = None
