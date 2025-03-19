import os
import yaml
import pickle
from typing import Dict, Any, Optional, Union
from fastapi import APIRouter, Body, Depends, HTTPException
from starlette.requests import Request as FastAPIRequest
from ..common.auth import TokenService
from ..common.input_schema_decorator import schema, input_schema, output_schema
from ..common.utils import apply_error_handler_to_service, apply_error_handler_to_router
from .client import GitHubClient
from .service import GitHubService
from .schema import (
    ApiResponse, GetRepositoriesParams, GetRepositoryParams, 
    GetIssuesParams, GetIssueParams, GetPullRequestsParams, 
    GetPullRequestParams, GetCommitParams, StarRepositoryParams, 
    UnstarRepositoryParams, GetGitTreeParams, GetRepositoryContentsParams,
    RepositoriesResponse, RepositoryResponse,
    IssuesResponse, IssueResponse, PullRequestsResponse, 
    PullRequestResponse, CommitResponse, StarResponse, UnstarResponse,
    GetCommitsParams, CommitsResponse, CreatePullRequestParams, 
    UpdatePullRequestParams, MergePullRequestParams, GetPullRequestReviewsParams,
    CreatePullRequestReviewParams, PullRequestReviewsResponse, 
    PullRequestReviewResponse, CreatePullRequestResponse, UpdatePullRequestResponse,
    MergePullRequestResponse, CreateRepositoryFromTemplateParams, CreateRepositoryFromTemplateResponse,
    GitTreeSchema, GitTreeEntry, GitTreeList, RepositoryContentSchema, RepositoryContentList,
    CreateBlobParams, CreateBlobResponse, GetBlobParams, GetBlobResponse,
    UpdateFileParams, FileUpdateResponse, GetRepositoryContentParams, RepositoryContentResponse,
    DeleteFileParams, CreateFileParams
)
from ..common.examples_handler import ExamplesLoader
from ..common.utils import apply_error_handler_to_client
router = APIRouter(prefix="/github", tags=["github"])

examples = ExamplesLoader()

async def get_github_service(request: FastAPIRequest):
    try:
        token_data = await TokenService.get_user_token(request, 'github')
        if not token_data or not token_data.get('access_token'):
            raise HTTPException(
                status_code=401,
                detail="No GitHub token data found"
            )
            
        client = GitHubClient(token_data['access_token'])
        apply_error_handler_to_client(client)
        service = GitHubService(client)
        
        apply_error_handler_to_service(service)
        
        return service
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Failed to initialize GitHub service: {str(e)}"
        )


@router.post("/get_repositories", response_model=ApiResponse)
@schema(input_schema_class=GetRepositoriesParams, output_schema_class=RepositoriesResponse, examples=examples["/github/repositories"])
async def get_repositories(
    params: Dict[str, Any] = Body({}),
    service: GitHubService = Depends(get_github_service)
):
    validated_params = GetRepositoriesParams(**params)
    return service.get_repositories(**validated_params.dict(exclude_unset=True))


@router.post("/get_repository", response_model=ApiResponse)
@schema(input_schema_class=GetRepositoryParams, output_schema_class=RepositoryResponse, examples=examples["/github/repository"])
async def get_repository(
    params: Dict[str, Any] = Body(...),
    service: GitHubService = Depends(get_github_service)
):
    validated_params = GetRepositoryParams(**params)
    return service.get_repository(**validated_params.dict())


@router.post("/get_issues", response_model=ApiResponse)
@schema(input_schema_class=GetIssuesParams, output_schema_class=IssuesResponse, examples=examples["/github/issues"])
async def get_issues(
    params: Dict[str, Any] = Body(...),
    service: GitHubService = Depends(get_github_service)
):
    validated_params = GetIssuesParams(**params)
    return service.get_issues(**validated_params.dict())


@router.post("/get_issue", response_model=ApiResponse)
@schema(input_schema_class=GetIssueParams, output_schema_class=IssueResponse, examples=examples["/github/issue"])
async def get_issue(
    params: Dict[str, Any] = Body(...),
    service: GitHubService = Depends(get_github_service)
):
    validated_params = GetIssueParams(**params)
    return service.get_issue(**validated_params.dict())


@router.post("/get_pull_requests", response_model=ApiResponse)
@schema(input_schema_class=GetPullRequestsParams, output_schema_class=PullRequestsResponse, examples=examples["/github/pull_requests"])
async def get_pull_requests(
    params: Dict[str, Any] = Body(...),
    service: GitHubService = Depends(get_github_service)
):
    validated_params = GetPullRequestsParams(**params)
    return service.get_pull_requests(**validated_params.dict())


