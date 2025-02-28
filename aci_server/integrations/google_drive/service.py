from typing import Optional, IO, Union, Dict, Any, List
from .client import DriveClient
from .schema import FileList, DriveFile, FileFilters, ApiResponse, PermissionType, PermissionRole, PermissionResponse
from datetime import datetime
from dateutil import parser
import os
from ..common.component_handler import load_components, prepare_components_auto
import base64
import aiohttp
from io import BytesIO
from fastapi import HTTPException
import tempfile
import requests

class DriveService:
    def __init__(self, client: DriveClient):
        self.client = client
        self.components_data = self._load_components()

    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
        
    def prepare_response(self, data: Union[DriveFile, FileList], component_name: str = None) -> ApiResponse:
        tool_name = "google-drive"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)

    def _prepare_file_data(self, file_data: Dict[str, Any]) -> Dict[str, Any]:
        prepared_data = {
            'id': file_data['id'],
            'name': file_data['name'],
            'mime_type': file_data['mimeType'],
            'parent_ids': file_data.get('parents'),
            'created_time': parser.parse(file_data['createdTime']),
            'modified_time': parser.parse(file_data['modifiedTime']),
            'size': file_data.get('size'),
            'web_view_link': file_data.get('webViewLink'),
            'web_content_link': file_data.get('webContentLink')
        }
        
        if file_data.get('parents'):
            parent_names = []
            for parent_id in file_data['parents']:
                try:
                    parent = self.client.get_file(parent_id)
                    parent_names.append(parent['name'])
                except Exception:
                    parent_names.append(None)
            prepared_data['parent_names'] = parent_names
        
        return prepared_data

    def list_files(self, page_token: Optional[str] = None, filters: Optional[FileFilters] = None) -> ApiResponse:
        query_parts = []
        
        if filters and filters.folders_only:
            query_parts.append("mimeType = 'application/vnd.google-apps.folder'")
        else:
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
        
        files = []
        for file_data in files_data:
            prepared_data = self._prepare_file_data(file_data)
            
            if file_data.get('parents'):
                prepared_data['parent_names'] = [parent_names_map.get(p) for p in file_data.get('parents', [])]
            
            files.append(DriveFile(**prepared_data))
        
        files_list = FileList(
            files=files,
            page_token=response.get('nextPageToken')
        )
        
        return self.prepare_response(files_list, "GoogleDriveFileCard")

    def get_file(self, file_id: str) -> ApiResponse:
        file_data = self.client.get_file(file_id)
        prepared_data = self._prepare_file_data(file_data)
        file = DriveFile(**prepared_data)
        return self.prepare_response(file, "GoogleDriveFileCard")

    def get_file_with_component(self, file_id: str) -> ApiResponse:
        file = self.get_file(file_id)
        return self.prepare_response(file, "GoogleDriveFileCard")

    def create_folder(self, name: str, parent_id: Optional[str] = None) -> ApiResponse:
        folder_data = self.client.create_folder(name, parent_id)
        folder_obj = self.get_file(folder_data['id']).data
        return self.prepare_response(folder_obj, "GoogleDriveFileCard")

    def upload_file(self, name: str, file_content: IO, mime_type: str, parent_id: Optional[str] = None) -> ApiResponse:
        file_data = self.client.upload_file(name, file_content, mime_type, parent_id)
        file_obj = self.get_file(file_data['id']).data
        return self.prepare_response(file_obj, "GoogleDriveFileCard")

    def download_file(self, file_id: str) -> tuple[IO, str]:
        file = self.get_file(file_id).data
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

    def move_file(self, file_id: str, new_parent_id: str) -> ApiResponse:
        self.client.move_file(file_id, new_parent_id)
        file_obj = self.get_file(file_id).data
        return self.prepare_response(file_obj, "GoogleDriveFileCard")

    def download_file_with_metadata(self, file_id: str):
        file_content, mime_type = self.download_file(file_id)
        file_info = self.get_file(file_id).data
        
        file_content.seek(0)
        file_bytes = file_content.read()
        
        # Encode binary data for JSON response
        base64_content = base64.b64encode(file_bytes).decode('utf-8')
        
        # Get extension from mapping or try to extract from original filename
        extension = self.GOOGLE_MIME_TYPE_EXTENSIONS.get(
            mime_type, 
            os.path.splitext(file_info.name)[1]  # Fallback to original extension
        )
        
        filename = f"{file_info.name}{extension}"
        
        return {
            "status": "success",
            "file_content": base64_content,  # Now a base64 string
            "mime_type": mime_type,
            "filename": filename
        }

    def read_file_content(self, file_id: str):
        from ..common.file_reader import read_file_content
        
        file_content, mime_type = self.download_file(file_id)
        file_info = self.get_file(file_id).data
        
        if any(x in mime_type for x in ['spreadsheet', 'excel', 'csv']):
            return {
                "success": False,
                "error": "Spreadsheet files are not supported for text reading",
                "file": file_info.dict()
            }
        
        text_content, success = read_file_content(file_content, mime_type)
        
        return {
            "success": success,
            "content": text_content,
            "file": file_info.dict(),
            "mime_type": mime_type
        }

    async def upload_file_from_url(self, file_url, filename, parent_id=None):
        """Download file from URL and upload to Google Drive"""
        try:
            # Download file from URL
            response = requests.get(file_url, stream=True)
            response.raise_for_status()  # Raise an exception for HTTP errors
            
            # Get content type from response headers
            content_type = response.headers.get('Content-Type', 'application/octet-stream')
            
            # Create a BytesIO object from the response content
            file_obj = BytesIO(response.content)
            
            # Make sure we're at the beginning of the file
            file_obj.seek(0)
            
            # Upload the file and get its data
            file_data = self.client.upload_file(
                name=filename,
                file_content=file_obj,
                mime_type=content_type,
                parent_id=parent_id
            )
            
            # Get the complete file object and prepare a proper response
            file_obj = self.get_file(file_data['id']).data
            
            # Return a properly formatted response
            return self.prepare_response(file_obj, "GoogleDriveFileCard")
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=400, detail=f"Failed to upload file from URL: {str(e)}")

    async def upload_file_from_base64(self, filename, file_base64, content_type, parent_id=None):
        """Decode base64 file and upload to Google Drive"""
        try:
            # Remove data URL prefix if present
            if ',' in file_base64:
                file_base64 = file_base64.split(',', 1)[1]
            
            # Clean any whitespace that might be present in the base64 string
            file_base64 = file_base64.strip()
            
            # Decode base64 to binary
            file_content = base64.b64decode(file_base64)
            
            # Create a BytesIO object
            file_obj = BytesIO(file_content)
            
            # Make sure we're at the beginning of the file
            file_obj.seek(0)
            
            # Upload the file and get its data
            file_data = self.client.upload_file(
                name=filename,
                file_content=file_obj,
                mime_type=content_type,
                parent_id=parent_id
            )
            
            # Get the complete file object and prepare a proper response
            file_obj = self.get_file(file_data['id']).data
            
            # Return a properly formatted response
            return self.prepare_response(file_obj, "GoogleDriveFileCard")
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=400, detail=f"Failed to decode base64 file: {str(e)}")

    def set_permission(self, file_id: str, permission: Dict[str, Any]) -> ApiResponse:
        try:
            perm_type = PermissionType(permission['type'])
            perm_role = PermissionRole(permission['role'])
            
            # Build base permission
            permission_body = {
                'type': perm_type.value,
                'role': perm_role.value
            }
            
            # Add type-specific fields
            extra_params = {}
            if perm_type in [PermissionType.USER, PermissionType.GROUP]:
                permission_body['emailAddress'] = permission['email']
                extra_params['emailMessage'] = permission.get('email_message')
            elif perm_type == PermissionType.DOMAIN:
                permission_body['domain'] = permission['domain']
            
            # Create the permission
            created_perm = self.client.create_permission(
                file_id=file_id,
                permission={**permission_body, **extra_params}
            )
            
            # Convert to PermissionResponse
            perm_response = PermissionResponse(
                id=created_perm['id'],
                role=PermissionRole(created_perm['role']),
                type=PermissionType(created_perm['type']),
                email_address=created_perm.get('emailAddress')
            )
            
            return self.prepare_response(perm_response, "GoogleDrivePermissionCard")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Permission setting failed: {str(e)}")

    def list_permissions(self, file_id: str) -> ApiResponse:
        try:
            permissions = self.client.list_permissions(file_id)
            perm_responses = [
                PermissionResponse(
                    id=p['id'],
                    role=PermissionRole(p['role']),
                    type=PermissionType(p['type']),
                    email_address=p.get('emailAddress')
                ) for p in permissions
            ]
            return self.prepare_response(perm_responses, "GoogleDrivePermissionList")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to list permissions: {str(e)}")

    def delete_permission(self, file_id: str, permission_id: str) -> None:
        try:
            self.client.delete_permission(file_id, permission_id)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Permission deletion failed: {str(e)}")

    def copy_file(self, file_id: str, name: Optional[str] = None, parent_id: Optional[str] = None) -> ApiResponse:
        try:
            file_data = self.client.copy_file(file_id, name, parent_id)
            file_obj = DriveFile(
                id=file_data['id'],
                name=file_data['name'],
                mime_type=file_data['mimeType'],
                parent_ids=file_data.get('parents'),
                created_time=parser.parse(file_data['createdTime']),
                modified_time=parser.parse(file_data['modifiedTime']),
                size=file_data.get('size'),
                web_view_link=file_data.get('webViewLink'),
                web_content_link=file_data.get('webContentLink')
            )
            return self.prepare_response(file_obj, "GoogleDriveFileCard")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to copy file: {str(e)}")

    GOOGLE_MIME_TYPES = {
        'application/vnd.google-apps.document': 'application/pdf',
        'application/vnd.google-apps.spreadsheet': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.google-apps.presentation': 'application/pdf',
        'application/vnd.google-apps.drawing': 'application/pdf',
    }

    # Add this class-level constant
    GOOGLE_MIME_TYPE_EXTENSIONS = {
        # Documents
        'application/pdf': '.pdf',
        'application/msword': '.doc',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
        'application/vnd.oasis.opendocument.text': '.odt',
        'text/plain': '.txt',
        
        # Spreadsheets
        'application/vnd.ms-excel': '.xls',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
        'application/vnd.oasis.opendocument.spreadsheet': '.ods',
        'text/csv': '.csv',
        
        # Presentations
        'application/vnd.ms-powerpoint': '.ppt',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation': '.pptx',
        'application/vnd.oasis.opendocument.presentation': '.odp',
        
        # Images
        'image/jpeg': '.jpg',
        'image/png': '.png',
        'image/gif': '.gif',
        'image/tiff': '.tiff',
        'image/svg+xml': '.svg',
        'image/webp': '.webp',
        
        # Audio/Video
        'audio/mpeg': '.mp3',
        'audio/wav': '.wav',
        'video/mp4': '.mp4',
        'video/quicktime': '.mov',
        
        # Archives
        'application/zip': '.zip',
        'application/x-tar': '.tar',
        'application/x-gzip': '.gz',
        
        # Google Workspace
        'application/vnd.google-apps.document': '.gdoc',
        'application/vnd.google-apps.spreadsheet': '.gsheet',
        'application/vnd.google-apps.presentation': '.gslides',
        
        # Other
        'application/json': '.json',
        'application/octet-stream': '.bin'
    }