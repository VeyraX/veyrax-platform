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


class PullRequestReviewSchema(BaseModel):
    id: int
    user: Dict[str, Any]
    body: Optional[str] = None
    state: str  # APPROVED, CHANGES_REQUESTED, COMMENTED, DISMISSED, PENDING
    html_url: str
    submitted_at: Optional[str] = None
    commit_id: str


class PullRequestReviewList(BaseModel):
    reviews: List[PullRequestReviewSchema]
    next_page: Optional[int] = None




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


class CreatePullRequestParams(BaseModel):
    owner: str
    repo: str
    title: str
    head: str  # The name of the branch where your changes are implemented
    base: str  # The name of the branch you want the changes pulled into
    body: Optional[str] = None
    draft: Optional[bool] = False


class UpdatePullRequestParams(BaseModel):
    owner: str
    repo: str
    pull_number: int
    title: Optional[str] = None
    body: Optional[str] = None
    state: Optional[str] = None  # open, closed
    base: Optional[str] = None  # The name of the branch you want the changes pulled into
    maintainer_can_modify: Optional[bool] = Field(
        default=None, 
        description="Indicates whether maintainers can modify the pull request. Note: This parameter can only be set on cross-repo pull requests (pull requests from a fork). Using this parameter on same-repo pull requests will result in a 422 error."
    )


class MergePullRequestParams(BaseModel):
    owner: str
    repo: str
    pull_number: int
    commit_title: Optional[str] = None
    commit_message: Optional[str] = None
    merge_method: Optional[str] = "merge"  # merge, squash, rebase


class GetPullRequestReviewsParams(BaseModel):
    owner: str
    repo: str
    pull_number: int


class CreatePullRequestReviewParams(BaseModel):
    owner: str
    repo: str
    pull_number: int
    body: Optional[str] = None
    event: Optional[str] = None  # APPROVE, REQUEST_CHANGES, COMMENT
    comments: Optional[List[Dict[str, Any]]] = None


# Input schema
class CreateRepositoryFromTemplateParams(BaseModel):
    template_owner: str
    template_repo: str
    owner: Optional[str] = None
    name: str
    description: Optional[str] = None
    include_all_branches: Optional[bool] = False
    private: Optional[bool] = False


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


class PullRequestReviewsResponse(BaseModel):
    data: PullRequestReviewList
    message: Optional[str] = None


class PullRequestReviewResponse(BaseModel):
    data: PullRequestReviewSchema
    message: Optional[str] = None


class CreatePullRequestResponse(BaseModel):
    data: PullRequestSchema
    message: Optional[str] = None


class UpdatePullRequestResponse(BaseModel):
    data: PullRequestSchema
    message: Optional[str] = None


class MergePullRequestResponse(BaseModel):
    message: str
    data: Optional[Dict[str, Any]] = None


class CreateRepositoryFromTemplateResponse(BaseModel):
    data: RepositorySchema
    message: Optional[str] = None


class GitTreeEntry(BaseModel):
    path: str
    mode: str
    type: str  # blob, tree, commit
    sha: str
    size: Optional[int] = None
    url: Optional[str] = None


class GitTreeSchema(BaseModel):
    sha: str
    url: str
    tree: List[GitTreeEntry]
    truncated: bool


class GitTreeList(BaseModel):
    trees: List[GitTreeSchema]
    next_page: Optional[int] = None


class RepositoryContentSchema(BaseModel):
    type: str  # file, dir, symlink, submodule
    encoding: Optional[str] = None
    size: int
    name: str
    path: str
    content: Optional[str] = None
    sha: str
    url: str
    git_url: Optional[str] = None
    html_url: Optional[str] = None
    download_url: Optional[str] = None
    _links: Dict[str, Any]


class RepositoryContentList(BaseModel):
    contents: List[RepositoryContentSchema]
    next_page: Optional[int] = None


# Input schemas
class GetGitTreeParams(BaseModel):
    owner: str
    repo: str
    tree_sha: str
    recursive: bool = False


class GetRepositoryContentsParams(BaseModel):
    owner: str
    repo: str
    path: str
    ref: Optional[str] = None
    decode_content: Optional[bool] = Field(
        True, 
        description="Whether to automatically decode base64 content"
    )


class GitTreeResponse(BaseModel):
    data: GitTreeSchema
    message: Optional[str] = None


class RepositoryContentResponse(BaseModel):
    data: Union[RepositoryContentSchema, RepositoryContentList]
    message: Optional[str] = None


# Add to Input schemas section
class CreateBlobParams(BaseModel):
    owner: str
    repo: str
    content: str
    encoding: Optional[str] = "utf-8"

class GetBlobParams(BaseModel):
    owner: str
    repo: str
    file_sha: str
    auto_decode: Optional[bool] = Field(
        True, 
        description="Whether to automatically decode base64 content. Only applies when encoding is base64"
    )

# Add to Output schemas section
class CreateBlobResponse(BaseModel):
    url: str
    sha: str

class GetBlobResponse(BaseModel):
    content: str
    encoding: str
    url: str
    sha: str
    decoded_content: Optional[str] = Field(
        None,
        description="Automatically decoded content when auto_decode=true and encoding is base64"
    )


class CommitAuthor(BaseModel):
    name: str
    email: str
    date: str

class CommitTree(BaseModel):
    sha: str
    url: str

class CommitParent(BaseModel):
    sha: str
    url: str
    html_url: str

class CommitVerification(BaseModel):
    verified: bool
    reason: str
    signature: Optional[str] = None
    payload: Optional[str] = None

class CommitDetail(BaseModel):
    author: CommitAuthor
    committer: CommitAuthor
    message: str
    tree: CommitTree
    url: str
    comment_count: Optional[int] = Field(0)
    verification: CommitVerification

class FileUpdateResponse(BaseModel):
    content: Optional[Dict[str, Any]] = None
    commit: CommitDetail
    message: Optional[str] = None



# Update ApiResponse model
class ApiResponse(BaseModel):
    data: Optional[Union[RepositorySchema, RepositoryList, IssueSchema, IssueList, 
                         PullRequestSchema, PullRequestList, CommitSchema, CommitList,
                         PullRequestReviewSchema, PullRequestReviewList, GitTreeSchema, GitTreeList,
                         RepositoryContentSchema, RepositoryContentList, CreateBlobResponse, GetBlobResponse, FileUpdateResponse]] = None
    component: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None
    message: Optional[str] = None

class CreateFileParams(BaseModel):
    owner: str
    repo: str
    path: str
    message: str
    content: str
    encoding: Optional[str] = Field("utf-8", description="Input encoding: 'utf-8' or 'base64'")
    branch: Optional[str] = None

class UpdateFileParams(BaseModel):
    owner: str
    repo: str
    path: str
    message: str
    content: str
    encoding: Optional[str] = Field("utf-8", description="Input encoding: 'utf-8' or 'base64'")
    sha: str = Field(..., description="Required for updates")
    branch: Optional[str] = None

# Add to Input schemas section
class GetRepositoryContentParams(BaseModel):
    owner: str
    repo: str
    path: str
    ref: Optional[str] = None
    decode_content: Optional[bool] = Field(
        True, 
        description="Whether to automatically decode base64 content"
    )

class DeleteFileParams(BaseModel):
    owner: str
    repo: str
    path: str
    message: str
    sha: str
    branch: Optional[str] = None
    committer: Optional[Dict[str, str]] = Field(
        None,
        description="Committer information (name and email)"
    )
    author: Optional[Dict[str, str]] = Field(
        None,
        description="Author information (name and email)"
    )