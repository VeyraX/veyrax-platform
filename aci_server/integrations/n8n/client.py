import requests
from typing import Dict, Any, Optional, List, Union

class N8nClient:
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url + "/api/v1"
        self.headers = {
            "X-N8N-API-KEY": api_key,
            "Content-Type": "application/json"
        }
    
    # Users endpoints
    def list_users(self, cursor: Optional[str] = None) -> Dict[str, Any]:
        params = {}
        if cursor:
            params["cursor"] = cursor
            
        response = requests.get(
            f"{self.base_url}/users",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def get_user(self, user_id: str) -> Dict[str, Any]:
        """Get a user by ID"""
        response = requests.get(
            f"{self.base_url}/users/{user_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def create_users(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create multiple users"""
        response = requests.post(
            f"{self.base_url}/users",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def delete_user(self, user_id: str) -> Dict[str, Any]:
        """Delete a user by ID"""
        response = requests.delete(
            f"{self.base_url}/users/{user_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return {"success": True} if not response.content else response.json()
    
    def update_user_role(self, user_id: str, role: str) -> Dict[str, Any]:
        """Update a user's global role"""
        response = requests.patch(
            f"{self.base_url}/users/{user_id}/role",
            headers=self.headers,
            json={"newRoleName": role}
        )
        response.raise_for_status()
        return response.json()
    
    # Executions endpoints
    def list_executions(self, cursor: Optional[str] = None, workflow_id: Optional[Union[int, str]] = None) -> Dict[str, Any]:
        """Get all executions"""
        params = {}
        if cursor:
            params["cursor"] = cursor
        if workflow_id:
            params["workflowId"] = workflow_id
            
        response = requests.get(
            f"{self.base_url}/executions",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def get_execution(self, execution_id: Union[int, str]) -> Dict[str, Any]:
        """Get an execution by ID"""
        response = requests.get(
            f"{self.base_url}/executions/{execution_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def delete_execution(self, execution_id: Union[int, str]) -> Dict[str, Any]:
        """Delete an execution by ID"""
        response = requests.delete(
            f"{self.base_url}/executions/{execution_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return {"success": True} if not response.content else response.json()

    # Workflow endpoints
    def list_workflows(self, cursor: Optional[str] = None, tags: Optional[List[str]] = None, active: Optional[bool] = None) -> Dict[str, Any]:
        """Get all workflows"""
        params = {}
        if cursor:
            params["cursor"] = cursor
        if tags:
            params["tags"] = ",".join(tags)
        if active is not None:
            params["active"] = str(active).lower()
            
        response = requests.get(
            f"{self.base_url}/workflows",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def get_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Get a workflow by ID"""
        response = requests.get(
            f"{self.base_url}/workflows/{workflow_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def create_workflow(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new workflow"""
        response = requests.post(
            f"{self.base_url}/workflows",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def update_workflow(self, workflow_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a workflow"""
        response = requests.put(
            f"{self.base_url}/workflows/{workflow_id}",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def delete_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Delete a workflow by ID"""
        response = requests.delete(
            f"{self.base_url}/workflows/{workflow_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return {"success": True} if not response.content else response.json()
    
    def activate_workflow(self, workflow_id: str, active: bool) -> Dict[str, Any]:
        """Activate or deactivate a workflow using the activate endpoint"""
        data = {"active": active}
        response = requests.post(
            f"{self.base_url}/workflows/{workflow_id}/activate",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def deactivate_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Deactivate a workflow using the dedicated deactivate endpoint"""
        response = requests.post(
            f"{self.base_url}/workflows/{workflow_id}/deactivate",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def copy_workflow(self, workflow_id: str, destination_project_id: Optional[str] = None) -> Dict[str, Any]:
        """Copy a workflow"""
        data = {}
        if destination_project_id:
            data["destinationProjectId"] = destination_project_id
            
        response = requests.post(
            f"{self.base_url}/workflows/{workflow_id}/copy",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def list_tags(self) -> List[Dict[str, Any]]:
        """Get all workflow tags"""
        response = requests.get(
            f"{self.base_url}/tags",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    # Credential endpoints
    def list_credentials(self, cursor: Optional[str] = None, cred_type: Optional[str] = None) -> Dict[str, Any]:
        """Get all credentials"""
        params = {}
        if cursor:
            params["cursor"] = cursor
        if cred_type:
            params["type"] = cred_type
            
        response = requests.get(
            f"{self.base_url}/credentials",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def create_credential(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new credential"""
        response = requests.post(
            f"{self.base_url}/credentials",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def delete_credential(self, credential_id: str) -> Dict[str, Any]:
        """Delete a credential by ID"""
        response = requests.delete(
            f"{self.base_url}/credentials/{credential_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return {"success": True} if not response.content else response.json()
    
    def get_credential_type(self, cred_type: str) -> Dict[str, Any]:
        """Get credential type schema"""
        response = requests.get(
            f"{self.base_url}/credentials/schema/{cred_type}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    # Tag endpoints (extending existing tag functions)
    def create_tag(self, name: str) -> Dict[str, Any]:
        """Create a new tag"""
        response = requests.post(
            f"{self.base_url}/tags",
            headers=self.headers,
            json={"name": name}
        )
        response.raise_for_status()
        return response.json()
    
    def delete_tag(self, tag_id: str) -> Dict[str, Any]:
        """Delete a tag by ID"""
        response = requests.delete(
            f"{self.base_url}/tags/{tag_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return {"success": True} if not response.content else response.json()
    
    def update_tag(self, tag_id: str, name: str) -> Dict[str, Any]:
        """Update a tag"""
        response = requests.patch(
            f"{self.base_url}/tags/{tag_id}",
            headers=self.headers,
            json={"name": name}
        )
        response.raise_for_status()
        return response.json()

    # Source Control endpoints
    def pull_from_source_control(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """Pull changes from the remote repository"""
        response = requests.post(
            f"{self.base_url}/source-control/pull",
            headers=self.headers,
            json=options
        )
        response.raise_for_status()
        return response.json()
    
    # Variable endpoints
    def list_variables(self, cursor: Optional[str] = None, limit: Optional[int] = 100) -> Dict[str, Any]:
        """Get all variables"""
        params = {"limit": min(limit, 250)} if limit else {"limit": 100}
        if cursor:
            params["cursor"] = cursor
            
        response = requests.get(
            f"{self.base_url}/variables",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def create_variable(self, data: Dict[str, str]) -> Dict[str, Any]:
        """Create a new variable"""
        response = requests.post(
            f"{self.base_url}/variables",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def delete_variable(self, variable_id: str) -> Dict[str, Any]:
        """Delete a variable by ID"""
        response = requests.delete(
            f"{self.base_url}/variables/{variable_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return {"success": True} if not response.content else response.json()

    # Project endpoints
    def list_projects(self, cursor: Optional[str] = None, limit: Optional[int] = 100) -> Dict[str, Any]:
        """Get all projects"""
        params = {"limit": min(limit, 250)} if limit else {"limit": 100}
        if cursor:
            params["cursor"] = cursor
            
        response = requests.get(
            f"{self.base_url}/projects",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def create_project(self, data: Dict[str, str]) -> Dict[str, Any]:
        """Create a new project"""
        response = requests.post(
            f"{self.base_url}/projects",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def update_project(self, project_id: str, name: str) -> Dict[str, Any]:
        """Update a project"""
        response = requests.put(
            f"{self.base_url}/projects/{project_id}",
            headers=self.headers,
            json={"name": name}
        )
        response.raise_for_status()
        return {"success": True} if not response.content else response.json()
    
    def delete_project(self, project_id: str) -> Dict[str, Any]:
        """Delete a project by ID"""
        response = requests.delete(
            f"{self.base_url}/projects/{project_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return {"success": True} if not response.content else response.json()
