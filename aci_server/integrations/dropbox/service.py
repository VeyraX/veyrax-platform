from datetime import datetime
from typing import Optional, List, Tuple, BinaryIO, Union, Dict, Any
from .client import DropboxClient
from .schema import DropboxFile, FileList, FileFilters, ApiResponse
import os
from ..common.component_handler import load_components, prepare_components_auto

class DropboxService:
    def __init__(self, access_token: str):
        self.client = DropboxClient(access_token)
        self.components_data = self._load_components()

    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
        
    def prepare_response(self, data: Union[DropboxFile, FileList], component_name: str = None) -> ApiResponse:
        tool_name = "dropbox"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)

    def _convert_to_dropbox_file(self, file_data: dict) -> DropboxFile:
        return DropboxFile(
            id=file_data.get(".tag", "") + ":" + file_data.get("id", ""),
            name=file_data.get("name", ""),
            path_display=file_data.get("path_display", ""),
            path_lower=file_data.get("path_lower", ""),
            mime_type=file_data.get("mime_type"),
            size=file_data.get("size"),
            is_folder=file_data.get(".tag") == "folder",
            created_time=datetime.fromisoformat(file_data.get("client_modified", "1970-01-01T00:00:00Z").replace("Z", "+00:00")),
            modified_time=datetime.fromisoformat(file_data.get("server_modified", "1970-01-01T00:00:00Z").replace("Z", "+00:00")),
            shared_link=None 
        )

    def list_files(self, filters: FileFilters) -> ApiResponse:
        response = self.client.list_files(
            path=filters.path,
            recursive=filters.recursive,
            limit=filters.limit
        )
        
        files = [
            self._convert_to_dropbox_file(entry) 
            for entry in response.get("entries", [])
        ]
        
        file_list = FileList(
            files=files,
            cursor=response.get("cursor"),
            has_more=response.get("has_more", False)
        )
        
        return self.prepare_response(file_list, "DropboxFileCard")

    def get_file(self, path: str) -> ApiResponse:
        file_data = self.client.get_file_metadata(path)
        file = self._convert_to_dropbox_file(file_data)
        return self.prepare_response(file, "DropboxFileCard")

    def create_folder(self, path: str) -> ApiResponse:
        response = self.client.create_folder(path)
        file = self._convert_to_dropbox_file(response["metadata"])
        return self.prepare_response(file, "DropboxFileCard")

    def upload_file(self, path: str, file: BinaryIO, mode: str = "add") -> ApiResponse:
        response = self.client.upload_file(path, file, mode)
        file = self._convert_to_dropbox_file(response)
        return self.prepare_response(file, "DropboxFileCard")

    def download_file(self, path: str) -> Tuple[bytes, DropboxFile]:
        try:
            content, metadata = self.client.download_file(path)
            dropbox_file = self._convert_to_dropbox_file(metadata)
            return content, dropbox_file
        except Exception as e:
            print(f"Download error in service: {str(e)}")
            raise

    def delete_file(self, path: str) -> ApiResponse:
        response = self.client.delete_file(path)
        file = self._convert_to_dropbox_file(response["metadata"])
        return self.prepare_response(file, "DropboxFileCard")

    def move_file(self, from_path: str, to_path: str) -> ApiResponse:
        try:
            response = self.client.move_file(from_path, to_path)
            if "metadata" not in response:
                print(f"Unexpected response structure: {response}")
                file = self._convert_to_dropbox_file(response)
            else:
                file = self._convert_to_dropbox_file(response["metadata"])
            return self.prepare_response(file, "DropboxFileCard")
        except Exception as e:
            print(f"Move file error: {str(e)}")
            raise