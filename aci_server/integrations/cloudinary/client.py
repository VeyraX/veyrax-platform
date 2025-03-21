import requests
import base64
import hashlib
import time
import os
import json
from typing import Dict, Any, Optional, List, Union
from urllib.parse import urlencode


class CloudinaryAPIError(Exception):
    def __init__(self, message, errors=None):
        self.message = message
        self.errors = errors
        super().__init__(self.message)


class CloudinaryClient:
    def __init__(self, cloud_name: str, api_key: str, api_secret: str):
        self.cloud_name = cloud_name
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = f"https://api.cloudinary.com/v1_1/{cloud_name}"
        self.auth = (api_key, api_secret)

    def _generate_signature(self, params: Dict[str, Any]) -> str:
        """
        Generate a signature according to Cloudinary's documentation:
        1. All parameters should be included except: file, cloud_name, resource_type and api_key
        2. Add the timestamp parameter
        3. Sort all parameters alphabetically
        4. Join the parameters as key=value pairs with &
        5. Append the API secret
        6. Generate SHA-1 hash
        """
        # Exclude the parameters that should not be part of the signature
        excluded_params = ["file", "cloud_name", "resource_type", "api_key"]
        params_to_sign = {k: v for k, v in params.items() if v is not None and k not in excluded_params}
        
        # Sort parameters by key
        params_list = []
        for key in sorted(params_to_sign.keys()):
            value = params_to_sign[key]
            # Convert boolean values to string
            if isinstance(value, bool):
                value = str(value).lower()
            # Convert numeric values to string
            elif isinstance(value, (int, float)):
                value = str(value)
            params_list.append(f"{key}={value}")
        
        # Join parameters into a signature string
        signature_string = "&".join(params_list)
        
        # Add the API secret to the end (without any separator)
        signature_string = f"{signature_string}{self.api_secret}"
        
        # Compute SHA-1 hash and return hexadecimal digest
        return hashlib.sha1(signature_string.encode('utf-8')).hexdigest()

    def _prepare_upload_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare parameters for upload, adding timestamp and signature if needed."""
        # Make a copy of the parameters to avoid modifying the original
        clean_params = {k: v for k, v in params.items() if v is not None}
        
        # Add cloud_name if not present
        if "cloud_name" not in clean_params:
            clean_params["cloud_name"] = self.cloud_name
        
        if "upload_preset" not in clean_params or not clean_params["upload_preset"]:
            # For signed uploads, add timestamp and api_key
            if "timestamp" not in clean_params:
                clean_params["timestamp"] = int(time.time())
            
            if "api_key" not in clean_params:
                clean_params["api_key"] = self.api_key

            # Generate the signature after setting timestamp and api_key
            clean_params["signature"] = self._generate_signature(clean_params)
        
        return clean_params

    def _handle_response(self, response):
        """Handle API response and parse errors if needed."""
        try:
            # Even if status code is not 2xx, try to parse the JSON
            data = response.json()
            
            # Check if the response contains an error
            if "error" in data:
                if isinstance(data["error"], dict) and "message" in data["error"]:
                    error_message = data["error"]["message"]
                else:
                    error_message = str(data["error"])
                raise CloudinaryAPIError(error_message, data)
            
            # If status code indicates an error but no "error" in JSON
            if not response.ok:
                response.raise_for_status()
                
            return data
        except json.JSONDecodeError:
            # If the response is not JSON, raise the HTTP error
            response.raise_for_status()
            raise CloudinaryAPIError(f"Invalid response: {response.text}")

    def upload(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Upload a file to Cloudinary from a URL."""
        resource_type = params.pop("resource_type", "image")
        url = f"{self.base_url}/{resource_type}/upload"
        
        # Make sure file parameter is a URL (string)
        if "file" not in params or not params["file"]:
            raise CloudinaryAPIError("Missing required parameter: file URL")
        
        # Prepare the upload parameters including signature
        upload_params = self._prepare_upload_params(params)
        
        try:
            # Send the upload request with the URL in the form data
            response = requests.post(url, data=upload_params)
            return self._handle_response(response)
        except CloudinaryAPIError:
            # Pass through our custom exception
            raise
        except Exception as e:
            # Wrap any other exceptions
            raise CloudinaryAPIError(f"Upload failed: {str(e)}")

    def explicit(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate derived transformations for an existing asset."""
        resource_type = params.pop("resource_type", "image")
        url = f"{self.base_url}/{resource_type}/explicit"
        
        # Fix for 'async' parameter which is a Python keyword
        if "async_" in params:
            params["async"] = params.pop("async_")
        
        try:
            upload_params = self._prepare_upload_params(params)
            response = requests.post(url, data=upload_params, auth=self.auth)
            return self._handle_response(response)
        except CloudinaryAPIError:
            # Pass through our custom exception
            raise
        except Exception as e:
            # Wrap any other exceptions
            raise CloudinaryAPIError(f"Explicit transformation failed: {str(e)}")

    def list_assets(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List assets (resources) in the Cloudinary account."""
        resource_type = params.pop("resource_type", "image")
        type_ = params.pop("type", "upload")
        url = f"{self.base_url}/resources/{resource_type}/{type_}"
        
        try:
            # Convert params to query params
            query_params = {k: v for k, v in params.items() if v is not None}
            response = requests.get(url, params=query_params, auth=self.auth)
            return self._handle_response(response)
        except CloudinaryAPIError:
            # Pass through our custom exception
            raise
        except Exception as e:
            # Wrap any other exceptions
            raise CloudinaryAPIError(f"List assets failed: {str(e)}")

    def get_asset_details(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get details for a specific asset."""
        resource_type = params.pop("resource_type", "image")
        type_ = params.pop("type", "upload")
        public_id = params.pop("public_id")
        
        url = f"{self.base_url}/resources/{resource_type}/{type_}/{public_id}"
        
        try:
            # Convert remaining params to query params
            query_params = {k: v for k, v in params.items() if v is not None}
            response = requests.get(url, params=query_params, auth=self.auth)
            return self._handle_response(response)
        except CloudinaryAPIError:
            # Pass through our custom exception
            raise
        except Exception as e:
            # Wrap any other exceptions
            raise CloudinaryAPIError(f"Get asset details failed: {str(e)}")

    def delete_asset(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete an asset."""
        resource_type = params.pop("resource_type", "image")
        url = f"{self.base_url}/{resource_type}/destroy"
        
        try:
            upload_params = self._prepare_upload_params(params)
            response = requests.post(url, data=upload_params, auth=self.auth)
            return self._handle_response(response)
        except CloudinaryAPIError:
            # Pass through our custom exception
            raise
        except Exception as e:
            # Wrap any other exceptions
            raise CloudinaryAPIError(f"Delete asset failed: {str(e)}")

    def rename_asset(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Rename an asset (change its public ID)."""
        resource_type = params.pop("resource_type", "image")
        url = f"{self.base_url}/{resource_type}/rename"
        
        try:
            upload_params = self._prepare_upload_params(params)
            response = requests.post(url, data=upload_params, auth=self.auth)
            return self._handle_response(response)
        except CloudinaryAPIError:
            # Pass through our custom exception
            raise
        except Exception as e:
            # Wrap any other exceptions
            raise CloudinaryAPIError(f"Rename asset failed: {str(e)}") 