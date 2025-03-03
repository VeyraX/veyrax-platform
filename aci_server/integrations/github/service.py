import json
import os
from typing import Dict, Any, List, Optional, Union

from .client import GitHubClient
from .schema import (
    RepositorySchema, RepositoryList, IssueSchema, IssueList,
    PullRequestSchema, PullRequestList, CommitSchema, ApiResponse, CommitList
)
from ..common.component_handler import prepare_components_auto, load_components

class GitHubService:
    def __init__(self, client: GitHubClient):
        self.client = client
        self.components_data = self._load_components()

    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)

    def prepare_response(self, data: Union[RepositoryList, IssueList, PullRequestList, CommitList], component_name: str = None) -> ApiResponse:
        tool_name = "github"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)

    def get_repositories(self, username=None, type="all", sort="updated", 
                         direction="desc", per_page=30, page=1) -> ApiResponse:
        params = {
            "username": username,
            "type": type,
            "sort": sort,
            "direction": direction,
            "per_page": per_page,
            "page": page
        }
        
        response = self.client.get_repositories(**params)
        
        repositories = []
        for repo_data in response:
            repositories.append(RepositorySchema(**repo_data))
        
        repository_list = RepositoryList(
            repositories=repositories,
            next_page=page + 1 if len(repositories) == per_page else None
        )
        
        return self.prepare_response(repository_list, "GitHubRepositoryCard")

    def get_repository(self, owner: str, repo: str) -> ApiResponse:
        response = self.client.get_repository(owner, repo)
        repository = RepositorySchema(**response)
        
        return self.prepare_response(repository, "GitHubRepositoryCard")

    def get_issues(self, owner: str, repo: str, state="open", sort="created", 
                   direction="desc", per_page=30, page=1) -> ApiResponse:
        params = {
            "state": state,
            "sort": sort,
            "direction": direction,
            "per_page": per_page,
            "page": page
        }
        
        response = self.client.get_issues(owner, repo, **params)
        
        issues = []
        for issue_data in response:
            if "pull_request" not in issue_data:
                issue_data["repository"] = {"owner": owner, "name": repo}
                issues.append(IssueSchema(**issue_data))
        
        issue_list = IssueList(
            issues=issues,
            next_page=page + 1 if len(issues) == per_page else None
        )
        
        return self.prepare_response(issue_list, "GitHubIssueCard")

    def get_issue(self, owner: str, repo: str, issue_number: int) -> ApiResponse:
        response = self.client.get_issue(owner, repo, issue_number)
        
        response["repository"] = {"owner": owner, "name": repo}
        issue = IssueSchema(**response)
        
        return self.prepare_response(issue, "GitHubIssueCard")

    def get_pull_requests(self, owner: str, repo: str, state="open", sort="created", 
                          direction="desc", per_page=30, page=1) -> ApiResponse:
        params = {
            "state": state,
            "sort": sort,
            "direction": direction,
            "per_page": per_page,
            "page": page
        }
        
        response = self.client.get_pull_requests(owner, repo, **params)
        
        pull_requests = []
        for pr_data in response:
            pull_requests.append(PullRequestSchema(**pr_data))
        
        pr_list = PullRequestList(
            pull_requests=pull_requests,
            next_page=page + 1 if len(pull_requests) == per_page else None
        )
        
        return self.prepare_response(pr_list, "GitHubPullRequestCard")

    def get_pull_request(self, owner: str, repo: str, pull_number: int) -> ApiResponse:
        response = self.client.get_pull_request(owner, repo, pull_number)
        pull_request = PullRequestSchema(**response)
        
        return self.prepare_response(pull_request, "GitHubPullRequestCard")

    def get_commit(self, owner: str, repo: str, commit_sha: str) -> ApiResponse:
        response = self.client.get_commit(owner, repo, commit_sha)
        commit = CommitSchema(**response)
        
        return self.prepare_response(commit, "GitHubCommitCard")

    def star_repository(self, owner: str, repo: str) -> ApiResponse:
        self.client.star_repository(owner, repo)
        
        return self.prepare_response(None, "GitHubRepositoryCard", 
                                    message=f"Repository {owner}/{repo} has been starred successfully")

    def unstar_repository(self, owner: str, repo: str) -> ApiResponse:
        self.client.unstar_repository(owner, repo)
        
        return self.prepare_response(None, "GitHubRepositoryCard", 
                                    message=f"Repository {owner}/{repo} has been unstarred successfully")

    def get_commits(self, owner: str, repo: str, sha=None, path=None, author=None,
                   since=None, until=None, per_page=30, page=1) -> ApiResponse:
        try:
            params = {
                'sha': sha,
                'path': path,
                'author': author,
                'since': since,
                'until': until,
                'per_page': per_page,
                'page': page
            }
            params = {k: v for k, v in params.items() if v is not None}
            
            response = self.client.get_commits(owner, repo, **params)
            
            commits_list = []
            for commit in response:
                commits_list.append(CommitSchema(**commit))
            
            next_page = None
            if len(commits_list) == per_page:
                next_page = page + 1
                
            result = CommitList(commits=commits_list, next_page=next_page)
            return self.prepare_response(result, "GitHubCommitCard")
        except Exception as e:
            import traceback
            traceback.print_exc()
            return ApiResponse(message=f"Error retrieving commits: {str(e)}")