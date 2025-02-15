from typing import Optional, IO
from .client import DriveClient
from .schema import FileList, DriveFile, FileFilters
from datetime import datetime
from dateutil import parser

class DriveService:
    def __init__(self, client: DriveClient):
        self.client = client

    def list_files(self, page_token: Optional[str] = None, filters: Optional[FileFilters] = None) -> FileList:
        query_parts = []
        
        if filters:
            if filters.name_contains:
                query_parts.append(f"name contains '{filters.name_contains}'")
            if filters.mime_type:
                query_parts.append(f"mimeType = '{filters.mime_type}'")
            if filters.parent_id:
                query_parts.append(f"'{filters.parent_id}' in parents")
            if filters.created_after:
                after_date = datetime.fromisoformat(filters.created_after).isoformat('T')
                query_parts.append(f"createdTime > '{after_date}'")
            if filters.created_before:
                before_date = datetime.fromisoformat(filters.created_before).isoformat('T')
                query_parts.append(f"createdTime < '{before_date}'")

        q = ' and '.join(query_parts) if query_parts else None
        response = self.client.list_files(pageToken=page_token, q=q, pageSize=20)
        
        files = [
            DriveFile(
                id=file['id'],
                name=file['name'],
                mime_type=file['mimeType'],
                parent_ids=file.get('parents'),
                created_time=parser.parse(file['createdTime']),
                modified_time=parser.parse(file['modifiedTime']),
                size=file.get('size')
            )
            for file in response.get('files', [])
        ]
        
        return FileList(
            files=files,
            page_token=response.get('nextPageToken')
        )

    def get_file(self, file_id: str) -> DriveFile:
        file = self.client.get_file(file_id)
        return DriveFile(
            id=file['id'],
            name=file['name'],
            mime_type=file['mimeType'],
            parent_ids=file.get('parents'),
            created_time=parser.parse(file['createdTime']),
            modified_time=parser.parse(file['modifiedTime']),
            size=file.get('size')
        )

    def create_folder(self, name: str, parent_id: Optional[str] = None) -> DriveFile:
        folder = self.client.create_folder(name, parent_id)
        return self.get_file(folder['id'])

    def upload_file(self, name: str, file_content: IO, mime_type: str, parent_id: Optional[str] = None) -> DriveFile:
        file = self.client.upload_file(name, file_content, mime_type, parent_id)
        return self.get_file(file['id'])

    def download_file(self, file_id: str) -> IO:
        return self.client.download_file(file_id)

    def delete_file(self, file_id: str) -> None:
        self.client.delete_file(file_id)

    def move_file(self, file_id: str, new_parent_id: str) -> DriveFile:
        self.client.move_file(file_id, new_parent_id)
        return self.get_file(file_id)