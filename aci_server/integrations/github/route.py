from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import ValidationError
from starlette.requests import Request as FastAPIRequest
from ..common.auth import TokenService
from ..common.input_schema_decorator import schema
from ..common.utils import format_validation_error
from .client import GitHubClient, GitHubAPIError
from .service import GitHubService
from .schema import (
    ApiResponse, GetRepositoriesParams, GetRepositoryParams, 
    GetIssuesParams, GetIssueParams, GetPullRequestsParams, 
    GetPullRequestParams, GetCommitParams, StarRepositoryParams, 
    UnstarRepositoryParams, RepositoriesResponse, RepositoryResponse,
    IssuesResponse, IssueResponse, PullRequestsResponse, 
    PullRequestResponse, CommitResponse, StarResponse, UnstarResponse,
    GetCommitsParams, CommitsResponse, CreatePullRequestParams, 
    UpdatePullRequestParams, MergePullRequestParams, GetPullRequestReviewsParams,
    CreatePullRequestReviewParams, PullRequestReviewsResponse, 
    PullRequestReviewResponse, CreatePullRequestResponse, UpdatePullRequestResponse,
    MergePullRequestResponse
)
from ..common.examples_handler import ExamplesLoader
router = APIRouter(prefix="/github", tags=["github"])

examples = ExamplesLoader()

async def get_github_service(request: FastAPIRequest):
    try:
        token_data = await TokenService.get_user_token(request, 'github')
        
        if TokenService.is_token_expired(token_data):
            try:
                token_data = await TokenService.refresh_token(request, token_data)
            except Exception as e:
                raise HTTPException(status_code=401, detail="Failed to refresh token")
        
        client = GitHubClient(token_data['access_token'])
        return GitHubService(client)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize GitHub service: {str(e)}")


def github_error_handler(func):
    async def wrapper(
        request: FastAPIRequest,
        params: Dict[str, Any] = Body(...),
        service: GitHubService = Depends(get_github_service)
    ):
        try:
            return await func(params, service)
            
        except ValidationError as e:
            schema_name = e.model.__name__ if hasattr(e, 'model') else 'Params'
            raise HTTPException(
                status_code=422,
                detail=format_validation_error(e, schema_name)
            )
            
        except HTTPException as he:
            raise he
        
        except GitHubAPIError as git_err:
            raise HTTPException(
                status_code=git_err.status_code,
                detail=git_err.message
            )
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error: {str(e)}"
            )
    return wrapper


@router.post("/get_repositories", response_model=ApiResponse)
@schema(input_schema_class=GetRepositoriesParams, output_schema_class=RepositoriesResponse, examples=examples["/github/repositories"])
@github_error_handler
async def get_repositories(params: Dict[str, Any], service: GitHubService = Depends(get_github_service)):
    validated_params = GetRepositoriesParams(**params)
    return service.get_repositories(**validated_params.dict())


@router.post("/get_repository", response_model=ApiResponse)
@schema(input_schema_class=GetRepositoryParams, output_schema_class=RepositoryResponse, examples=examples["/github/repository"])
@github_error_handler
async def get_repository(params: Dict[str, Any], service: GitHubService = Depends(get_github_service)):
    validated_params = GetRepositoryParams(**params)
    return service.get_repository(**validated_params.dict())


@router.post("/get_issues", response_model=ApiResponse)
@schema(input_schema_class=GetIssuesParams, output_schema_class=IssuesResponse, examples=examples["/github/issues"])
@github_error_handler
async def get_issues(params: Dict[str, Any], service: GitHubService = Depends(get_github_service)):
    validated_params = GetIssuesParams(**params)
    return service.get_issues(**validated_params.dict())


@router.post("/get_issue", response_model=ApiResponse)
@schema(input_schema_class=GetIssueParams, output_schema_class=IssueResponse, examples=examples["/github/issue"])
@github_error_handler
async def get_issue(params: Dict[str, Any], service: GitHubService = Depends(get_github_service)):
    validated_params = GetIssueParams(**params)
    return service.get_issue(**validated_params.dict())


@router.post("/get_pull_requests", response_model=ApiResponse)
@schema(input_schema_class=GetPullRequestsParams, output_schema_class=PullRequestsResponse, examples=examples["/github/pull_requests"])
@github_error_handler
async def get_pull_requests(params: Dict[str, Any], service: GitHubService):
    validated_params = GetPullRequestsParams(**params)
    return service.get_pull_requests(**validated_params.dict())


