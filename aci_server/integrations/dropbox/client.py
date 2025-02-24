import requests
from typing import Optional, Dict, Any, IO
import json

class DropboxClient:
    BASE_URL = "https://api.dropboxapi.com/2"
    CONTENT_URL = "https://content.dropboxapi.com/2"

    def __init__(self, access_token: str):
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

    def list_files(self, path: str = "", **kwargs) -> Dict[str, Any]:
        endpoint = f"{self.BASE_URL}/files/list_folder"
        data = {
            "path": path,
            "recursive": False,
            "include_media_info": False,
            "include_deleted": False,
            "include_has_explicit_shared_members": False,
            **kwargs
        }
        
        response = requests.post(endpoint, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

    def get_file_metadata(self, path: str) -> Dict[str, Any]:
        endpoint = f"{self.BASE_URL}/files/get_metadata"
        path = f"/{path.strip('/')}"
        data = {"path": path}
        
        response = requests.post(endpoint, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

    def create_folder(self, path: str) -> Dict[str, Any]:
        endpoint = f"{self.BASE_URL}/files/create_folder_v2"
        data = {"path": path}
        
        response = requests.post(endpoint, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

    def upload_file(self, path: str, file_content: IO, mode: str = "add") -> Dict[str, Any]:
        endpoint = f"{self.CONTENT_URL}/files/upload"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Dropbox-API-Arg": json.dumps({
                "path": path,
                "mode": mode,
                "autorename": True
            }),
            "Content-Type": "application/octet-stream"
        }
        
        response = requests.post(endpoint, headers=headers, data=file_content)
        response.raise_for_status()
        return response.json()

    def download_file(self, path: str) -> tuple[bytes, Dict[str, Any]]:
        endpoint = f"{self.CONTENT_URL}/files/download"
        path = f"/{path.strip('/')}"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Dropbox-API-Arg": json.dumps({"path": path})
        }
        
        response = requests.post(endpoint, headers=headers)
        response.raise_for_status()
        
        metadata = json.loads(response.headers["Dropbox-API-Result"])
        return response.content, metadata

    def delete_file(self, path: str) -> Dict[str, Any]:
        endpoint = f"{self.BASE_URL}/files/delete_v2"
        data = {"path": path}
        
        response = requests.post(endpoint, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

    def move_file(self, from_path: str, to_path: str) -> Dict[str, Any]:
        endpoint = f"{self.BASE_URL}/files/move_v2"
        data = {
            "from_path": from_path,
            "to_path": to_path,
            "allow_shared_folder": True,
            "autorename": False,
            "allow_ownership_transfer": False
        }
        
        try:
            response = requests.post(endpoint, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Dropbox API Error: {str(e)}")
            if hasattr(e.response, 'json'):
                print(f"Response: {e.response.json()}")
            raise