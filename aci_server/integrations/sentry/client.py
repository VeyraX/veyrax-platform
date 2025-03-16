import requests
from typing import Dict, Any, Optional

class SentryClient:
    BASE_URL = "https://sentry.io/api/0"
    
    def __init__(self, access_token: str, org_slug: str):
        self.access_token = access_token
        self.org_slug = org_slug
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    def _handle_response(self, response: requests.Response) -> Dict:
        response.raise_for_status()
        return response.json()

    # Organization and Team Management
    def list_organizations(self) -> Dict:
        return self._handle_response(
            requests.get(f"{self.BASE_URL}/organizations/", headers=self.headers)
        )
        
    def list_teams(self) -> Dict:
        return self._handle_response(
            requests.get(f"{self.BASE_URL}/organizations/{self.org_slug}/teams/", headers=self.headers)
        )
        
    def create_team(self, data: Dict[str, Any]) -> Dict:
        return self._handle_response(
            requests.post(f"{self.BASE_URL}/organizations/{self.org_slug}/teams/", 
                         headers=self.headers,
                         json=data)
        )
        
    def list_user_teams(self) -> Dict:
        return self._handle_response(
            requests.get(f"{self.BASE_URL}/organizations/{self.org_slug}/user-teams/", 
                        headers=self.headers)
        )

    # Project Management
    def list_projects(self) -> Dict:
        return self._handle_response(
            requests.get(f"{self.BASE_URL}/organizations/{self.org_slug}/projects/", headers=self.headers)
        )
        
    def create_project(self, team_slug: str, data: Dict[str, Any]) -> Dict:
        return self._handle_response(
            requests.post(f"{self.BASE_URL}/teams/{self.org_slug}/{team_slug}/projects/", 
                         headers=self.headers,
                         json=data)
        )
    
    # Issues and Events Management
    def list_issues(self, project_slug: str, query_params: Optional[Dict[str, Any]] = None) -> Dict:
        return self._handle_response(
            requests.get(f"{self.BASE_URL}/projects/{self.org_slug}/{project_slug}/issues/", 
                        headers=self.headers,
                        params=query_params)
        )
        
    def get_issue_details(self, issue_id: str) -> Dict:
        return self._handle_response(
            requests.get(f"{self.BASE_URL}/issues/{issue_id}/", 
                        headers=self.headers)
        )
        
    def list_issue_events(self, issue_id: str, query_params: Optional[Dict[str, Any]] = None) -> Dict:
        return self._handle_response(
            requests.get(f"{self.BASE_URL}/issues/{issue_id}/events/", 
                        headers=self.headers,
                        params=query_params)
        )
    
    # Releases Management
    def list_releases(self, query_params: Optional[Dict[str, Any]] = None) -> Dict:
        return self._handle_response(
            requests.get(f"{self.BASE_URL}/organizations/{self.org_slug}/releases/", 
                        headers=self.headers,
                        params=query_params)
        )
        
    def create_release(self, data: Dict[str, Any]) -> Dict:
        return self._handle_response(
            requests.post(
                f"{self.BASE_URL}/organizations/{self.org_slug}/releases/",
                headers=self.headers,
                json=data
            )
        )
    
    # Alert Rules Management
    def list_alert_rules(self, project_slug: str) -> Dict:
        return self._handle_response(
            requests.get(f"{self.BASE_URL}/projects/{self.org_slug}/{project_slug}/rules/", 
                        headers=self.headers)
        )
        
    def create_alert_rule(self, project_slug: str, data: Dict[str, Any]) -> Dict:
        return self._handle_response(
            requests.post(f"{self.BASE_URL}/projects/{self.org_slug}/{project_slug}/rules/", 
                         headers=self.headers,
                         json=data)
        )
    
    # User Feedback Management
    def list_user_feedback(self, project_slug: str, query_params: Optional[Dict[str, Any]] = None) -> Dict:
        return self._handle_response(
            requests.get(f"{self.BASE_URL}/projects/{self.org_slug}/{project_slug}/user-feedback/", 
                        headers=self.headers,
                        params=query_params)
        )
    
    # Service Hooks Management
    def list_service_hooks(self, project_slug: str) -> Dict:
        return self._handle_response(
            requests.get(f"{self.BASE_URL}/projects/{self.org_slug}/{project_slug}/hooks/", 
                        headers=self.headers)
        )
        
    def create_service_hook(self, project_slug: str, data: Dict[str, Any]) -> Dict:
        return self._handle_response(
            requests.post(f"{self.BASE_URL}/projects/{self.org_slug}/{project_slug}/hooks/", 
                         headers=self.headers,
                         json=data)
        )

    def get_project_dsn(self, project_slug: str) -> Dict:
        return self._handle_response(
            requests.get(
                f"{self.BASE_URL}/projects/{self.org_slug}/{project_slug}/keys/",
                headers=self.headers
            )
        )

