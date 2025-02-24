from datetime import datetime
from typing import Optional, List, Tuple, BinaryIO
from .client import DropboxClient
from .schema import DropboxFile, FileList, FileFilters

class DropboxService:
    def __init__(self, access_token: str):
        self.client = DropboxClient(access_token)

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
            shared_link=None  # Требуется отдельный запрос для получения shared_link
        )

    def list_files(self, filters: FileFilters) -> FileList:
        response = self.client.list_files(
            path=filters.path,
            recursive=filters.recursive,
            limit=filters.limit
        )
        
        files = [
            self._convert_to_dropbox_file(entry) 
            for entry in response.get("entries", [])
        ]
        
        return FileList(
            files=files,
            cursor=response.get("cursor"),
            has_more=response.get("has_more", False)
        )

    def get_file(self, path: str) -> DropboxFile:
        file_data = self.client.get_file_metadata(path)
        return self._convert_to_dropbox_file(file_data)

    def create_folder(self, path: str) -> DropboxFile:
        response = self.client.create_folder(path)
        return self._convert_to_dropbox_file(response["metadata"])

    def upload_file(self, path: str, file: BinaryIO, mode: str = "add") -> DropboxFile:
        response = self.client.upload_file(path, file, mode)
        return self._convert_to_dropbox_file(response)

    def download_file(self, path: str) -> Tuple[bytes, DropboxFile]:
        content, metadata = self.client.download_file(path)
        return content, self._convert_to_dropbox_file(metadata)

    def delete_file(self, path: str) -> DropboxFile:
        response = self.client.delete_file(path)
        return self._convert_to_dropbox_file(response["metadata"])

    def move_file(self, from_path: str, to_path: str) -> DropboxFile:
        try:
            response = self.client.move_file(from_path, to_path)
            if "metadata" not in response:
                print(f"Unexpected response structure: {response}")
                return self._convert_to_dropbox_file(response)
            return self._convert_to_dropbox_file(response["metadata"])
        except Exception as e:
            print(f"Move file error: {str(e)}")
            raise