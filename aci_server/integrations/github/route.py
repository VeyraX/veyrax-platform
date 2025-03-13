import os
import yaml
import pickle
from typing import Dict, Any, Optional
from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import ValidationError
from starlette.requests import Request as FastAPIRequest
from ..common.auth import TokenService
from ..common.input_schema_decorator import schema, input_schema, output_schema
from ..common.utils import format_validation_error
from .client import GitHubClient
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


@router.post("/get_repositories", response_model=ApiResponse)
@schema(input_schema_class=GetRepositoriesParams, output_schema_class=RepositoriesResponse, examples=examples["/github/repositories"])
async def get_repositories(
    params: Dict[str, Any] = Body({}),
    service: GitHubService = Depends(get_github_service)
):
    try:
        validated_params = GetRepositoriesParams(**params)
        return service.get_repositories(**validated_params.dict())
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetRepositoriesParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/get_repository", response_model=ApiResponse)
@schema(input_schema_class=GetRepositoryParams, output_schema_class=RepositoryResponse, examples=examples["/github/repository"])
async def get_repository(
    params: Dict[str, Any] = Body(...),
    service: GitHubService = Depends(get_github_service)
):
    try:
        validated_params = GetRepositoryParams(**params)
        return service.get_repository(**validated_params.dict())
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetRepositoryParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/get_issues", response_model=ApiResponse)
@schema(input_schema_class=GetIssuesParams, output_schema_class=IssuesResponse, examples=examples["/github/issues"])
async def get_issues(
    params: Dict[str, Any] = Body(...),
    service: GitHubService = Depends(get_github_service)
):
    try:
        validated_params = GetIssuesParams(**params)
        return service.get_issues(**validated_params.dict())
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetIssuesParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/get_issue", response_model=ApiResponse)
@schema(input_schema_class=GetIssueParams, output_schema_class=IssueResponse, examples=examples["/github/issue"])
async def get_issue(
    params: Dict[str, Any] = Body(...),
    service: GitHubService = Depends(get_github_service)
):
    try:
        validated_params = GetIssueParams(**params)
        return service.get_issue(**validated_params.dict())
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetIssueParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/get_pull_requests", response_model=ApiResponse)
@schema(input_schema_class=GetPullRequestsParams, output_schema_class=PullRequestsResponse, examples=examples["/github/pull_requests"])
async def get_pull_requests(
    params: Dict[str, Any] = Body(...),
    service: GitHubService = Depends(get_github_service)
):
    try:
        validated_params = GetPullRequestsParams(**params)
        return service.get_pull_requests(**validated_params.dict())
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetPullRequestsParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/get_pull_request", response_model=ApiResponse)
@schema(input_schema_class=GetPullRequestParams, output_schema_class=PullRequestResponse, examples=examples["/github/pull_request"])
async def get_pull_request(
    params: Dict[str, Any] = Body(...),
    service: GitHubService = Depends(get_github_service)
):
    try:
        validated_params = GetPullRequestParams(**params)
        return service.get_pull_request(**validated_params.dict())
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetPullRequestParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_commits", response_model=ApiResponse)
@schema(input_schema_class=GetCommitsParams, output_schema_class=CommitsResponse, examples=examples["/github/commits"])
async def get_commits(
    params: Dict[str, Any] = Body(...),
    service: GitHubService = Depends(get_github_service)
):
    try:
        validated_params = GetCommitsParams(**params)
        return service.get_commits(**validated_params.dict())
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetCommitsParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/get_commit", response_model=ApiResponse)
@schema(input_schema_class=GetCommitParams, output_schema_class=CommitResponse, examples=examples["/github/commit"])
async def get_commit(
    params: Dict[str, Any] = Body(...),
    service: GitHubService = Depends(get_github_service)
):
    try:
        validated_params = GetCommitParams(**params)
        return service.get_commit(**validated_params.dict())
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetCommitParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/star_repository", response_model=ApiResponse)
@schema(input_schema_class=StarRepositoryParams, output_schema_class=StarResponse, examples=examples["/github/star"])
async def star_repository(
    params: Dict[str, Any] = Body(...),
    service: GitHubService = Depends(get_github_service)
):
    try:
        validated_params = StarRepositoryParams(**params)
        return service.star_repository(**validated_params.dict())
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'StarRepositoryParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/unstar_repository", response_model=ApiResponse)
@schema(input_schema_class=UnstarRepositoryParams, output_schema_class=UnstarResponse, examples=examples["/github/unstar"])
async def unstar_repository(
    params: Dict[str, Any] = Body(...),
    service: GitHubService = Depends(get_github_service)
):
    try:
        validated_params = UnstarRepositoryParams(**params)
        return service.unstar_repository(**validated_params.dict())
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'UnstarRepositoryParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create_pull_request", response_model=ApiResponse)
@schema(input_schema_class=CreatePullRequestParams, output_schema_class=CreatePullRequestResponse, examples=examples["/create_pull_request"])
async def create_pull_request(
    params: Dict[str, Any] = Body(...),
    service: GitHubService = Depends(get_github_service)
):
    try:
        validated_params = CreatePullRequestParams(**params)
        return service.create_pull_request(**validated_params.dict())
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'CreatePullRequestParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update_pull_request", response_model=ApiResponse)
@schema(input_schema_class=UpdatePullRequestParams, output_schema_class=UpdatePullRequestResponse, examples=examples["/update_pull_request"])
async def update_pull_request(
    params: Dict[str, Any] = Body(...),
    service: GitHubService = Depends(get_github_service)
):
    try:
        validated_params = UpdatePullRequestParams(**params)
        return service.update_pull_request(**validated_params.dict())
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'UpdatePullRequestParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/merge_pull_request", response_model=ApiResponse)
@schema(input_schema_class=MergePullRequestParams, output_schema_class=MergePullRequestResponse, examples=examples["/merge_pull_request"])
async def merge_pull_request(
    params: Dict[str, Any] = Body(...),
    service: GitHubService = Depends(get_github_service)
):
    try:
        validated_params = MergePullRequestParams(**params)
        return service.merge_pull_request(**validated_params.dict())
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'MergePullRequestParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/get_pull_request_reviews", response_model=ApiResponse)
@schema(input_schema_class=GetPullRequestReviewsParams, output_schema_class=PullRequestReviewsResponse, examples=examples["/get_pull_request_reviews"])
async def get_pull_request_reviews(
    params: Dict[str, Any] = Body(...),
    service: GitHubService = Depends(get_github_service)
):
    try:
        validated_params = GetPullRequestReviewsParams(**params)
        return service.get_pull_request_reviews(**validated_params.dict())
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetPullRequestReviewsParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create_pull_request_review", response_model=ApiResponse)
@schema(input_schema_class=CreatePullRequestReviewParams, output_schema_class=PullRequestReviewResponse, examples=examples["/create_pull_request_review"])
async def create_pull_request_review(
    params: Dict[str, Any] = Body(...),
    service: GitHubService = Depends(get_github_service)
):
    try:
        validated_params = CreatePullRequestReviewParams(**params)
        return service.create_pull_request_review(**validated_params.dict())
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'CreatePullRequestReviewParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))