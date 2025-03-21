import requests
from typing import Dict, Any, Optional, List, Union

class PosthogClient:
    def __init__(self, api_key: str, base_url: str = "https://us.posthog.com"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
    
    def execute_query(self, project_id: str, query_data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/api/projects/{project_id}/query/"
        response = requests.post(url, headers=self.headers, json=query_data)
        response.raise_for_status()
        return response.json()
    
    def get_query(self, project_id: str, query_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/api/projects/{project_id}/query/{query_id}/"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def delete_query(self, project_id: str, query_id: str) -> None:
        url = f"{self.base_url}/api/projects/{project_id}/query/{query_id}/"
        response = requests.delete(url, headers=self.headers)
        response.raise_for_status()
        return None
    
    def get_insights(self, project_id: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/api/projects/{project_id}/insights/"
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def create_insight(self, project_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/api/projects/{project_id}/insights/"
        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()
    
    def get_insight(self, project_id: str, insight_id: int, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/api/projects/{project_id}/insights/{insight_id}/"
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def update_insight(self, project_id: str, insight_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/api/projects/{project_id}/insights/{insight_id}/"
        response = requests.patch(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()
    
    def check_auth(self) -> bool:
        try:
            # Получаем организации для проверки аутентификации
            self.get_organizations()
            return True
        except Exception:
            return False

    def get_dashboards(self, project_id: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/api/projects/{project_id}/dashboards/"
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    def create_dashboard(self, project_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/api/projects/{project_id}/dashboards/"
        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

    def get_dashboard(self, project_id: str, dashboard_id: int) -> Dict[str, Any]:
        url = f"{self.base_url}/api/projects/{project_id}/dashboards/{dashboard_id}/"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def update_dashboard(self, project_id: str, dashboard_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/api/projects/{project_id}/dashboards/{dashboard_id}/"
        response = requests.patch(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

    def get_events(self, project_id: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/api/projects/{project_id}/events/"
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    def get_event(self, project_id: str, event_id: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/api/projects/{project_id}/events/{event_id}/"
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    def get_projects(self, organization_id: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Retrieve a list of projects in the specified organization"""
        url = f"{self.base_url}/api/organizations/{organization_id}/projects/"
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    def get_project(self, organization_id: str, project_id: int) -> Dict[str, Any]:
        """Retrieve a specific project by ID"""
        url = f"{self.base_url}/api/organizations/{organization_id}/projects/{project_id}/"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_organizations(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Retrieve a list of organizations"""
        url = f"{self.base_url}/api/organizations/"
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    def get_organization(self, organization_id: str) -> Dict[str, Any]:
        """Retrieve a specific organization by ID"""
        url = f"{self.base_url}/api/organizations/{organization_id}/"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_organization_members(self, organization_id: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Retrieve a list of members in the specified organization"""
        url = f"{self.base_url}/api/organizations/{organization_id}/members/"
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    def get_persons(self, project_id: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Retrieve a paginated list of persons"""
        url = f"{self.base_url}/api/projects/{project_id}/persons/"
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    def get_person(self, project_id: str, person_id: int, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Retrieve a specific person by ID"""
        url = f"{self.base_url}/api/projects/{project_id}/persons/{person_id}/"
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    def update_person(self, project_id: str, person_id: Union[int, str], data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a person's properties"""
        url = f"{self.base_url}/api/projects/{project_id}/persons/{person_id}/"
        response = requests.patch(url, headers=self.headers, json=data)
        response.raise_for_status()
        
        if response.status_code == 204 or not response.text.strip():
            return {
                "id": person_id,
                "distinct_ids": [],
                "properties": data.get("properties", {})
            }
        
        return response.json()

    def delete_person(self, project_id: str, person_id: int, delete_events: bool = False) -> None:
        """Delete a person and optionally their events"""
        url = f"{self.base_url}/api/projects/{project_id}/persons/{person_id}/"
        params = {"delete_events": "true" if delete_events else "false"}
        response = requests.delete(url, headers=self.headers, params=params)
        response.raise_for_status()
        return None

    def bulk_delete_persons(self, project_id: str, data: Dict[str, Any], delete_events: bool = False) -> Dict[str, Any]:
        """Bulk delete persons by IDs or distinct_ids"""
        url = f"{self.base_url}/api/projects/{project_id}/persons/bulk_delete/"
        params = {"delete_events": "true" if delete_events else "false"}
        response = requests.post(url, headers=self.headers, json=data, params=params)
        response.raise_for_status()
        return {"success": True}

    def get_actions(self, project_id: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Retrieve a paginated list of actions"""
        url = f"{self.base_url}/api/projects/{project_id}/actions/"
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    def create_action(self, project_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new action"""
        url = f"{self.base_url}/api/projects/{project_id}/actions/"
        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

    def get_action(self, project_id: str, action_id: int, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Retrieve a specific action by ID"""
        url = f"{self.base_url}/api/projects/{project_id}/actions/{action_id}/"
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    def update_action(self, project_id: str, action_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an action's properties"""
        url = f"{self.base_url}/api/projects/{project_id}/actions/{action_id}/"
        response = requests.patch(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

    def delete_action(self, project_id: str, action_id: int) -> Dict[str, bool]:
        """Delete an action (mark as deleted)"""
        url = f"{self.base_url}/api/projects/{project_id}/actions/{action_id}/"

        get_response = requests.get(url, headers=self.headers)
        
        if get_response.status_code == 200:
            update_data = {"deleted": True}
            patch_response = requests.patch(url, headers=self.headers, json=update_data)
            
            if patch_response.status_code >= 200 and patch_response.status_code < 300:
                return {"success": True}
        
        return {"success": False}
    
    def get_feature_flags(self, project_id: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Retrieve a paginated list of feature flags"""
        url = f"{self.base_url}/api/projects/{project_id}/feature_flags/"
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    def create_feature_flag(self, project_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new feature flag"""
        url = f"{self.base_url}/api/projects/{project_id}/feature_flags/"
        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

    def get_feature_flag(self, project_id: str, flag_id: int) -> Dict[str, Any]:
        """Retrieve a specific feature flag by ID"""
        url = f"{self.base_url}/api/projects/{project_id}/feature_flags/{flag_id}/"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def update_feature_flag(self, project_id: str, flag_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a feature flag"""
        url = f"{self.base_url}/api/projects/{project_id}/feature_flags/{flag_id}/"
        response = requests.patch(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

    def delete_feature_flag(self, project_id: str, flag_id: int) -> Dict[str, bool]:
        """Mark a feature flag as deleted"""
        url = f"{self.base_url}/api/projects/{project_id}/feature_flags/{flag_id}/"
        data = {"deleted": True}
        response = requests.patch(url, headers=self.headers, json=data)
        response.raise_for_status()
        return {"success": True}

