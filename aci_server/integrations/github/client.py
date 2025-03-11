import requests
from typing import Dict, Any, Optional


class GitHubClient:
    BASE_URL = "https://api.github.com"

    def __init__(self, token: str):
        self.token = token
        self._initialize_client()

    def _initialize_client(self):
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def get_repositories(self, **kwargs) -> Dict[str, Any]:
        username = kwargs.pop('username', None)
        if username:
            endpoint = f"/users/{username}/repos"
        else:
            endpoint = "/user/repos"
        return self._make_request("GET", endpoint, params=kwargs)

    def get_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        endpoint = f"/repos/{owner}/{repo}"
        return self._make_request("GET", endpoint)

    def get_issues(self, owner: str, repo: str, **kwargs) -> Dict[str, Any]:
        endpoint = f"/repos/{owner}/{repo}/issues"
        return self._make_request("GET", endpoint, params=kwargs)

    def get_issue(self, owner: str, repo: str, issue_number: int) -> Dict[str, Any]:
        endpoint = f"/repos/{owner}/{repo}/issues/{issue_number}"
        return self._make_request("GET", endpoint)

    def get_pull_requests(self, owner: str, repo: str, **kwargs) -> Dict[str, Any]:
        endpoint = f"/repos/{owner}/{repo}/pulls"
        return self._make_request("GET", endpoint, params=kwargs)

    def get_pull_request(self, owner: str, repo: str, pull_number: int) -> Dict[str, Any]:
        endpoint = f"/repos/{owner}/{repo}/pulls/{pull_number}"
        return self._make_request("GET", endpoint)

    def get_commit(self, owner: str, repo: str, commit_sha: str) -> Dict[str, Any]:
        endpoint = f"/repos/{owner}/{repo}/commits/{commit_sha}"
        return self._make_request("GET", endpoint)

    def get_commits(self, owner: str, repo: str, **kwargs) -> Dict[str, Any]:
        endpoint = f"/repos/{owner}/{repo}/commits"
        return self._make_request("GET", endpoint, params=kwargs)

    def star_repository(self, owner: str, repo: str) -> None:
        endpoint = f"/user/starred/{owner}/{repo}"
        return self._make_request("PUT", endpoint)

    def unstar_repository(self, owner: str, repo: str) -> None:
        endpoint = f"/user/starred/{owner}/{repo}"
        return self._make_request("DELETE", endpoint)

    def create_pull_request(self, owner: str, repo: str, data: dict) -> Dict[str, Any]:
        """Create a new pull request."""
        endpoint = f"/repos/{owner}/{repo}/pulls"
        return self._make_request("POST", endpoint, data=data)

    def update_pull_request(self, owner: str, repo: str, pull_number: int, data: dict) -> Dict[str, Any]:
        """Update an existing pull request."""
        endpoint = f"/repos/{owner}/{repo}/pulls/{pull_number}"
        return self._make_request("PATCH", endpoint, data=data)

    def merge_pull_request(self, owner: str, repo: str, pull_number: int, data: dict) -> Dict[str, Any]:
        """Merge a pull request."""
        endpoint = f"/repos/{owner}/{repo}/pulls/{pull_number}/merge"
        return self._make_request("PUT", endpoint, data=data)

    def get_pull_request_reviews(self, owner: str, repo: str, pull_number: int) -> Dict[str, Any]:
        """Get reviews for a pull request."""
        endpoint = f"/repos/{owner}/{repo}/pulls/{pull_number}/reviews"
        return self._make_request("GET", endpoint)

    def create_pull_request_review(self, owner: str, repo: str, pull_number: int, data: dict) -> Dict[str, Any]:
        """Create a review for a pull request."""
        endpoint = f"/repos/{owner}/{repo}/pulls/{pull_number}/reviews"
        return self._make_request("POST", endpoint, data=data)

    def _make_request(self, method, endpoint, params=None, data=None):
        """Make a request to the GitHub API."""
        url = f"{self.BASE_URL}{endpoint}"
        response = requests.request(
            method=method,
            url=url,
            headers=self.headers,
            params=params,
            json=data
        )
        
        if response.status_code == 204:
            return {}
            
        response.raise_for_status()
        return response.json() if response.content else {}
