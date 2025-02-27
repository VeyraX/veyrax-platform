from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload, MediaIoBaseUpload
from typing import Optional, Dict, Any, IO, List
import io

class DriveClient:
    def __init__(self, credentials: Credentials):
        self.credentials = credentials
        self.service = build('drive', 'v3', credentials=credentials)

    def list_files(self, **kwargs) -> Dict[str, Any]:
        return self.service.files().list(
            fields="nextPageToken, files(id, name, mimeType, parents, createdTime, modifiedTime, size, webViewLink, webContentLink)",
            **kwargs
        ).execute()

    def get_file(self, file_id: str) -> Dict[str, Any]:
        return self.service.files().get(
            fileId=file_id,
            fields="id, name, mimeType, parents, createdTime, modifiedTime, size, webViewLink, webContentLink"
        ).execute()

    def create_folder(self, name: str, parent_id: Optional[str] = None) -> Dict[str, Any]:
        file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_id:
            file_metadata['parents'] = [parent_id]
        
        return self.service.files().create(
            body=file_metadata,
            fields='id, name, mimeType, parents'
        ).execute()

    def upload_file(self, name: str, file_content: IO, mime_type: str, parent_id: Optional[str] = None) -> Dict[str, Any]:
        file_metadata = {'name': name}
        if parent_id:
            file_metadata['parents'] = [parent_id]

        media = MediaIoBaseUpload(
            file_content,
            mimetype=mime_type,
            resumable=True
        )
        
        return self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, mimeType, parents, size'
        ).execute()

    def download_file(self, file_id: str, mime_type: Optional[str] = None) -> IO:
        file_content = io.BytesIO()
        
        if mime_type:
            request = self.service.files().export_media(
                fileId=file_id,
                mimeType=mime_type
            )
        else:
            request = self.service.files().get_media(fileId=file_id)
            
        downloader = MediaIoBaseDownload(file_content, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
        return file_content

    def delete_file(self, file_id: str) -> None:
        self.service.files().delete(
            fileId=file_id,
            supportsAllDrives=True
        ).execute()

    def move_file(self, file_id: str, new_parent_id: str) -> Dict[str, Any]:
        try:
            file = self.service.files().get(
                fileId=file_id,
                fields='parents,permissions',
                supportsAllDrives=True
            ).execute()
            
            previous_parents = file.get('parents', [])
            
            if not any(p.get('role') in ['owner', 'writer'] for p in file.get('permissions', [])):
                raise PermissionError(f"No write access for file {file_id}")

            params = {
                'fileId': file_id,
                'fields': 'id, name, mimeType, parents, createdTime, modifiedTime, size',
                'supportsAllDrives': True,
                'addParents': new_parent_id,
                'removeParents': ','.join(previous_parents) if previous_parents else None
            }

            if not previous_parents:
                del params['removeParents']
                params['body'] = {'parents': [new_parent_id]}

            return self.service.files().update(**params).execute()

        except Exception as e:
            if "cannotAddParent" in str(e):
                raise Exception("Domain policy prevents adding parents. Verify Google Workspace settings.")
            raise

    def read_file(self, file_id: str) -> tuple[bytes, str]:
        file = self.service.files().get(fileId=file_id, fields='mimeType').execute()
        mime_type = file.get('mimeType', '')
        
        request = self.service.files().get_media(fileId=file_id)
        file_content = request.execute()
        
        return file_content, mime_type

    def create_permission(self, file_id: str, permission: Dict[str, Any]) -> Dict[str, Any]:
        # Extract notification parameters only if they exist
        email_message = permission.pop('emailMessage', None)
        
        # Prepare optional parameters
        optional_params = {}
        # if send_notification is not None:
        #     optional_params['sendEmailNotification'] = send_notification
        if email_message is not None:
            optional_params['emailMessage'] = email_message
        
        return self.service.permissions().create(
            fileId=file_id,
            body=permission,
            fields='id,role,type,emailAddress',
            **optional_params
        ).execute()

    def list_permissions(self, file_id: str) -> List[Dict[str, Any]]:
        response = self.service.permissions().list(
            fileId=file_id,
            fields='permissions(id,role,type,emailAddress)'
        ).execute()
        return response.get('permissions', [])

    def delete_permission(self, file_id: str, permission_id: str) -> None:
        self.service.permissions().delete(
            fileId=file_id,
            permissionId=permission_id
        ).execute()

    def copy_file(self, file_id: str, name: Optional[str] = None, parent_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a copy of a file.
        
        Args:
            file_id: The ID of the file to copy
            name: Optional new name for the copy
            parent_id: Optional ID of the parent folder for the copy
            
        Returns:
            Dict containing the copied file's metadata
        """
        body = {}
        if name:
            body['name'] = name
        if parent_id:
            body['parents'] = [parent_id]
        
        return self.service.files().copy(
            fileId=file_id,
            body=body,
            fields='id, name, mimeType, parents, createdTime, modifiedTime, size, webViewLink, webContentLink',
            supportsAllDrives=True
        ).execute()