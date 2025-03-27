import requests
from typing import Dict, Any, Optional, List
import os


class UploadThingClient:
    BASE_URL = "https://api.uploadthing.com"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "x-uploadthing-api-key": api_key
        }
    
    def list_files(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Low-level API call to list files"""
        response = requests.post(
            f"{self.BASE_URL}/v6/listFiles",
            headers=self.headers,
            json=payload
        )
        
        response.raise_for_status()
        return response.json()
    
    def poll_upload(self, file_key: str) -> Dict[str, Any]:
        """Low-level API call to poll for upload completion status"""
        response = requests.get(
            f"{self.BASE_URL}/v6/pollUpload/{file_key}",
            headers=self.headers
        )
        
        response.raise_for_status()
        return response.json()
    
    def get_server_callback(self, auth_token: str) -> Dict[str, Any]:
        """Low-level API call to get server callback data"""
        headers = {**self.headers, "Authorization": auth_token}
        response = requests.get(
            f"{self.BASE_URL}/v6/serverCallback",
            headers=headers
        )
        
        response.raise_for_status()
        return response.json()
    
    def set_server_callback(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Low-level API call to set server callback data"""
        response = requests.post(
            f"{self.BASE_URL}/v6/serverCallback",
            headers=self.headers,
            json=payload
        )
        
        response.raise_for_status()
        return response.json()
    
    def prepare_upload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Low-level API call to prepare uploads and get presigned URLs"""
        response = requests.post(
            f"{self.BASE_URL}/v6/prepareUpload",
            headers=self.headers,
            json=payload
        )
        
        response.raise_for_status()
        return response.json()
    
    
    def upload_files(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Low-level API call to upload files directly without a file route"""
        response = requests.post(
            f"{self.BASE_URL}/v6/uploadFiles",
            headers=self.headers,
            json=payload
        )
        
        response.raise_for_status()
        return response.json()
    
    def rename_files(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Low-level API call to rename files"""
        response = requests.post(
            f"{self.BASE_URL}/v6/renameFiles",
            headers=self.headers,
            json=payload
        )
        
        response.raise_for_status()
        return response.json()
    
    def delete_files(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Low-level API call to delete files"""
        response = requests.post(
            f"{self.BASE_URL}/v6/deleteFiles",
            headers=self.headers,
            json=payload
        )
        
        response.raise_for_status()
        return response.json()
    
    def get_app_info(self) -> Dict[str, Any]:
        """Low-level API call to get app info"""
        response = requests.post(
            f"{self.BASE_URL}/v7/getAppInfo",
            headers=self.headers
        )
        
        response.raise_for_status()
        return response.json()
    
    def get_usage_info(self) -> Dict[str, Any]:
        """Low-level API call to get usage info"""
        response = requests.post(
            f"{self.BASE_URL}/v6/getUsageInfo",
            headers=self.headers
        )
        
        response.raise_for_status()
        return response.json()
    
    def test_connection(self) -> bool:
        """Test the API connection using a minimal limit value"""
        try:
            self.list_files({"limit": 1})
            return True
        except Exception:
            return False 