import requests
from typing import Dict, Any, Optional


class GitHubAPIError(Exception):
    """Base exception for GitHub API errors"""
    default_message = "GitHub API error occurred"
    default_status = 500
    
    def __init__(self, message=None, status_code=None):
        self.message = message or self.default_message
        self.status_code = status_code or self.default_status
        super().__init__(self.message)

    @classmethod
    def from_response(cls, response: requests.Response):
        """Factory method to create appropriate error from response"""
        error_classes = {
            401: GitHubAuthError,
            404: GitHubNotFoundError,
            422: GitHubValidationError,
            429: GitHubRateLimitError
        }
        
        error_class = error_classes.get(response.status_code, cls)
        
        try:
            error_data = response.json()
            message = error_data.get('message', response.text)
        except:
            message = response.text
            
        return error_class(
            message=f"{response.status_code} Error: {message}",
            status_code=response.status_code
        )

# Subclasses must be defined AFTER the from_response method
class GitHubAuthError(GitHubAPIError):
    default_message = "Authentication failed - invalid or expired token"
    default_status = 401

class GitHubNotFoundError(GitHubAPIError):
    default_message = "Resource not found - check repository/user existence and permissions"
    default_status = 404

class GitHubValidationError(GitHubAPIError):
    default_message = "Invalid request parameters"
    default_status = 422

class GitHubRateLimitError(GitHubAPIError):
    default_message = "API rate limit exceeded"
    default_status = 429

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
        url = f"{self.BASE_URL}{endpoint}"
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                params=params,
                json=data
            )
            
            if not response.ok:
                error = GitHubAPIError.from_response(response)

                if isinstance(error, GitHubValidationError) and "/pulls" in endpoint:
                    error.message += " - Check your branch names, cannot create pull request between these branches"
                
                raise error

            return response.json() if response.content else {}
            
        except requests.exceptions.RequestException as e:
            raise GitHubAPIError(f"Request failed: {str(e)}", 500) from e
