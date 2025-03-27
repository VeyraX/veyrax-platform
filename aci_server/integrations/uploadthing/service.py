from typing import Dict, Any, Optional, List, Union
import os
import tempfile
from .client import UploadThingClient
from .schema import (
    ListFilesParams,
    FileList,
    PollUploadParams,
    PollUploadResult,
    GetServerCallbackParams,
    GetServerCallbackResult,
    SetServerCallbackParams,
    SetServerCallbackResult,
    PrepareUploadParams,
    PrepareUploadFields,
    PrepareUploadMultipart,
    FileToUpload,
    UploadFilesParams,
    FileDetails,
    UploadFromUrlParams,
    UploadFromUrlResponse,
    RenameFilesParams,
    RenameFilesResult,
    DeleteFilesParams,
    DeleteFilesResult,
    GetAppInfoParams,
    AppInfoResult,
    GetUsageInfoParams,
    UsageInfoResult,
    ApiResponse
)
from ..common.component_handler import load_components, prepare_components_auto
import requests
from urllib.parse import urlparse


class UploadThingService:
    def __init__(self, client: UploadThingClient):
        self.client = client
        self.components_data = self._load_components()
    
    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
    
    def prepare_response(self, data: Any, component_name: str = None) -> ApiResponse:
        tool_name = "uploadthing"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)
    
    def _prepare_list_files_params(self, params: ListFilesParams) -> Dict[str, Any]:
        """Prepare parameters for the list_files API call"""
        return {
            "limit": params.limit,
            "offset": params.offset
        }
    
    def list_files(self, params: ListFilesParams) -> ApiResponse:
        # Process parameters in the service layer
        payload = self._prepare_list_files_params(params)
        
        # Call the client with processed parameters
        response = self.client.list_files(payload)
        
        validated_data = FileList(**response)
        return self.prepare_response(validated_data, "UploadThingFileList")
    
    def poll_upload(self, params: PollUploadParams) -> ApiResponse:
        # Call the client to poll for the upload status
        response = self.client.poll_upload(params.fileKey)
        
        # Validate and process the response
        validated_data = PollUploadResult(**response)
        return self.prepare_response(validated_data, "UploadThingFileDetail")
    
    def get_server_callback(self, params: GetServerCallbackParams) -> ApiResponse:
        # Call the client to get server callback data
        response = self.client.get_server_callback(params.authorization)
        
        # Validate and process the response
        validated_data = GetServerCallbackResult(**response)
        return self.prepare_response(validated_data, "UploadThingCallbackStatus")
    
    def _prepare_server_callback_payload(self, params: SetServerCallbackParams) -> Dict[str, Any]:
        """Prepare payload for the set_server_callback API call"""
        return {
            "fileKey": params.fileKey,
            "callbackData": params.callbackData
        }
    
    def set_server_callback(self, params: SetServerCallbackParams) -> ApiResponse:
        # Prepare the payload
        payload = self._prepare_server_callback_payload(params)
        
        # Call the client to set server callback data
        response = self.client.set_server_callback(payload)
        
        # Validate and process the response
        validated_data = SetServerCallbackResult(**response)
        return self.prepare_response(validated_data, "UploadThingCallbackStatus")
    
    def _prepare_files_for_upload(self, files: List[FileToUpload]) -> List[Dict[str, Any]]:
        """Convert Pydantic models to dictionaries for the API call"""
        return [
            {
                "name": file.name,
                "size": file.size,
                "customId": file.customId
            }
            for file in files
        ]
    
    def _prepare_prepare_upload_payload(self, params: PrepareUploadParams) -> Dict[str, Any]:
        """Prepare payload for the prepare_upload API call"""
        files = self._prepare_files_for_upload(params.files)
        
        return {
            "callbackUrl": str(params.callbackUrl),
            "callbackSlug": params.callbackSlug,
            "files": files,
            "routeConfig": params.routeConfig,
            "metadata": params.metadata
        }
    
    def prepare_upload(self, params: PrepareUploadParams) -> ApiResponse:
        # Prepare the payload
        payload = self._prepare_prepare_upload_payload(params)
        
        # Call the client to prepare the upload
        response = self.client.prepare_upload(payload)
        
        # The response is a list of upload data objects which could be either
        # single-part or multi-part upload instructions
        validated_data = []
        for item in response:
            # Determine if this is a single-part or multi-part upload
            if "url" in item and "fields" in item:
                # Single-part upload
                validated_data.append(PrepareUploadFields(**item))
            elif "urls" in item and "uploadId" in item:
                # Multi-part upload
                validated_data.append(PrepareUploadMultipart(**item))
        
        return self.prepare_response(validated_data, "UploadThingPreparedUpload")
    
    def _prepare_file_details(self, files: List[FileDetails]) -> List[Dict[str, Any]]:
        """Convert FileDetails models to dictionaries for the API call"""
        return [
            {
                "name": file.name,
                "size": file.size,
                "type": file.type,
                "customId": file.customId
            }
            for file in files
        ]
    
    def _prepare_upload_files_payload(self, params: UploadFilesParams) -> Dict[str, Any]:
        """Prepare payload for the upload_files API call"""
        files = self._prepare_file_details(params.files)
        
        return {
            "files": files,
            "acl": params.acl,
            "metadata": params.metadata,
            "contentDisposition": params.contentDisposition
        }
    
    def upload_files(self, params: UploadFilesParams) -> ApiResponse:
        # Prepare the payload
        payload = self._prepare_upload_files_payload(params)
        
        # Call the client to upload the files
        response = self.client.upload_files(payload)
        
        # Extract the response data - it might be a list directly or nested in a 'data' field
        file_data = response
        if isinstance(response, dict) and "data" in response:
            file_data = response["data"]
        
        # Process the file data - could be single-part or multi-part uploads
        validated_data = []
        for item in file_data:
            # Determine if this is a single-part or multi-part upload
            if "url" in item and "fields" in item:
                # Single-part upload
                validated_data.append(PrepareUploadFields(**item))
            elif "urls" in item and "uploadId" in item:
                # Multi-part upload
                validated_data.append(PrepareUploadMultipart(**item))
        
        return self.prepare_response(validated_data, "UploadThingPreparedUpload") 
    
    def _get_file_params(self, path: str, custom_id: Optional[str] = None) -> Dict[str, Any]:
        # Get file info from path
        file_stats = os.stat(path)
        file_name = os.path.basename(path)
        
        # Determine file type from extension
        _, ext = os.path.splitext(file_name)
        file_type = ext.lstrip('.').lower() if ext else None
        
        # Prepare parameters
        params = {
            "name": file_name,
            "size": file_stats.st_size,
        }
        
        # Add customId if provided
        if custom_id is not None:
            params["customId"] = custom_id
            
        # Add type if available
        if file_type:
            params["type"] = file_type
            
        return params
    
    def _get_file_params_from_url(self, url: str, custom_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get file information from a URL and return parameters in the required format for UploadThing.
        
        Args:
            url: URL of the file
            custom_id: Optional custom identifier for the file
            
        Returns:
            Dictionary with file name, size, and optional customId and type
        """
        # Get file info from URL
        response = requests.head(url, allow_redirects=True)
        response.raise_for_status()
        
        # Extract file name from URL
        parsed_url = urlparse(url)
        file_name = os.path.basename(parsed_url.path)
        
        # Get file size from headers if available
        content_length = response.headers.get('Content-Length')
        file_size = int(content_length) if content_length else 0
        
        # Determine file type - first try content-type header
        file_type = None
        content_type = response.headers.get('Content-Type')
        if content_type and '/' in content_type:
            # Extract subtype from content-type (e.g., 'image/jpeg' -> 'jpeg')
            file_type = content_type.split('/')[-1]
        
        # If no content-type or it's generic, try file extension
        if not file_type or file_type in ['octet-stream', 'binary']:
            _, ext = os.path.splitext(file_name)
            if ext:
                file_type = ext.lstrip('.').lower()
        
        # Prepare parameters
        params = {
            "name": file_name,
            "size": file_size,
        }
        
        # Add customId if provided
        if custom_id is not None:
            params["customId"] = custom_id
            
        # Add type if available
        if file_type:
            params["type"] = file_type
            
        return params
        
    def upload_from_url(self, params: UploadFromUrlParams) -> ApiResponse:
        # Get file parameters from URL
        file_params = self._get_file_params_from_url(str(params.url), params.customId)
        
        # Create FileToUpload object
        file_to_upload = FileToUpload(
            name=file_params["name"],
            size=file_params["size"],
            customId=params.customId
        )
        
        # Create PrepareUploadParams
        prepare_params = PrepareUploadParams(
            callbackUrl=params.callbackUrl,
            callbackSlug=params.callbackSlug,
            files=[file_to_upload],
            routeConfig=params.routeConfig,
            metadata=params.metadata
        )
        
        # Prepare the upload
        prepare_response = self.prepare_upload(prepare_params)
        
        # Download the file from URL to a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            try:
                response = requests.get(str(params.url), stream=True)
                response.raise_for_status()
                
                # Write the file content to a temporary file
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        temp_file.write(chunk)
                
                temp_file.flush()
                
                # Upload each prepared file
                for upload_data in prepare_response.data:
                    if hasattr(upload_data, "url") and hasattr(upload_data, "fields"):
                        # Single-part upload
                        upload_url = upload_data.url
                        fields = upload_data.fields
                        
                        with open(temp_file.name, "rb") as f:
                            files = {
                                "file": (fields["key"], f, fields.get("Content-Type", "application/octet-stream"))
                            }
                            upload_response = requests.post(upload_url, data=fields, files=files)
                            upload_response.raise_for_status()
                    elif hasattr(upload_data, "urls") and hasattr(upload_data, "uploadId"):
                        # Multi-part upload not implemented yet
                        raise NotImplementedError("Multi-part upload from URL is not supported yet")
            finally:
                # Clean up the temporary file
                try:
                    os.unlink(temp_file.name)
                except Exception:
                    pass
        
        return prepare_response
    
    def _prepare_rename_files_payload(self, params: RenameFilesParams) -> Dict[str, Any]:
        """Prepare the payload for the rename_files API call"""
        updates = []
        for update in params.updates:
            updates.append({
                "fileKey": update.fileKey,
                "newName": update.newName
            })
        
        return {
            "updates": updates
        }
    
    def rename_files(self, params: RenameFilesParams) -> ApiResponse:
        """Rename multiple files in UploadThing"""
        # Prepare the payload
        payload = self._prepare_rename_files_payload(params)
        
        # Call the client to rename files
        response = self.client.rename_files(payload)
        
        # Validate the response
        validated_data = RenameFilesResult(**response)
        
        # Return the API response
        return self.prepare_response(validated_data, "UploadThingRenameResult")
    
    def _prepare_delete_files_payload(self, params: DeleteFilesParams) -> Dict[str, Any]:
        """Prepare the payload for the delete_files API call"""
        payload = {}
        
        if params.fileKeys:
            payload["fileKeys"] = params.fileKeys
        
        if params.customIds:
            payload["customIds"] = params.customIds
        
        return payload
    
    def delete_files(self, params: DeleteFilesParams) -> ApiResponse:
        """Delete multiple files in UploadThing"""
        # Prepare the payload
        payload = self._prepare_delete_files_payload(params)
        
        # Call the client to delete files
        response = self.client.delete_files(payload)
        
        # Validate the response
        validated_data = DeleteFilesResult(**response)
        
        # Return the API response
        return self.prepare_response(validated_data, "UploadThingDeleteResult")
    
    def get_app_info(self) -> ApiResponse:
        """Get app information from UploadThing"""
        # Call the client to get app info
        response = self.client.get_app_info()
        
        # Validate the response
        validated_data = AppInfoResult(**response)
        
        # Return the API response
        return self.prepare_response(validated_data, "UploadThingAppInfo")
    
    def get_usage_info(self) -> ApiResponse:
        """Get usage information from UploadThing"""
        # Call the client to get usage info
        response = self.client.get_usage_info()
        
        # Validate the response
        validated_data = UsageInfoResult(**response)
        
        # Return the API response
        return self.prepare_response(validated_data, "UploadThingUsageInfo")