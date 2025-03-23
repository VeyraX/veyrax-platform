from typing import Optional, Dict, Any, List, Union
from .client import GoogleDocsClient
from .schema import (
    DocumentMetadata, 
    SearchResult, 
    DocumentList,
    DocumentItem,
    ApiResponse,
    DocumentContent
)
import os
from ..common.component_handler import load_components, prepare_components_auto

class GoogleDocsService:
    def __init__(self, client: GoogleDocsClient):
        self.client = client
        self.components_data = self._load_components()

    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
        
    def prepare_response(self, data: Any, component_name: str = None) -> ApiResponse:
        tool_name = "google_docs"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)

    def get_document(self, document_id: str) -> ApiResponse:
        document_data = self.client.get_document(document_id)
        
        metadata = DocumentMetadata(
            id=document_data['documentId'],
            title=document_data['title'],
            url=f"https://docs.google.com/document/d/{document_data['documentId']}",
            revision_id=document_data.get('revisionId')
        )
        
        return self.prepare_response(metadata, "GoogleDocsDocumentCard")
    
    def create_document(self, title: str) -> ApiResponse:
        document_data = self.client.create_document(title)
        
        metadata = DocumentMetadata(
            id=document_data['documentId'],
            title=document_data['title'],
            url=f"https://docs.google.com/document/d/{document_data['documentId']}",
            revision_id=document_data.get('revisionId')
        )
        
        return self.prepare_response(metadata, "GoogleDocsDocumentCard")
    
    def batch_update(self, document_id: str, requests: List[Dict[str, Any]]) -> ApiResponse:
        response = self.client.batch_update(document_id, requests)
        
        return self.prepare_response(response, "GoogleDocsUpdateResult")
    
    def insert_text(self, document_id: str, location_index: int, text: str) -> ApiResponse:
        response = self.client.insert_text(document_id, location_index, text)
        
        return self.prepare_response(response, "GoogleDocsUpdateResult")
    
    def replace_all_text(self, document_id: str, text_to_replace: str, replace_text: str) -> ApiResponse:
        response = self.client.replace_all_text(document_id, text_to_replace, replace_text)
        
        return self.prepare_response(response, "GoogleDocsUpdateResult")
    
    def search_text(self, document_id: str, search_term: str, case_sensitive: bool = False) -> ApiResponse:
        response = self.client.search_text(document_id, search_term, case_sensitive)
        
        result = SearchResult(
            matches=response.get('matches', []),
            total_found=response.get('total_found', 0)
        )
        
        return self.prepare_response(result, "GoogleDocsSearchResult")
    
    def get_document_content(self, document_id: str) -> ApiResponse:
        document_data = self.client.get_document_content(document_id)
        
        content = DocumentContent(
            id=document_data['documentId'],
            title=document_data['title'],
            url=f"https://docs.google.com/document/d/{document_data['documentId']}",
            revision_id=document_data.get('revisionId'),
            content=document_data.get('extractedContent', ''),
            structural_elements=document_data.get('body', {}).get('content', [])
        )
        
        return self.prepare_response(content, "GoogleDocsContentViewer")