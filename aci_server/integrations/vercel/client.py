import requests
from typing import Dict, Any, List, Optional

class VercelClient:
    BASE_URL = "https://api.vercel.com"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self._initialize_client()

    def _initialize_client(self):
        """Initialize client with proper headers"""
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def list_deployments(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """List deployments under the authenticated user or team"""
        response = requests.get(
            f"{self.BASE_URL}/v6/deployments",
            headers=self.headers,
            params=self._clean_params(params or {})
        )
        response.raise_for_status()
        return response.json()

    def get_deployment(self, id_or_url: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get a deployment by ID or URL"""
        response = requests.get(
            f"{self.BASE_URL}/v13/deployments/{id_or_url}",
            headers=self.headers,
            params=self._clean_params(params or {})
        )
        response.raise_for_status()
        return response.json()

    def delete_deployment(self, deployment_id: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Delete a deployment by ID"""
        response = requests.delete(
            f"{self.BASE_URL}/v13/deployments/{deployment_id}",
            headers=self.headers,
            params=self._clean_params(params or {})
        )
        response.raise_for_status()
        return response.json()

    def cancel_deployment(self, deployment_id: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Cancel a deployment which is currently building"""
        response = requests.patch(
            f"{self.BASE_URL}/v12/deployments/{deployment_id}/cancel",
            headers=self.headers,
            params=self._clean_params(params or {})
        )
        response.raise_for_status()
        return response.json()

    def get_deployment_files(self, deployment_id: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """List deployment files"""
        response = requests.get(
            f"{self.BASE_URL}/v6/deployments/{deployment_id}/files",
            headers=self.headers,
            params=self._clean_params(params or {})
        )
        response.raise_for_status()
        return response.json()
        
    def get_user(self) -> Dict[str, Any]:
        """Get authenticated user information"""
        response = requests.get(
            f"{self.BASE_URL}/v2/user",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def get_deployment_events(self, id_or_url: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get the build logs of a deployment by deployment ID"""
        response = requests.get(
            f"{self.BASE_URL}/v3/deployments/{id_or_url}/events",
            headers=self.headers,
            params=self._clean_params(params or {})
        )
        response.raise_for_status()
        print(response.json())
        return response.json()

    def add_domain_to_project(self, project_id_or_name: str, data: Dict[str, Any], params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Add a domain to a project"""
        response = requests.post(
            f"{self.BASE_URL}/v10/projects/{project_id_or_name}/domains",
            headers=self.headers,
            json=data,
            params=self._clean_params(params or {})
        )
        response.raise_for_status()
        return response.json()

    def create_project(self, data: Dict[str, Any], params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a new project"""
        response = requests.post(
            f"{self.BASE_URL}/v11/projects",
            headers=self.headers,
            json=data,
            params=self._clean_params(params or {})
        )
        response.raise_for_status()
        return response.json()

    def create_env_vars(self, project_id_or_name: str, data: Dict[str, Any], params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create one or more environment variables for a project"""
        print(data)
        response = requests.post(
            f"{self.BASE_URL}/v10/projects/{project_id_or_name}/env",
            headers=self.headers,
            json=data,
            params=self._clean_params(params or {})
        )
        print(response.json())
        
        # Instead of raising an exception, return the error response
        if response.status_code == 400 and "error" in response.json():
            return response.json()
        
        response.raise_for_status()
        return response.json()

    def delete_project(self, project_id_or_name: str, params: Dict[str, Any] = None) -> None:
        """Delete a project"""
        response = requests.delete(
            f"{self.BASE_URL}/v9/projects/{project_id_or_name}",
            headers=self.headers,
            params=self._clean_params(params or {})
        )
        response.raise_for_status()
        return None

    def edit_env_var(self, project_id_or_name: str, env_var_id: str, data: Dict[str, Any], params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Edit an environment variable for a project"""
        response = requests.patch(
            f"{self.BASE_URL}/v9/projects/{project_id_or_name}/env/{env_var_id}",
            headers=self.headers,
            json=data,
            params=self._clean_params(params or {})
        )
        response.raise_for_status()
        return response.json()
    
    def get_project(self, project_id_or_name: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get a project by ID or name"""
        response = requests.get(
            f"{self.BASE_URL}/v9/projects/{project_id_or_name}",
            headers=self.headers,
            params=self._clean_params(params or {})
        )
        response.raise_for_status()
        return response.json()
    
    def get_project_domain(self, project_id_or_name: str, domain: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get a project domain by project ID/name and domain name"""
        response = requests.get(
            f"{self.BASE_URL}/v9/projects/{project_id_or_name}/domains/{domain}",
            headers=self.headers,
            params=self._clean_params(params or {})
        )
        response.raise_for_status()
        return response.json()
    
    def remove_env_var(self, project_id_or_name: str, env_var_id: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Remove an environment variable from a project"""
        response = requests.delete(
            f"{self.BASE_URL}/v9/projects/{project_id_or_name}/env/{env_var_id}",
            headers=self.headers,
            params=self._clean_params(params or {})
        )
        response.raise_for_status()
        return response.json()
    
    def list_projects(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Retrieve a list of projects"""
        response = requests.get(
            f"{self.BASE_URL}/v10/projects",
            headers=self.headers,
            params=self._clean_params(params or {})
        )
        response.raise_for_status()
        return response.json()

    def get_project_domains(self, project_id_or_name: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Retrieve the domains associated with a given project"""
        response = requests.get(
            f"{self.BASE_URL}/v9/projects/{project_id_or_name}/domains",
            headers=self.headers,
            params=self._clean_params(params or {})
        )
        response.raise_for_status()
        return response.json()

    def verify_project_domain(self, project_id_or_name: str, domain: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Verify a project domain"""
        response = requests.post(
            f"{self.BASE_URL}/v9/projects/{project_id_or_name}/domains/{domain}/verify",
            headers=self.headers,
            params=self._clean_params(params or {})
        )
        response.raise_for_status()
        return response.json()

    def update_project(self, project_id_or_name: str, data: Dict[str, Any], params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Update an existing project"""
        response = requests.patch(
            f"{self.BASE_URL}/v9/projects/{project_id_or_name}",
            headers=self.headers,
            json=data,
            params=self._clean_params(params or {})
        )
        response.raise_for_status()
        return response.json()

    def get_project_env_vars(self, project_id_or_name: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get all environment variables for a project"""
        response = requests.get(
            f"{self.BASE_URL}/v9/projects/{project_id_or_name}/env",
            headers=self.headers,
            params=self._clean_params(params or {})
        )
        response.raise_for_status()
        return response.json()

    def create_deployment(self, data: Dict[str, Any], params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a new deployment"""
        print(data)
        response = requests.post(
            f"{self.BASE_URL}/v13/deployments",
            headers=self.headers,
            json=data,
            params=self._clean_params(params or {})
        )
        
        response_data = response.json()
        
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if response_data and "error" in response_data:
                error_info = response_data["error"]
                error_message = f"{e} - {error_info.get('code', '')}: {error_info.get('message', '')}"
                raise requests.exceptions.HTTPError(error_message, response=response)
            raise
            
        return response_data

    def _clean_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Clean parameters for API requests"""
        cleaned = {}
        for k, v in params.items():
            if v is None:
                continue
            if isinstance(v, bool):
                cleaned[k] = str(v).lower()
            elif isinstance(v, list):
                cleaned[k] = ",".join(map(str, v))
            else:
                cleaned[k] = v
        return cleaned