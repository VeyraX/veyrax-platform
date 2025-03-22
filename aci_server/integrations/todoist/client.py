import requests
from typing import Dict, Any, List, Optional
import uuid

class TodoistClient:
    BASE_URL = "https://api.todoist.com/rest/v2"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def get_projects(self) -> List[Dict[str, Any]]:
        """Get all projects"""
        response = requests.get(
            f"{self.BASE_URL}/projects",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def create_project(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new project"""
        headers = {**self.headers, "X-Request-Id": str(uuid.uuid4())}
        response = requests.post(
            f"{self.BASE_URL}/projects",
            headers=headers,
            json=params
        )
        response.raise_for_status()
        return response.json()
    
    def get_project(self, project_id: str) -> Dict[str, Any]:
        """Get a specific project by ID"""
        response = requests.get(
            f"{self.BASE_URL}/projects/{project_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def update_project(self, project_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update a project"""
        headers = {**self.headers, "X-Request-Id": str(uuid.uuid4())}
        response = requests.post(
            f"{self.BASE_URL}/projects/{project_id}",
            headers=headers,
            json=params
        )
        response.raise_for_status()
        return response.json()
    
    def delete_project(self, project_id: str) -> bool:
        """Delete a project"""
        response = requests.delete(
            f"{self.BASE_URL}/projects/{project_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return True
    
    def get_collaborators(self, project_id: str) -> List[Dict[str, Any]]:
        """Get all collaborators of a shared project"""
        response = requests.get(
            f"{self.BASE_URL}/projects/{project_id}/collaborators",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_sections(self, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all sections, optionally filtered by project"""
        url = f"{self.BASE_URL}/sections"
        params = {}
        if project_id:
            params["project_id"] = project_id
        
        response = requests.get(
            url,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()

    def get_section(self, section_id: str) -> Dict[str, Any]:
        """Get a specific section by ID"""
        response = requests.get(
            f"{self.BASE_URL}/sections/{section_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def create_section(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new section"""
        headers = {**self.headers, "X-Request-Id": str(uuid.uuid4())}
        response = requests.post(
            f"{self.BASE_URL}/sections",
            headers=headers,
            json=params
        )
        response.raise_for_status()
        return response.json()

    def update_section(self, section_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update a section"""
        headers = {**self.headers, "X-Request-Id": str(uuid.uuid4())}
        response = requests.post(
            f"{self.BASE_URL}/sections/{section_id}",
            headers=headers,
            json=params
        )
        response.raise_for_status()
        return response.json()

    def delete_section(self, section_id: str) -> bool:
        """Delete a section"""
        response = requests.delete(
            f"{self.BASE_URL}/sections/{section_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return True

    def get_tasks(self, project_id: Optional[str] = None, section_id: Optional[str] = None, 
                  label: Optional[str] = None, filter_str: Optional[str] = None, 
                  lang: Optional[str] = None, ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Get tasks, with optional filtering"""
        url = f"{self.BASE_URL}/tasks"
        params = {}
        
        if project_id:
            params["project_id"] = project_id
        if section_id:
            params["section_id"] = section_id
        if label:
            params["label"] = label
        if filter_str:
            params["filter"] = filter_str
        if lang:
            params["lang"] = lang
        if ids:
            params["ids"] = ",".join(ids)
        
        response = requests.get(
            url,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()

    def create_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new task"""
        headers = {**self.headers, "X-Request-Id": str(uuid.uuid4())}
        response = requests.post(
            f"{self.BASE_URL}/tasks",
            headers=headers,
            json=params
        )
        response.raise_for_status()
        return response.json()

    def get_task(self, task_id: str) -> Dict[str, Any]:
        """Get a specific task by ID"""
        response = requests.get(
            f"{self.BASE_URL}/tasks/{task_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def update_task(self, task_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update a task"""
        headers = {**self.headers, "X-Request-Id": str(uuid.uuid4())}
        response = requests.post(
            f"{self.BASE_URL}/tasks/{task_id}",
            headers=headers,
            json=params
        )
        response.raise_for_status()
        return response.json()

    def close_task(self, task_id: str) -> bool:
        """Close a task (mark as complete)"""
        response = requests.post(
            f"{self.BASE_URL}/tasks/{task_id}/close",
            headers=self.headers
        )
        response.raise_for_status()
        return True

    def reopen_task(self, task_id: str) -> bool:
        """Reopen a task (mark as incomplete)"""
        response = requests.post(
            f"{self.BASE_URL}/tasks/{task_id}/reopen",
            headers=self.headers
        )
        response.raise_for_status()
        return True

    def delete_task(self, task_id: str) -> bool:
        """Delete a task"""
        response = requests.delete(
            f"{self.BASE_URL}/tasks/{task_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return True

    def get_comments(self, task_id: Optional[str] = None, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all comments for a task or project"""
        url = f"{self.BASE_URL}/comments"
        params = {}
        
        if task_id:
            params["task_id"] = task_id
        if project_id:
            params["project_id"] = project_id
        
        if not task_id and not project_id:
            raise ValueError("Either task_id or project_id must be provided")
        
        response = requests.get(
            url,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()

    def create_comment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new comment"""
        headers = {**self.headers, "X-Request-Id": str(uuid.uuid4())}
        response = requests.post(
            f"{self.BASE_URL}/comments",
            headers=headers,
            json=params
        )
        response.raise_for_status()
        return response.json()

    def get_comment(self, comment_id: str) -> Dict[str, Any]:
        """Get a specific comment by ID"""
        response = requests.get(
            f"{self.BASE_URL}/comments/{comment_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def update_comment(self, comment_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update a comment"""
        headers = {**self.headers, "X-Request-Id": str(uuid.uuid4())}
        response = requests.post(
            f"{self.BASE_URL}/comments/{comment_id}",
            headers=headers,
            json=params
        )
        response.raise_for_status()
        return response.json()

    def delete_comment(self, comment_id: str) -> bool:
        """Delete a comment"""
        response = requests.delete(
            f"{self.BASE_URL}/comments/{comment_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return True

    def get_personal_labels(self) -> List[Dict[str, Any]]:
        """Get all personal labels"""
        response = requests.get(
            f"{self.BASE_URL}/labels",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def create_personal_label(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new personal label"""
        headers = {**self.headers, "X-Request-Id": str(uuid.uuid4())}
        response = requests.post(
            f"{self.BASE_URL}/labels",
            headers=headers,
            json=params
        )
        response.raise_for_status()
        return response.json()

    def get_personal_label(self, label_id: str) -> Dict[str, Any]:
        """Get a specific personal label by ID"""
        response = requests.get(
            f"{self.BASE_URL}/labels/{label_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def update_personal_label(self, label_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update a personal label"""
        headers = {**self.headers, "X-Request-Id": str(uuid.uuid4())}
        response = requests.post(
            f"{self.BASE_URL}/labels/{label_id}",
            headers=headers,
            json=params
        )
        response.raise_for_status()
        return response.json()

    def delete_personal_label(self, label_id: str) -> bool:
        """Delete a personal label"""
        response = requests.delete(
            f"{self.BASE_URL}/labels/{label_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return True

    def get_shared_labels(self, omit_personal: bool = False) -> List[str]:
        """Get all shared labels"""
        url = f"{self.BASE_URL}/labels/shared"
        params = {}
        if omit_personal:
            params["omit_personal"] = "true"
        
        response = requests.get(
            url,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()

    def rename_shared_label(self, name: str, new_name: str) -> bool:
        """Rename a shared label"""
        headers = {**self.headers, "X-Request-Id": str(uuid.uuid4())}
        response = requests.post(
            f"{self.BASE_URL}/labels/shared/rename",
            headers=headers,
            json={"name": name, "new_name": new_name}
        )
        response.raise_for_status()
        return True

    def remove_shared_label(self, name: str) -> bool:
        """Remove a shared label"""
        headers = {**self.headers, "X-Request-Id": str(uuid.uuid4())}
        response = requests.post(
            f"{self.BASE_URL}/labels/shared/remove",
            headers=headers,
            json={"name": name}
        )
        response.raise_for_status()
        return True
