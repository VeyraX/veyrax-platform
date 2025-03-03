from datetime import datetime
from typing import Optional, List, Tuple, BinaryIO, Union, Dict, Any
from .client import DropboxClient
from .schema import DropboxFile, FileList, FileFilters, ApiResponse, SearchResult
import os
from ..common.component_handler import load_components, prepare_components_auto
import base64
from ..common.file_reader import read_file_content
from ..common.file_utils import get_mime_type_from_extension

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

    def _convert_to_dropbox_file(self, file_data: dict, is_folder: bool = False) -> DropboxFile:
        mime_type = file_data.get("mime_type")
        if not mime_type and not is_folder and file_data.get("name"):
            mime_type = get_mime_type_from_extension(file_data.get("name", ""))

        return DropboxFile(
            id=file_data.get(".tag", "") + ":" + file_data.get("id", ""),
            name=file_data.get("name", ""),
            path_display=file_data.get("path_display", ""),
            path_lower=file_data.get("path_lower", ""),
            mime_type=mime_type,
            size=file_data.get("size"),
            is_folder=is_folder or (file_data.get(".tag") == "folder"),
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

    def create_folder(self, path: str, autorename: bool = False) -> ApiResponse:
        response = self.client.create_folder(path, autorename)
        file = self._convert_to_dropbox_file(response["metadata"], True)
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

    def upload_file_b64(self, path: str, file_content_b64: str, mode: str = "add") -> ApiResponse:
        file_content = base64.b64decode(file_content_b64)
        return self.upload_file(path, file_content, mode)

    def download_file_b64(self, path: str):
        clean_path = '/' + '/'.join(filter(None, path.split('/')))
        content, metadata = self.download_file(clean_path)
        
        filename = metadata.name if hasattr(metadata, 'name') else "download"
        mime_type = metadata.mime_type if hasattr(metadata, 'mime_type') else "application/octet-stream"
        
        content_b64 = base64.b64encode(content).decode('utf-8')
        
        return {
            "status": "success",
            "data": {
                "file_content": content_b64,
                "mime_type": mime_type,
                "filename": filename,
                "file_info": metadata.dict()
            }
        }

    def read_file_content(self, path: str):
        content, file_info = self.download_file(path)
        mime_type = file_info.mime_type
        
        if any(x in (mime_type or "") for x in ['spreadsheet', 'excel', 'csv']):
            return {
                "success": False,
                "error": "Spreadsheet files are not supported for text reading",
                "data": {
                    "file": file_info.dict()
                }
            }
    
        text_content, success = read_file_content(content, mime_type)
        
        return {
            "success": success,
            "data": {
                "content": text_content,
                "file": file_info.dict(),
                "mime_type": mime_type
            }
        }

    def create_shared_link(self, path: str, settings: Optional[Dict[str, Any]] = None) -> ApiResponse:
        try:
            response = self.client.create_shared_link(path, settings)
            
            # Extract the URL from the response
            shared_url = response.get("url")
            
            # Create a DropboxFile object with the shared link
            file = self._convert_to_dropbox_file(response)
            
            # Add the shared link to the file object
            file.shared_link = shared_url
            
            return self.prepare_response(file, "DropboxFileCard")
        except Exception as e:
            print(f"Create shared link error: {str(e)}")
            # If the link already exists, try to extract the existing link
            if "shared_link_already_exists" in str(e) and hasattr(e, "response"):
                try:
                    error_data = e.response.json().get("error", {})
                    if ".tag" in error_data and error_data[".tag"] == "shared_link_already_exists":
                        existing_metadata = error_data.get("metadata", {})
                        file = self._convert_to_dropbox_file(existing_metadata)
                        file.shared_link = existing_metadata.get("url")
                        return self.prepare_response(file, "DropboxFileCard")
                except:
                    pass
            raise

    def search_files(self, query: str, path: str = "", max_results: int = 20, 
                    filename_only: bool = False, file_status: str = "active") -> ApiResponse:
        """
        Search for files and folders in Dropbox.
        
        Args:
            query: The string to search for
            path: The path in the user's Dropbox to search
            max_results: Maximum number of results to return
            filename_only: Whether to search only the filename
            file_status: Filter results by file status
            
        Returns:
            ApiResponse containing search results
        """
        try:
            response = self.client.search_files(
                query=query,
                path=path,
                max_results=max_results,
                filename_only=filename_only,
                file_status=file_status
            )
            
            # Extract files from the matches
            files = []
            for match in response.get("matches", []):
                metadata = match.get("metadata", {}).get("metadata", {})
                if metadata:
                    files.append(self._convert_to_dropbox_file(metadata))
            
            # Create a SearchResult object
            search_result = SearchResult(
                files=files,
                cursor=response.get("cursor"),
                has_more=response.get("has_more", False)
            )
            
            return self.prepare_response(search_result, "DropboxFileList")
        except Exception as e:
            print(f"Search files error: {str(e)}")
            raise
    
    def search_continue(self, cursor: str) -> ApiResponse:
        """
        Continue a search with the cursor from a previous search.
        
        Args:
            cursor: The cursor returned from a previous search
            
        Returns:
            ApiResponse containing the next page of search results
        """
        try:
            response = self.client.search_continue(cursor)
            
            # Extract files from the matches
            files = []
            for match in response.get("matches", []):
                metadata = match.get("metadata", {}).get("metadata", {})
                if metadata:
                    files.append(self._convert_to_dropbox_file(metadata))
            
            # Create a SearchResult object
            search_result = SearchResult(
                files=files,
                cursor=response.get("cursor"),
                has_more=response.get("has_more", False)
            )
            
            return self.prepare_response(search_result, "DropboxFileList")
        except Exception as e:
            print(f"Search continue error: {str(e)}")
            raise