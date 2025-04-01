from typing import Optional, Dict, Any, List
import requests
from urllib.parse import urljoin
import base64

class JiraClient:
    def __init__(self, token: str):
        self.token = token
        self.session = requests.Session()
        
        self.session.headers.update({
            'Authorization': f'Bearer {token}', 
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.base_url = None
        self.cloud_id = None
        self.browser_base_url = None
        self.site_id = None

    def get_accessible_resources(self) -> List[Dict[str, Any]]:
        response = self.session.get(
            "https://api.atlassian.com/oauth/token/accessible-resources",
            headers={'Authorization': f'Bearer {self.token}'}
        )
        response.raise_for_status()
        return response.json()

    def initialize_client(self):
        resources = self.get_accessible_resources()
        if not resources:
            raise Exception("No Jira resources available")
        
        resource = resources[0]
        self.cloud_id = resource['id']
        self.site_id = resource.get('url', '').split('/')[-1].replace('.atlassian.net', '')
        self.base_url = f"https://api.atlassian.com/ex/jira/{self.cloud_id}/rest/api/2"
        self.browser_base_url = f"https://{self.site_id}.atlassian.net"
        return resource

    def get_server_info(self) -> Dict[str, Any]:
        if not self.cloud_id:
            self.initialize_client()
        response = self.session.get(
            f"https://api.atlassian.com/ex/jira/{self.cloud_id}/rest/api/3/serverInfo",
            headers={'Authorization': f'Bearer {self.token}'}
        )
        response.raise_for_status()
        return response.json()

    def make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        if not self.base_url:
            self.initialize_client()
            
        url = f"{self.base_url}/{endpoint}"
        
        headers = kwargs.pop('headers', {})
        headers.update({
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        kwargs['headers'] = headers
        
        response = self.session.request(method, url, **kwargs)
        
        if not response.ok:
            try:
                error_data = response.json()
                error_message = error_data.get('errorMessages', [])
                if error_message:
                    error_message = error_message[0]
                else:
                    error_message = error_data.get('errors', {}).get('error', str(response.text))
                response.reason = error_message
            except:
                pass
            response.raise_for_status()
        
        return response.json() if response.content else None

    def get_issue(self, issue_id: str) -> Dict[str, Any]:
        return self.make_request('GET', f'issue/{issue_id}')

    def get_issue_comments(self, issue_id: str) -> Dict[str, Any]:
        return self.make_request('GET', f'issue/{issue_id}/comment')

    def create_issue(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        return self.make_request('POST', 'issue', json={'fields': fields})

    def update_issue(self, issue_id: str, fields: Dict[str, Any]) -> None:
        return self.make_request('PUT', f'issue/{issue_id}', json={'fields': fields})

    def delete_issue(self, issue_id: str) -> None:
        return self.make_request('DELETE', f'issue/{issue_id}')

    def transition_issue(self, issue_id: str, transition_id: str) -> Dict[str, Any]:
        return self.make_request(
            'POST',
            f'issue/{issue_id}/transitions',
            json={'transition': {'id': transition_id}}
        )

    def search_issues(self, jql: str, start_at: int = 0, max_results: int = 50) -> Dict[str, Any]:
        params = {
            'jql': jql,
            'startAt': start_at,
            'maxResults': max_results
        }
        return self.make_request('GET', 'search', params=params)

    def add_comment(self, issue_id: str, body: str) -> Dict[str, Any]:
        return self.make_request('POST', f'issue/{issue_id}/comment', json={'body': body})

    def get_comments(self, issue_id: str) -> List[Dict[str, Any]]:
        response = self.make_request('GET', f'issue/{issue_id}/comment')
        return response.get('comments', [])

    def get_projects(self) -> List[Dict[str, Any]]:
        """Get all accessible projects"""
        return self.make_request('GET', 'project')

    def get_project(self, project_id: str) -> Dict[str, Any]:
        """Get detailed project information"""
        return self.make_request('GET', f'project/{project_id}')

    def get_all_statuses(self) -> List[Dict[str, Any]]:
        """Get all available statuses"""
        return self.make_request('GET', 'status')

    def get_all_priorities(self) -> List[Dict[str, Any]]:
        """Get all available priorities"""
        return self.make_request('GET', 'priority')

    def get_all_issue_types(self) -> List[Dict[str, Any]]:
        """Get all issue types"""
        return self.make_request('GET', 'issuetype')

    def get_all_fields(self) -> List[Dict[str, Any]]:
        """Get all available fields"""
        return self.make_request('GET', 'field')

    def get_users(self, query: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get users that match the search query"""
        params = {
            'query': query if query else ''
        }
        return self.make_request('GET', 'user/search', params=params)

    def get_transitions(self, issue_id: str) -> Dict[str, Any]:
        return self.make_request('GET', f'issue/{issue_id}/transitions')