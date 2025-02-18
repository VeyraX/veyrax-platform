from fastapi import APIRouter, Depends, HTTPException, Query, Request as FastAPIRequest
from typing import Optional, List
import pickle
import os

from .schema import (
    IssueList, Issue, ProjectList, Project,
    IssueCreate, IssueUpdate, CommentCreate, IssueFilter, CommentResponse,
    UserList, TeamList, Team, WorkflowStateList
)
from .service import LinearService
from .client import LinearClient
from ..common.auth import TokenService

router = APIRouter(prefix="/linear", tags=["linear"])

async def get_linear_service(request: FastAPIRequest) -> LinearService:
    try:
        token_data = await TokenService.get_user_token(request, 'linear')
        if not token_data or not token_data.get('access_token'):
            raise HTTPException(
                status_code=401,
                detail="No Linear access token found"
            )
            
        client = LinearClient(token_data['access_token'])
        return LinearService(client)
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Failed to initialize Linear service: {str(e)}"
        )

@router.get(
    "/issues",
    response_model=IssueList,
    summary="List all issues",
    description="Retrieve a paginated list of Linear issues"
)
async def list_issues(
    cursor: Optional[str] = Query(None, description="Pagination cursor"),
    max_results: int = Query(50, ge=1, le=100, description="Maximum number of results to return"),
    service: LinearService = Depends(get_linear_service)
) -> IssueList:
    try:
        return service.list_issues(cursor, max_results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/issues/search",
    response_model=IssueList,
    summary="Search issues",
    description="Search Linear issues using a text query"
)
async def search_issues(
    query: str = Query(..., description="Search query string"),
    cursor: Optional[str] = Query(None, description="Pagination cursor"),
    max_results: int = Query(50, ge=1, le=100, description="Maximum number of results to return"),
    service: LinearService = Depends(get_linear_service)
) -> IssueList:
    try:
        return service.search_issues(query, cursor, max_results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post(
    "/issues/filter",
    response_model=IssueList,
    summary="Filter issues",
    description="Filter issues using various criteria"
)
async def filter_issues(
    filters: IssueFilter,
    cursor: Optional[str] = Query(None, description="Pagination cursor"),
    max_results: int = Query(50, ge=1, le=100, description="Maximum number of results to return"),
    service: LinearService = Depends(get_linear_service)
) -> IssueList:
    try:
        return service.filter_issues(filters, cursor, max_results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post(
    "/issues",
    response_model=Issue,
    status_code=201,
    summary="Create issue",
    description="Create a new Linear issue"
)
async def create_issue(
    issue: IssueCreate,
    service: LinearService = Depends(get_linear_service)
) -> Issue:
    try:
        return service.create_issue(issue)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch(
    "/issues/{issue_id}",
    response_model=Issue,
    summary="Update issue",
    description="Update an existing Linear issue"
)
async def update_issue(
    issue_id: str,
    issue_update: IssueUpdate,
    service: LinearService = Depends(get_linear_service)
) -> Issue:
    return service.update_issue(issue_id, issue_update)

@router.post(
    "/issues/{issue_id}/comments",
    response_model=CommentResponse,
    summary="Add comment",
    description="Add a comment to an existing Linear issue"
)
async def comment_issue(
    issue_id: str,
    comment: CommentCreate,
    service: LinearService = Depends(get_linear_service)
) -> CommentResponse:
    try:
        return service.comment_issue(issue_id, comment)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/projects",
    response_model=ProjectList,
    summary="List projects",
    description="Retrieve a paginated list of Linear projects"
)
async def list_projects(
    cursor: Optional[str] = Query(None, description="Pagination cursor"),
    max_results: int = Query(50, ge=1, le=100, description="Maximum number of results to return"),
    service: LinearService = Depends(get_linear_service)
) -> ProjectList:
    try:
        return service.list_projects(cursor, max_results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/users",
    response_model=UserList,
    summary="List users",
    description="Retrieve a paginated list of Linear users"
)
async def list_users(
    cursor: Optional[str] = Query(None, description="Pagination cursor"),
    max_results: int = Query(50, ge=1, le=100, description="Maximum number of results to return"),
    service: LinearService = Depends(get_linear_service)
) -> UserList:
    try:
        return service.list_users(cursor, max_results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/teams",
    response_model=TeamList,
    summary="List teams",
    description="Retrieve a paginated list of Linear teams"
)
async def list_teams(
    cursor: Optional[str] = Query(None, description="Pagination cursor"),
    max_results: int = Query(50, ge=1, le=100, description="Maximum number of results to return"),
    service: LinearService = Depends(get_linear_service)
) -> TeamList:
    try:
        return service.list_teams(cursor, max_results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/workflow-states",
    response_model=WorkflowStateList,
    summary="List workflow states",
    description="Retrieve a paginated list of Linear workflow states (statuses)"
)
async def list_workflow_states(
    cursor: Optional[str] = Query(None, description="Pagination cursor"),
    max_results: int = Query(50, ge=1, le=100, description="Maximum number of results to return"),
    service: LinearService = Depends(get_linear_service)
) -> WorkflowStateList:
    try:
        return service.list_workflow_states(cursor, max_results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))