@router.post("/get_pull_request", response_model=ApiResponse)
@schema(input_schema_class=GetPullRequestParams, output_schema_class=PullRequestResponse, examples=examples["/github/pull_request"])
@github_error_handler
async def get_pull_request(params: Dict[str, Any], service: GitHubService = Depends(get_github_service)):
    validated_params = GetPullRequestParams(**params)
    return service.get_pull_request(**validated_params.dict())

@router.post("/get_commits", response_model=ApiResponse)
@schema(input_schema_class=GetCommitsParams, output_schema_class=CommitsResponse, examples=examples["/github/commits"])
@github_error_handler
async def get_commits(params: Dict[str, Any], service: GitHubService = Depends(get_github_service)):
    validated_params = GetCommitsParams(**params)
    return service.get_commits(**validated_params.dict())


@router.post("/get_commit", response_model=ApiResponse)
@schema(input_schema_class=GetCommitParams, output_schema_class=CommitResponse, examples=examples["/github/commit"])
@github_error_handler
async def get_commit(params: Dict[str, Any], service: GitHubService = Depends(get_github_service)):
    validated_params = GetCommitParams(**params)
    return service.get_commit(**validated_params.dict())


@router.post("/star_repository", response_model=ApiResponse)
@schema(input_schema_class=StarRepositoryParams, output_schema_class=StarResponse, examples=examples["/github/star"])
@github_error_handler
async def star_repository(params: Dict[str, Any], service: GitHubService = Depends(get_github_service)):
    validated_params = StarRepositoryParams(**params)
    return service.star_repository(**validated_params.dict())


@router.post("/unstar_repository", response_model=ApiResponse)
@schema(input_schema_class=UnstarRepositoryParams, output_schema_class=UnstarResponse, examples=examples["/github/unstar"])
@github_error_handler
async def unstar_repository(params: Dict[str, Any], service: GitHubService = Depends(get_github_service)):
    validated_params = UnstarRepositoryParams(**params)
    return service.unstar_repository(**validated_params.dict())


@router.post("/create_pull_request", response_model=ApiResponse)
@schema(input_schema_class=CreatePullRequestParams, output_schema_class=CreatePullRequestResponse, examples=examples["/create_pull_request"])
@github_error_handler
async def create_pull_request(params: Dict[str, Any], service: GitHubService = Depends(get_github_service)):
    validated_params = CreatePullRequestParams(**params)
    return service.create_pull_request(**validated_params.dict())


@router.post("/update_pull_request", response_model=ApiResponse)
@schema(input_schema_class=UpdatePullRequestParams, output_schema_class=UpdatePullRequestResponse, examples=examples["/update_pull_request"])
@github_error_handler
async def update_pull_request(params: Dict[str, Any], service: GitHubService = Depends(get_github_service)):
    validated_params = UpdatePullRequestParams(**params)
    return service.update_pull_request(**validated_params.dict())


@router.post("/merge_pull_request", response_model=ApiResponse)
@schema(input_schema_class=MergePullRequestParams, output_schema_class=MergePullRequestResponse, examples=examples["/merge_pull_request"])
@github_error_handler
async def merge_pull_request(params: Dict[str, Any], service: GitHubService = Depends(get_github_service)):
    validated_params = MergePullRequestParams(**params)
    return service.merge_pull_request(**validated_params.dict())


@router.post("/get_pull_request_reviews", response_model=ApiResponse)
@schema(input_schema_class=GetPullRequestReviewsParams, output_schema_class=PullRequestReviewsResponse, examples=examples["/get_pull_request_reviews"])
@github_error_handler
async def get_pull_request_reviews(params: Dict[str, Any], service: GitHubService = Depends(get_github_service)):
    validated_params = GetPullRequestReviewsParams(**params)
    return service.get_pull_request_reviews(**validated_params.dict())


@router.post("/create_pull_request_review", response_model=ApiResponse)
@schema(input_schema_class=CreatePullRequestReviewParams, output_schema_class=PullRequestReviewResponse, examples=examples["/create_pull_request_review"])
@github_error_handler
async def create_pull_request_review(params: Dict[str, Any], service: GitHubService = Depends(get_github_service)):
    validated_params = CreatePullRequestReviewParams(**params)
    return service.create_pull_request_review(**validated_params.dict())
