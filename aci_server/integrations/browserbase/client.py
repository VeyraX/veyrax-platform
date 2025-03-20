import requests
from typing import Dict, Any, Optional

class BrowserBaseClient:
    BASE_URL = "https://api.browserbase.com/v1"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "X-BB-API-Key": api_key
        }
    
    def get_session(self, session_id: str) -> Dict[str, Any]:
        """Get details about a specific session"""
        response = requests.get(
            f"{self.BASE_URL}/sessions/{session_id}", 
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def create_session(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new browser session"""
        response = requests.post(
            f"{self.BASE_URL}/sessions", 
            headers=self.headers,
            json=params
        )
        response.raise_for_status()
        return response.json()
    
    def update_session(self, session_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update a session's status"""
        response = requests.put(
            f"{self.BASE_URL}/sessions/{session_id}", 
            headers=self.headers,
            json=params
        )
        response.raise_for_status()
        return response.json()
    
    def list_sessions(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """List all sessions with optional filtering"""
        response = requests.get(
            f"{self.BASE_URL}/sessions", 
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def get_context(self, context_id: str) -> Dict[str, Any]:
        """Get details about a specific context"""
        response = requests.get(
            f"{self.BASE_URL}/contexts/{context_id}", 
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def create_context(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new browser context"""
        response = requests.post(
            f"{self.BASE_URL}/contexts", 
            headers=self.headers,
            json=params
        )
        response.raise_for_status()
        return response.json()
    
    def delete_context(self, context_id: str) -> None:
        """Delete a browser context"""
        response = requests.delete(
            f"{self.BASE_URL}/contexts/{context_id}", 
            headers=self.headers
        )
        response.raise_for_status()
        return None
    
    def get_session_logs(self, session_id: str) -> Dict[str, Any]:
        """Get logs for a specific session"""
        response = requests.get(
            f"{self.BASE_URL}/sessions/{session_id}/logs", 
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_session_recording(self, session_id: str) -> Dict[str, Any]:
        """Get recording data for a specific session"""
        response = requests.get(
            f"{self.BASE_URL}/sessions/{session_id}/recording", 
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_session_debug(self, session_id: str) -> Dict[str, Any]:
        """Get debug information for a specific session"""
        response = requests.get(
            f"{self.BASE_URL}/sessions/{session_id}/debug", 
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_session_downloads(self, session_id: str) -> Dict[str, Any]:
        """Download data from a specific session"""
        response = requests.get(
            f"{self.BASE_URL}/sessions/{session_id}/downloads", 
            headers=self.headers
        )
        response.raise_for_status()
        
        return {
            "status_code": response.status_code,
            "content_type": response.headers.get("Content-Type", "application/octet-stream"),
            "file": response.content
        }
    
    def create_session_uploads(self, session_id: str, file_content: str) -> Dict[str, Any]:
        """Upload a file to a specific session"""
        response = requests.post(
            f"{self.BASE_URL}/sessions/{session_id}/uploads", 
            headers=self.headers,
            data=file_content
        )
        response.raise_for_status()
        return response.json()
    
    def list_projects(self) -> Dict[str, Any]:
        """List all projects for the authenticated user"""
        response = requests.get(
            f"{self.BASE_URL}/projects", 
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_project(self, project_id: str) -> Dict[str, Any]:
        """Get details about a specific project"""
        response = requests.get(
            f"{self.BASE_URL}/projects/{project_id}", 
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_project_usage(self, project_id: str) -> Dict[str, Any]:
        """Get usage statistics for a specific project"""
        response = requests.get(
            f"{self.BASE_URL}/projects/{project_id}/usage", 
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_extension(self, extension_id: str) -> Dict[str, Any]:
        """Get details about a specific extension"""
        response = requests.get(
            f"{self.BASE_URL}/extensions/{extension_id}", 
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def delete_extension(self, extension_id: str) -> None:
        """Delete an extension"""
        response = requests.delete(
            f"{self.BASE_URL}/extensions/{extension_id}", 
            headers=self.headers
        )
        response.raise_for_status()
        return None
    
    def upload_extension(self, file_content: str, project_id: Optional[str] = None) -> Dict[str, Any]:
        """Upload an extension"""
        headers = self.headers.copy()
        if project_id:
            headers["X-Project-ID"] = project_id
        
        files = {'file': file_content}
        response = requests.post(
            f"{self.BASE_URL}/extensions", 
            headers=headers,
            files=files
        )
        response.raise_for_status()
        return response.json()