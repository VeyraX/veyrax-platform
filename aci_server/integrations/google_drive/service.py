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
        
        query_parts.append("mimeType != 'application/vnd.google-apps.folder'")
        
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
            if filters.folders_only:
                query_parts = ["mimeType = 'application/vnd.google-apps.folder'"]

        q = ' and '.join(query_parts)
        page_size = filters.max_results if filters and filters.max_results else 20
        response = self.client.list_files(pageToken=page_token, q=q, pageSize=page_size)
        
        files_data = response.get('files', [])
        
        parent_names_map = {}
        all_parent_ids = set()
        for file in files_data:
            if file.get('parents'):
                all_parent_ids.update(file['parents'])
        
        if all_parent_ids:
            for parent_id in all_parent_ids:
                try:
                    parent = self.client.get_file(parent_id)
                    parent_names_map[parent_id] = parent['name']
                except Exception:
                    parent_names_map[parent_id] = None
        
        files = [
            DriveFile(
                id=file['id'],
                name=file['name'],
                mime_type=file['mimeType'],
                parent_ids=file.get('parents'),
                parent_names=[parent_names_map.get(p) for p in file.get('parents', [])] if file.get('parents') else None,
                created_time=parser.parse(file['createdTime']),
                modified_time=parser.parse(file['modifiedTime']),
                size=file.get('size'),
                web_view_link=file.get('webViewLink'),
                web_content_link=file.get('webContentLink')
            )
            for file in files_data
        ]
        
        return FileList(
            files=files,
            page_token=response.get('nextPageToken')
        )

    def get_file(self, file_id: str) -> DriveFile:
        file = self.client.get_file(file_id)
        
        parent_names = None
        if file.get('parents'):
            parent_names = []
            for parent_id in file['parents']:
                try:
                    parent = self.client.get_file(parent_id)
                    parent_names.append(parent['name'])
                except Exception:
                    parent_names.append(None)
        
        return DriveFile(
            id=file['id'],
            name=file['name'],
            mime_type=file['mimeType'],
            parent_ids=file.get('parents'),
            parent_names=parent_names,
            created_time=parser.parse(file['createdTime']),
            modified_time=parser.parse(file['modifiedTime']),
            size=file.get('size'),
            web_view_link=file.get('webViewLink'),
            web_content_link=file.get('webContentLink')
        )

    def create_folder(self, name: str, parent_id: Optional[str] = None) -> DriveFile:
        folder = self.client.create_folder(name, parent_id)
        return self.get_file(folder['id'])

    def upload_file(self, name: str, file_content: IO, mime_type: str, parent_id: Optional[str] = None) -> DriveFile:
        file = self.client.upload_file(name, file_content, mime_type, parent_id)
        return self.get_file(file['id'])

    def download_file(self, file_id: str) -> tuple[IO, str]:
        file = self.get_file(file_id)
        mime_type = file.mime_type
        
        if mime_type in self.GOOGLE_MIME_TYPES:
            export_mime_type = self.GOOGLE_MIME_TYPES[mime_type]
            file_content = self.client.download_file(file_id, export_mime_type)
            return file_content, export_mime_type
        else:
            file_content = self.client.download_file(file_id)
            return file_content, mime_type

    def delete_file(self, file_id: str) -> None:
        self.client.delete_file(file_id)

    def move_file(self, file_id: str, new_parent_id: str) -> DriveFile:
        self.client.move_file(file_id, new_parent_id)
        return self.get_file(file_id)

    GOOGLE_MIME_TYPES = {
        'application/vnd.google-apps.document': 'application/pdf',
        'application/vnd.google-apps.spreadsheet': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.google-apps.presentation': 'application/pdf',
        'application/vnd.google-apps.drawing': 'application/pdf',
    }