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

    def get_accessible_resources(self) -> Dict[str, Any]:
        response = self.session.get(
            "https://api.atlassian.com/oauth/token/accessible-resources",
            headers={'Authorization': f'Bearer {self.token}'}
        )
        response.raise_for_status()
        return response.json()

    def get_server_info(self, cloud_id: str) -> Dict[str, Any]:
        response = self.session.get(
            f"https://api.atlassian.com/ex/jira/{cloud_id}/rest/api/3/serverInfo",
            headers={'Authorization': f'Bearer {self.token}'}
        )
        response.raise_for_status()
        return response.json()

    def make_request(self, base_url: str, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        url = f"{base_url}/rest/api/2/{endpoint}"
        
        headers = kwargs.pop('headers', {})
        headers.update({
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        kwargs['headers'] = headers
        
        try:
            response = self.session.request(method, url, **kwargs)
            
            if not response.ok:
                error_detail = response.text
                try:
                    error_json = response.json()
                    if isinstance(error_json, dict):
                        error_detail = error_json.get('errorMessages', [])
                        if not error_detail and 'errors' in error_json:
                            error_detail = error_json['errors']
                except:
                    pass
                
                error_msg = f"{response.status_code} {response.reason} for url: {url}"
                if error_detail:
                    error_msg += f" - Details: {error_detail}"
                
                raise requests.exceptions.HTTPError(error_msg, response=response)
            
            return response.json() if response.content else None
        except requests.exceptions.RequestException as e:
            raise

    def get_issue(self, issue_id: str) -> Dict[str, Any]:
        return self.make_request(self.ATLASSIAN_API_URL, 'GET', f'issue/{issue_id}')

    def create_issue(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        return self.make_request(self.ATLASSIAN_API_URL, 'POST', 'issue', json={'fields': fields})

    def update_issue(self, issue_id: str, fields: Dict[str, Any]) -> None:
        self.make_request(self.ATLASSIAN_API_URL, 'PUT', f'issue/{issue_id}', json={'fields': fields})

    def delete_issue(self, issue_id: str) -> None:
        self.make_request(self.ATLASSIAN_API_URL, 'DELETE', f'issue/{issue_id}')

    def search_issues(self, jql: str, **kwargs) -> Dict[str, Any]:
        params = {
            'jql': jql,
            'startAt': kwargs.get('startAt', 0),
            'maxResults': kwargs.get('maxResults', 50)
        }
        return self.make_request(self.ATLASSIAN_API_URL, 'GET', 'search', params=params)

    def add_comment(self, issue_id: str, body: str) -> Dict[str, Any]:
        return self.make_request(self.ATLASSIAN_API_URL, 'POST', f'issue/{issue_id}/comment', json={'body': body})

    def get_comments(self, issue_id: str) -> List[Dict[str, Any]]:
        response = self.make_request(self.ATLASSIAN_API_URL, 'GET', f'issue/{issue_id}/comment')
        return response.get('comments', [])

    def get_projects(self) -> List[Dict[str, Any]]:
        """Get all accessible projects"""
        return self.make_request(self.base_url, 'GET', 'project')

    def get_project(self, project_id: str) -> Dict[str, Any]:
        """Get detailed project information"""
        return self.make_request(self.base_url, 'GET', f'project/{project_id}')

    def get_all_statuses(self) -> List[Dict[str, Any]]:
        """Get all available statuses"""
        return self.make_request(self.base_url, 'GET', 'status')

    def get_all_priorities(self) -> List[Dict[str, Any]]:
        """Get all available priorities"""
        return self.make_request(self.base_url, 'GET', 'priority')

    def get_all_issue_types(self) -> List[Dict[str, Any]]:
        """Get all issue types"""
        return self.make_request(self.base_url, 'GET', 'issuetype')

    def get_all_fields(self) -> List[Dict[str, Any]]:
        """Get all available fields"""
        return self.make_request(self.base_url, 'GET', 'field')

    def get_users(self, query: Optional[str] = None, base_url: str = None) -> List[Dict[str, Any]]:
        """Get users that match the search query"""
        params = {
            'query': query if query else ''
        }
        return self.make_request(base_url, 'GET', 'user/search', params=params)

    def get_transitions(self, issue_id: str, base_url: str) -> List[Dict[str, Any]]:
        return self.make_request(
            base_url,
            'GET',
            f'issue/{issue_id}/transitions'
        )