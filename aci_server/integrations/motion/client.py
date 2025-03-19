import requests
from typing import Dict, Any, Optional, List

class MotionClient:
    BASE_URL = "https://api.usemotion.com/v1"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def create_comment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new comment on a task"""
        response = requests.post(
            f"{self.BASE_URL}/comments",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()

    def get_comments(self, task_id: str, cursor: Optional[str] = None) -> Dict[str, Any]:
        """Get all comments for a task"""
        params = {"taskId": task_id}
        if cursor:
            params["cursor"] = cursor
            
        response = requests.get(
            f"{self.BASE_URL}/comments",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()

    def create_project(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new project"""
        response = requests.post(
            f"{self.BASE_URL}/projects",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()

    def get_project(self, project_id: str) -> Dict[str, Any]:
        """Get a single project by ID"""
        response = requests.get(
            f"{self.BASE_URL}/projects/{project_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def list_projects(self, workspace_id: Optional[str] = None, cursor: Optional[str] = None) -> Dict[str, Any]:
        """List all projects for a workspace"""
        params = {}
        if workspace_id:
            params["workspaceId"] = workspace_id
        if cursor:
            params["cursor"] = cursor
            
        response = requests.get(
            f"{self.BASE_URL}/projects",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
        
    def create_recurring_task(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new recurring task"""
        response = requests.post(
            f"{self.BASE_URL}/recurring-tasks",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
        
    def delete_recurring_task(self, task_id: str) -> Dict[str, Any]:
        """Delete a recurring task by ID"""
        response = requests.delete(
            f"{self.BASE_URL}/recurring-tasks/{task_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json() if response.content else {"success": True}
        
    def list_recurring_tasks(self, workspace_id: str, cursor: Optional[str] = None) -> Dict[str, Any]:
        """List all recurring tasks for a workspace"""
        params = {"workspaceId": workspace_id}
        if cursor:
            params["cursor"] = cursor
            
        response = requests.get(
            f"{self.BASE_URL}/recurring-tasks",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()

    def get_schedules(self) -> List[Dict[str, Any]]:
        """Get all schedules for the authenticated user"""
        response = requests.get(
            f"{self.BASE_URL}/schedules",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
        
    def get_statuses(self, workspace_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get a list of statuses for a workspace"""
        params = {}
        if workspace_id:
            params["workspaceId"] = workspace_id
            
        response = requests.get(
            f"{self.BASE_URL}/statuses",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
        
    def list_users(self, team_id: Optional[str] = None, workspace_id: Optional[str] = None, cursor: Optional[str] = None) -> Dict[str, Any]:
        """Get a list of users for a team or workspace"""
        params = {}
        if team_id:
            params["teamId"] = team_id
        if workspace_id:
            params["workspaceId"] = workspace_id
        if cursor:
            params["cursor"] = cursor
            
        response = requests.get(
            f"{self.BASE_URL}/users",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
        
    def get_my_user(self) -> Dict[str, Any]:
        """Get information about the authenticated user"""
        response = requests.get(
            f"{self.BASE_URL}/users/me",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
        
    def list_workspaces(self, ids: Optional[List[str]] = None, cursor: Optional[str] = None) -> Dict[str, Any]:
        """Get a list of workspaces the user is part of"""
        params = {}
        if ids:
            params["ids"] = ",".join(ids)
        if cursor:
            params["cursor"] = cursor
            
        response = requests.get(
            f"{self.BASE_URL}/workspaces",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()

    def create_task(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new task"""
        response = requests.post(
            f"{self.BASE_URL}/tasks",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
        
    def delete_task(self, task_id: str) -> Dict[str, Any]:
        """Delete a task by ID"""
        response = requests.delete(
            f"{self.BASE_URL}/tasks/{task_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json() if response.content else {"success": True}
        
    def get_task(self, task_id: str) -> Dict[str, Any]:
        """Get a task by ID"""
        response = requests.get(
            f"{self.BASE_URL}/tasks/{task_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
        
    def list_tasks(self, 
                  assignee_id: Optional[str] = None,
                  cursor: Optional[str] = None,
                  include_all_statuses: Optional[bool] = None,
                  label: Optional[str] = None,
                  name: Optional[str] = None,
                  project_id: Optional[str] = None,
                  status: Optional[List[str]] = None,
                  workspace_id: Optional[str] = None) -> Dict[str, Any]:
        """List tasks based on query parameters"""
        params = {}
        if assignee_id:
            params["assigneeId"] = assignee_id
        if cursor:
            params["cursor"] = cursor
        if include_all_statuses is not None:
            params["includeAllStatuses"] = str(include_all_statuses).lower()
        if label:
            params["label"] = label
        if name:
            params["name"] = name
        if project_id:
            params["projectId"] = project_id
        if status:
            params["status"] = status
        if workspace_id:
            params["workspaceId"] = workspace_id
            
        response = requests.get(
            f"{self.BASE_URL}/tasks",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
        
    def move_task(self, task_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Move a task to a different workspace"""
        response = requests.patch(
            f"{self.BASE_URL}/tasks/{task_id}/move",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
        
    def unassign_task(self, task_id: str) -> Dict[str, Any]:
        """Remove the assignee of a task"""
        response = requests.delete(
            f"{self.BASE_URL}/tasks/{task_id}/assignee",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json() if response.content else {"success": True}
        
    def update_task(self, task_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a task"""
        response = requests.patch(
            f"{self.BASE_URL}/tasks/{task_id}",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()