@router.post("/get_pull_request", response_model=ApiResponse)
@schema(input_schema_class=GetPullRequestParams, output_schema_class=PullRequestResponse, examples=examples["/github/pull_request"])
async def get_pull_request(
    params: Dict[str, Any] = Body(...),
    service: GitHubService = Depends(get_github_service)
):
    validated_params = GetPullRequestParams(**params)
    return service.get_pull_request(**validated_params.dict())

@router.post("/get_commits", response_model=ApiResponse)
@schema(input_schema_class=GetCommitsParams, output_schema_class=CommitsResponse, examples=examples["/github/commits"])
async def get_commits(
    params: Dict[str, Any] = Body(...),
    service: GitHubService = Depends(get_github_service)
):
    validated_params = GetCommitsParams(**params)
    return service.get_commits(**validated_params.dict())


@router.post("/get_commit", response_model=ApiResponse)
@schema(input_schema_class=GetCommitParams, output_schema_class=CommitResponse, examples=examples["/github/commit"])
async def get_commit(
    params: Dict[str, Any] = Body(...),
    service: GitHubService = Depends(get_github_service)
):
    validated_params = GetCommitParams(**params)
    return service.get_commit(**validated_params.dict())


@router.post("/star_repository", response_model=ApiResponse)
@schema(input_schema_class=StarRepositoryParams, output_schema_class=StarResponse, examples=examples["/github/star"])
async def star_repository(
    params: Dict[str, Any] = Body(...),
    service: GitHubService = Depends(get_github_service)
):
    validated_params = StarRepositoryParams(**params)
    return service.star_repository(**validated_params.dict())


@router.post("/unstar_repository", response_model=ApiResponse)
@schema(input_schema_class=UnstarRepositoryParams, output_schema_class=UnstarResponse, examples=examples["/github/unstar"])
async def unstar_repository(
    params: Dict[str, Any] = Body(...),
    service: GitHubService = Depends(get_github_service)
):
    validated_params = UnstarRepositoryParams(**params)
    return service.unstar_repository(**validated_params.dict())


@router.post("/create_pull_request", response_model=ApiResponse)
@schema(input_schema_class=CreatePullRequestParams, output_schema_class=CreatePullRequestResponse, examples=examples["/create_pull_request"])
async def create_pull_request(
    params: Dict[str, Any] = Body(...),
    service: GitHubService = Depends(get_github_service)
):
    validated_params = CreatePullRequestParams(**params)
    return service.create_pull_request(**validated_params.dict())


@router.post("/update_pull_request", response_model=ApiResponse)
@schema(input_schema_class=UpdatePullRequestParams, output_schema_class=UpdatePullRequestResponse, examples=examples["/update_pull_request"])
async def update_pull_request(
    params: Dict[str, Any] = Body(...),
    service: GitHubService = Depends(get_github_service)
):
    validated_params = UpdatePullRequestParams(**params)
    return service.update_pull_request(**validated_params.dict())


@router.post("/merge_pull_request", response_model=ApiResponse)
@schema(input_schema_class=MergePullRequestParams, output_schema_class=MergePullRequestResponse, examples=examples["/merge_pull_request"])
async def merge_pull_request(
    params: Dict[str, Any] = Body(...),
    service: GitHubService = Depends(get_github_service)
):
    validated_params = MergePullRequestParams(**params)
    return service.merge_pull_request(**validated_params.dict())


@router.post("/get_pull_request_reviews", response_model=ApiResponse)
@schema(input_schema_class=GetPullRequestReviewsParams, output_schema_class=PullRequestReviewsResponse, examples=examples["/get_pull_request_reviews"])
async def get_pull_request_reviews(
    params: Dict[str, Any] = Body(...),
    service: GitHubService = Depends(get_github_service)
):
    validated_params = GetPullRequestReviewsParams(**params)
    return service.get_pull_request_reviews(**validated_params.dict())


@router.post("/create_pull_request_review", response_model=ApiResponse)
@schema(input_schema_class=CreatePullRequestReviewParams, output_schema_class=PullRequestReviewResponse, examples=examples["/create_pull_request_review"])
async def create_pull_request_review(
    params: Dict[str, Any] = Body(...),
    service: GitHubService = Depends(get_github_service)
):
    validated_params = CreatePullRequestReviewParams(**params)
    return service.create_pull_request_review(**validated_params.dict())


@router.post("/create_repository_from_template", response_model=ApiResponse)
@schema(
    input_schema_class=CreateRepositoryFromTemplateParams,
    output_schema_class=CreateRepositoryFromTemplateResponse,
    examples=examples["/create_repository_from_template"]
)
async def create_repository_from_template(
    params: Dict[str, Any] = Body(...),
    service: GitHubService = Depends(get_github_service)
):
    validated_params = CreateRepositoryFromTemplateParams(**params)
    return service.create_repository_from_template(
        template_owner=validated_params.template_owner,
        template_repo=validated_params.template_repo,
        owner=validated_params.owner,
        name=validated_params.name,
        description=validated_params.description,
        include_all_branches=validated_params.include_all_branches,
        private=validated_params.private
    )

