import json
import os
from typing import Dict, Any, List, Optional, Union
import requests
import base64
import binascii

from .client import GitHubClient
from .schema import (
    RepositorySchema, RepositoryList, IssueSchema, IssueList,
    PullRequestSchema, PullRequestList, CommitSchema, ApiResponse, CommitList,
    PullRequestReviewSchema, PullRequestReviewList, GitTreeSchema, GitTreeList,
    RepositoryContentSchema, RepositoryContentList, CreateBlobResponse, GetBlobResponse,
    FileUpdateResponse
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

        print("Pull request:", pull_request)
        
        return self.prepare_response(pull_request, "GitHubPullRequestCard")

    def get_commit(self, owner: str, repo: str, commit_sha: str) -> ApiResponse:
        response = self.client.get_commit(owner, repo, commit_sha)
        commit = CommitSchema(**response)
        
        return self.prepare_response(commit, "GitHubCommitCard")

    def star_repository(self, owner: str, repo: str) -> ApiResponse:
        self.client.star_repository(owner, repo)
        
        return ApiResponse(message='Repository starred successfully')

    def unstar_repository(self, owner: str, repo: str) -> ApiResponse:
        self.client.unstar_repository(owner, repo)
        
        return ApiResponse(message='Repository unstarred successfully')

    def get_commits(self, owner: str, repo: str, sha=None, path=None, author=None,
                   since=None, until=None, per_page=30, page=1) -> ApiResponse:
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

    def create_pull_request(self, owner: str, repo: str, title: str, head: str, 
                           base: str, body: str = None, draft: bool = False) -> ApiResponse:
        data = {
            "title": title,
            "head": head,
            "base": base,
            "body": body,
            "draft": draft
        }
        response = self.client.create_pull_request(
            owner=owner,
            repo=repo,
            data=data
        )
        
        pull_request = PullRequestSchema(**response)
        return self.prepare_response(pull_request, "GitHubPullRequestCard")

    def update_pull_request(self, owner: str, repo: str, pull_number: int, 
                           title: str = None, body: str = None, state: str = None, 
                           base: str = None, maintainer_can_modify: bool = None) -> ApiResponse:
        update_data = {
            "title": title,
            "body": body,
            "state": state,
            "base": base,
            "maintainer_can_modify": maintainer_can_modify
        }
        update_data = {k: v for k, v in update_data.items() if v is not None}
        
        response = self.client.update_pull_request(
            owner=owner,
            repo=repo,
            pull_number=pull_number,
            data=update_data
        )

        print("Update pull request response:", response)
        
        pull_request = PullRequestSchema(**response)
        return self.prepare_response(pull_request, "GitHubPullRequestCard")

    def merge_pull_request(self, owner: str, repo: str, pull_number: int, 
                          commit_title: str = None, commit_message: str = None, 
                          merge_method: str = "merge") -> ApiResponse:
        data = {
            "merge_method": merge_method,
            "commit_title": commit_title,
            "commit_message": commit_message
        }
        data = {k: v for k, v in data.items() if v is not None}
        
        response = self.client.merge_pull_request(
            owner=owner,
            repo=repo,
            pull_number=pull_number,
            data=data
        )
        
        return ApiResponse(message="Pull request merged successfully", data=response)

    def get_pull_request_reviews(self, owner: str, repo: str, pull_number: int) -> ApiResponse:
        response = self.client.get_pull_request_reviews(
            owner=owner,
            repo=repo,
            pull_number=pull_number
        )
        
        reviews = []
        for review_data in response:
            reviews.append(PullRequestReviewSchema(**review_data))
        
        review_list = PullRequestReviewList(
            reviews=reviews,
            next_page=None  # GitHub API doesn't support pagination for reviews
        )
        
        return self.prepare_response(review_list, "GitHubPullRequestReviewCard")

    def create_pull_request_review(self, owner: str, repo: str, pull_number: int, 
                                  body: str = None, event: str = None, 
                                  comments: list = None) -> ApiResponse:
        data = {
            "body": body,
            "event": event,
            "comments": comments
        }
        data = {k: v for k, v in data.items() if v is not None}
        
        response = self.client.create_pull_request_review(
            owner=owner,
            repo=repo,
            pull_number=pull_number,
            data=data
        )
        
        review = PullRequestReviewSchema(**response)
        return self.prepare_response(review, "GitHubPullRequestReviewCard")

    def create_repository_from_template(self, template_owner: str, template_repo: str, 
                                       owner: Optional[str], name: str, 
                                       description: Optional[str] = None,
                                       include_all_branches: bool = False,
                                       private: bool = False) -> ApiResponse:
        data = {
            "owner": owner,
            "name": name,
            "description": description,
            "include_all_branches": include_all_branches,
            "private": private
        }
        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}
        
        response = self.client.create_repository_from_template(
            template_owner=template_owner,
            template_repo=template_repo,
            data=data
        )
        
        repository = RepositorySchema(**response)
        return self.prepare_response(repository, "GitHubRepositoryCard")

    def get_git_tree(self, owner: str, repo: str, tree_sha: str, recursive: bool = False) -> ApiResponse:
        response = self.client.get_git_tree(owner, repo, tree_sha, recursive)
        tree = GitTreeSchema(**response)
        return self.prepare_response(tree, "GitHubGitTreeComponent")

    def get_repository_contents(self, owner: str, repo: str, path: str, ref: Optional[str] = None, decode_content: bool = False) -> ApiResponse:
        response = self.client.get_repository_contents(owner, repo, path, ref)
        
        def process_content(item):
            if decode_content and item.get("type") == "file" and item.get("encoding") == "base64":
                decoded = base64.b64decode(item["content"]).decode("utf-8")
                item["content"] = decoded
                item["encoding"] = "utf-8"
            return item

        if isinstance(response, list):
            contents = [RepositoryContentSchema(**process_content(item)) for item in response]
            return self.prepare_response(RepositoryContentList(contents=contents), "GitHubRepositoryContentComponent")
        
        content = RepositoryContentSchema(**process_content(response))
        return self.prepare_response(content, "GitHubRepositoryContentComponent")

    def create_blob(self, owner: str, repo: str, content: str, encoding: str = "utf-8") -> ApiResponse:
        response = self.client.create_blob(owner, repo, content, encoding)
        return self.prepare_response(CreateBlobResponse(**response), "GitHubBlobComponent")

    def get_blob(self, owner: str, repo: str, file_sha: str, auto_decode: bool = False) -> ApiResponse:
        response = self.client.get_blob(owner, repo, file_sha)
        print("Get blob response:", response)
        blob_data = GetBlobResponse(**response)
        
        if auto_decode and blob_data.encoding == "base64":
            decoded_content = base64.b64decode(blob_data.content).decode('utf-8')
            blob_data.decoded_content = decoded_content
        
        return self.prepare_response(blob_data, "GitHubBlobComponent")

    def update_file(self, owner: str, repo: str, path: str, message: str, 
                   content: str, encoding: str = "utf-8", 
                   sha: Optional[str] = None, branch: Optional[str] = None) -> ApiResponse:
        # Handle encoding
        if encoding == "utf-8":
            content_b64 = base64.b64encode(content.encode()).decode()
        elif encoding == "base64":
            content_b64 = content  # Assume content is already properly encoded
            # Validate base64
            base64.b64decode(content_b64, validate=True)
        else:
            return ApiResponse(message=f"Unsupported encoding: {encoding}")

        data = {
            "message": message,
            "content": content_b64,
            "sha": sha,
            "branch": branch
        }
        data = {k: v for k, v in data.items() if v is not None}

        response = self.client.update_file(owner, repo, path, data)
        return self.prepare_response(FileUpdateResponse(**response), "GitHubFileUpdateComponent")

    def delete_file(self, owner: str, repo: str, path: str, message: str, sha: str,
                   branch: Optional[str] = None, committer: Optional[Dict[str, str]] = None,
                   author: Optional[Dict[str, str]] = None) -> ApiResponse:
        data = {
            "message": message,
            "sha": sha,
            "branch": branch,
            "committer": committer,
            "author": author
        }
        data = {k: v for k, v in data.items() if v is not None}
        
        response = self.client.delete_file(owner, repo, path, data)
        return self.prepare_response(FileUpdateResponse(**response), "GitHubFileUpdateComponent")