from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union

class DocumentMetadata(BaseModel):
    id: str
    title: str
    url: Optional[str] = None
    revision_id: Optional[str] = None

class TextMatch(BaseModel):
    text: str
    start_index: int
    end_index: int

class SearchResult(BaseModel):
    matches: List[Dict[str, Any]]
    total_found: int

class DocumentItem(BaseModel):
    id: str
    name: str
    created_time: Optional[str] = None
    modified_time: Optional[str] = None
    web_view_link: Optional[str] = None

class DocumentList(BaseModel):
    items: List[DocumentItem]
    next_page_token: Optional[str] = None

class DocumentContent(BaseModel):
    id: str
    title: str
    url: Optional[str] = None
    revision_id: Optional[str] = None
    content: str
    structural_elements: Optional[List[Dict[str, Any]]] = None

# Request Schema
class GetDocumentParams(BaseModel):
    document_id: str

class CreateDocumentParams(BaseModel):
    title: str

class BatchUpdateParams(BaseModel):
    document_id: str
    requests: List[Dict[str, Any]]

class InsertTextParams(BaseModel):
    document_id: str
    location_index: int
    text: str

class ReplaceAllTextParams(BaseModel):
    document_id: str
    text_to_replace: str
    replace_text: str

class SearchTextParams(BaseModel):
    document_id: str
    search_term: str
    case_sensitive: Optional[bool] = False

class ListDocumentsParams(BaseModel):
    max_results: Optional[int] = 10
    page_token: Optional[str] = None

class GetDocumentContentParams(BaseModel):
    document_id: str

# Response Schema
class GetDocumentResponse(BaseModel):
    data: DocumentMetadata
    message: Optional[str] = None

class CreateDocumentResponse(BaseModel):
    data: DocumentMetadata
    message: Optional[str] = None

class BatchUpdateResponse(BaseModel):
    data: Dict[str, Any]
    message: Optional[str] = None

class InsertTextResponse(BaseModel):
    data: Dict[str, Any]
    message: Optional[str] = None

class ReplaceAllTextResponse(BaseModel):
    data: Dict[str, Any]
    message: Optional[str] = None

class SearchTextResponse(BaseModel):
    data: SearchResult
    message: Optional[str] = None

class ListDocumentsResponse(BaseModel):
    data: DocumentList
    message: Optional[str] = None

class GetDocumentContentResponse(BaseModel):
    data: DocumentContent
    message: Optional[str] = None

class ApiResponse(BaseModel):
    data: Union[
        DocumentMetadata,  
        DocumentContent,  
        Dict[str, Any],    
        SearchResult,      
        DocumentList       
    ]
    component: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None