@router.post("/get_git_tree", response_model=ApiResponse)
@schema(
    input_schema_class=GetGitTreeParams,
    output_schema_class=GitTreeSchema,
    examples=examples["/github/git_tree"]
)
async def get_git_tree(
    params: Dict[str, Any] = Body(...),
    service: GitHubService = Depends(get_github_service)
):
    validated_params = GetGitTreeParams(**params)
    return service.get_git_tree(**validated_params.dict())

@router.post("/get_repository_contents", response_model=ApiResponse)
@schema(
    input_schema_class=GetRepositoryContentsParams,
    output_schema_class=RepositoryContentSchema,
    examples=examples["/github/repository_contents"]
)
async def get_repository_contents(
    params: Dict[str, Any] = Body(...),
    service: GitHubService = Depends(get_github_service)
):
    validated_params = GetRepositoryContentsParams(**params)
    return service.get_repository_contents(**validated_params.dict())

@router.post("/create_blob", response_model=ApiResponse)
@schema(
    input_schema_class=CreateBlobParams,
    output_schema_class=CreateBlobResponse,
    examples=examples["/github/create_blob"]
)
async def create_blob(
    params: Dict[str, Any] = Body(...),
    service: GitHubService = Depends(get_github_service)
):
    validated_params = CreateBlobParams(**params)
    return service.create_blob(**validated_params.dict())

@router.post("/get_blob", response_model=ApiResponse)
@schema(
    input_schema_class=GetBlobParams,
    output_schema_class=GetBlobResponse,
    examples=examples["/github/get_blob"]
)
async def get_blob(
    params: Dict[str, Any] = Body(...),
    service: GitHubService = Depends(get_github_service)
):
    validated_params = GetBlobParams(**params)
    return service.get_blob(**validated_params.dict())

@router.post("/update_file", response_model=ApiResponse)
@schema(
    input_schema_class=UpdateFileParams,
    output_schema_class=FileUpdateResponse,
    examples=examples["/github/update_file"]
)
async def update_file(
    params: Dict[str, Any] = Body(...),
    service: GitHubService = Depends(get_github_service)
):
    validated_params = UpdateFileParams(**params)
    return service.update_file(
        owner=validated_params.owner,
        repo=validated_params.repo,
        path=validated_params.path,
        message=validated_params.message,
        content=validated_params.content,
        encoding=validated_params.encoding,
        sha=validated_params.sha,
        branch=validated_params.branch
    )


@router.post("/get_contents", response_model=ApiResponse)
@schema(
    input_schema_class=GetRepositoryContentParams,
    output_schema_class=RepositoryContentResponse,
    examples=examples["/github/get_contents"]
)
async def get_contents(
    params: Dict[str, Any] = Body(...),
    service: GitHubService = Depends(get_github_service)
):
    validated_params = GetRepositoryContentParams(**params)
    return service.get_repository_contents(
        owner=validated_params.owner,
        repo=validated_params.repo,
        path=validated_params.path,
        ref=validated_params.ref,
        decode_content=validated_params.decode_content
    )

@router.post("/delete_file", response_model=ApiResponse)
@schema(
    input_schema_class=DeleteFileParams,
    output_schema_class=FileUpdateResponse,
    examples=examples["/github/delete_file"]
)
async def delete_file(
    params: Dict[str, Any] = Body(...),
    service: GitHubService = Depends(get_github_service)
):
    validated_params = DeleteFileParams(**params)
    return service.delete_file(
        owner=validated_params.owner,
        repo=validated_params.repo,
        path=validated_params.path,
        message=validated_params.message,
        sha=validated_params.sha,
        branch=validated_params.branch,
        committer=validated_params.committer,
        author=validated_params.author
    )

@router.post("/create_file", response_model=ApiResponse)
@schema(
    input_schema_class=CreateFileParams,
    output_schema_class=FileUpdateResponse,
    examples=examples["/github/create_file"]
)
async def create_file(
    params: Dict[str, Any] = Body(...),
    service: GitHubService = Depends(get_github_service)
):
    validated_params = CreateFileParams(**params)
    return service.update_file(
        owner=validated_params.owner,
        repo=validated_params.repo,
        path=validated_params.path,
        message=validated_params.message,
        content=validated_params.content,
        encoding=validated_params.encoding,
        sha=None,
        branch=validated_params.branch
    )

apply_error_handler_to_router(router)