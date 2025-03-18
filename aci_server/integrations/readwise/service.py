from typing import Dict, Any, List, Optional
from .client import ReadwiseClient
from .schema import (
    SaveDocumentParams,
    ListDocumentsParams,
    UpdateDocumentParams,
    DeleteDocumentParams,
    DocumentResponse,
    DocumentListResponse,
    ApiResponse
)
import os
from ..common.component_handler import load_components, prepare_components_auto

class ReadwiseService:
    def __init__(self, client: ReadwiseClient):
        self.client = client
        self.components_data = self._load_components()

    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
        
    def prepare_response(self, data: Any, component_name: str = None) -> ApiResponse:
        tool_name = "readwise"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)

    def validate_token(self) -> bool:
        return self.client.validate_token()

    def save_document(self, params: SaveDocumentParams) -> ApiResponse:
        processed_params = self._process_save_params(params)
        response = self.client.save_document(processed_params)
        validated = DocumentResponse(**response)
        return self.prepare_response(validated, "ReadwiseDocumentCard")

    def list_documents(self, params: ListDocumentsParams) -> ApiResponse:
        processed_params = self._process_list_params(params)
        response = self.client.list_documents(processed_params)
        validated = DocumentListResponse(**response)
        return self.prepare_response(validated, "ReadwiseDocumentListCard")

    def update_document(self, document_id: str, params: UpdateDocumentParams) -> ApiResponse:
        processed_params = self._process_update_params(params)
        response = self.client.update_document(document_id, processed_params)
        validated = DocumentResponse(**response)
        return self.prepare_response(validated, "ReadwiseDocumentCard")

    def delete_document(self, document_id: str) -> ApiResponse:
        self.client.delete_document(document_id)
        return ApiResponse(data={"success": True, "message": "Document deleted successfully"})

    def _process_save_params(self, params: SaveDocumentParams) -> Dict[str, Any]:
        return params.model_dump(exclude_none=True)

    def _process_list_params(self, params: ListDocumentsParams) -> Dict[str, Any]:
        return params.model_dump(exclude_none=True)

    def _process_update_params(self, params: UpdateDocumentParams) -> Dict[str, Any]:
        return params.model_dump(exclude_none=True)
