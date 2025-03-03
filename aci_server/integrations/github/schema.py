from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class RepositorySchema(BaseModel):
    id: int
    name: str
    full_name: str
    description: Optional[str] = None
    html_url: str
    stargazers_count: Optional[int] = None
    forks_count: Optional[int] = None
    open_issues_count: Optional[int] = None
    owner: Dict[str, Any]
    private: bool
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    language: Optional[str] = None
    default_branch: Optional[str] = None
    topics: Optional[List[str]] = None


class IssueSchema(BaseModel):
    id: int
    number: int
    title: str
    body: Optional[str] = None
    state: str
    html_url: str
    user: Dict[str, Any]
    created_at: str
    updated_at: Optional[str] = None
    closed_at: Optional[str] = None
    labels: Optional[List[Dict[str, Any]]] = None
    assignees: Optional[List[Dict[str, Any]]] = None
    comments: Optional[int] = None
    repository: Optional[Dict[str, Any]] = None


class PullRequestSchema(BaseModel):
    id: int
    number: int
    title: str
    body: Optional[str] = None
    state: str
    html_url: str
    user: Dict[str, Any]
    created_at: str
    updated_at: Optional[str] = None
    closed_at: Optional[str] = None
    merged_at: Optional[str] = None
    labels: Optional[List[Dict[str, Any]]] = None
    assignees: Optional[List[Dict[str, Any]]] = None
    requested_reviewers: Optional[List[Dict[str, Any]]] = None
    head: Dict[str, Any]
    base: Dict[str, Any]
    merged: Optional[bool] = None
    mergeable: Optional[bool] = None
    draft: Optional[bool] = None


class CommitSchema(BaseModel):
    sha: str
    commit: Dict[str, Any]
    author: Optional[Dict[str, Any]] = None
    committer: Optional[Dict[str, Any]] = None
    html_url: str
    parents: Optional[List[Dict[str, Any]]] = None
    stats: Optional[Dict[str, Any]] = None
    files: Optional[List[Dict[str, Any]]] = None


class RepositoryList(BaseModel):
    repositories: List[RepositorySchema]
    next_page: Optional[int] = None


class IssueList(BaseModel):
    issues: List[IssueSchema]
    next_page: Optional[int] = None


class PullRequestList(BaseModel):
    pull_requests: List[PullRequestSchema]
    next_page: Optional[int] = None


class CommitList(BaseModel):
    commits: List[CommitSchema]
    next_page: Optional[int] = None


class ApiResponse(BaseModel):
    data: Optional[Union[RepositorySchema, RepositoryList, IssueSchema, IssueList, 
                         PullRequestSchema, PullRequestList, CommitSchema, CommitList]] = None
    component: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None
    message: Optional[str] = None


# Input schemas
class GetRepositoriesParams(BaseModel):
    username: Optional[str] = None
    type: Optional[str] = "all"  # all, owner, member
    sort: Optional[str] = "updated"  # created, updated, pushed, full_name
    direction: Optional[str] = "desc"  # asc, desc
    per_page: Optional[int] = 30
    page: Optional[int] = 1


class GetRepositoryParams(BaseModel):
    owner: str
    repo: str


class GetIssuesParams(BaseModel):
    owner: str
    repo: str
    state: Optional[str] = "open"  # open, closed, all
    sort: Optional[str] = "created"  # created, updated, comments
    direction: Optional[str] = "desc"  # asc, desc
    per_page: Optional[int] = 30
    page: Optional[int] = 1


class GetIssueParams(BaseModel):
    owner: str
    repo: str
    issue_number: int


class GetPullRequestsParams(BaseModel):
    owner: str
    repo: str
    state: Optional[str] = "open"  # open, closed, all
    sort: Optional[str] = "created"  # created, updated, popularity, long-running
    direction: Optional[str] = "desc"  # asc, desc
    per_page: Optional[int] = 30
    page: Optional[int] = 1


class GetPullRequestParams(BaseModel):
    owner: str
    repo: str
    pull_number: int


class GetCommitParams(BaseModel):
    owner: str
    repo: str
    commit_sha: str


class StarRepositoryParams(BaseModel):
    owner: str
    repo: str


class UnstarRepositoryParams(BaseModel):
    owner: str
    repo: str


class GetCommitsParams(BaseModel):
    owner: str
    repo: str
    sha: Optional[str] = None  # branch, tag, or commit SHA
    path: Optional[str] = None  # filter by file path
    author: Optional[str] = None  # filter by author
    since: Optional[str] = None  # ISO 8601 date
    until: Optional[str] = None  # ISO 8601 date
    per_page: Optional[int] = 30
    page: Optional[int] = 1


# Output schemas
class RepositoriesResponse(BaseModel):
    data: RepositoryList
    message: Optional[str] = None


class RepositoryResponse(BaseModel):
    data: RepositorySchema
    message: Optional[str] = None


class IssuesResponse(BaseModel):
    data: IssueList
    message: Optional[str] = None


class IssueResponse(BaseModel):
    data: IssueSchema
    message: Optional[str] = None


class PullRequestsResponse(BaseModel):
    data: PullRequestList
    message: Optional[str] = None


class PullRequestResponse(BaseModel):
    data: PullRequestSchema
    message: Optional[str] = None


class CommitResponse(BaseModel):
    data: CommitSchema
    message: Optional[str] = None


class StarResponse(BaseModel):
    message: str
    data: Optional[Any] = None


class UnstarResponse(BaseModel):
    message: str
    data: Optional[Any] = None


class CommitsResponse(BaseModel):
    data: CommitList
    message: Optional[str] = None