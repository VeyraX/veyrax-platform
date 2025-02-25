from fastapi import APIRouter, Depends, HTTPException, Request as FastAPIRequest, Body
from typing import Optional, List, Dict, Any
import pickle
import os

from .schema import (
    IssueList, Issue, ProjectList, Project,
    IssueCreate, IssueUpdate, CommentCreate, IssueFilter, CommentResponse,
    UserList, TeamList, Team, WorkflowStateList, ApiResponse
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

@router.post("/list_issues", response_model=ApiResponse)
async def list_issues(
    params: Dict[str, Any] = Body(...),
    service: LinearService = Depends(get_linear_service)
):
    try:
        cursor = params.get('cursor')
        max_results = params.get('max_results', 50)
        
        result = service.list_issues(cursor, max_results)
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search_issues", response_model=ApiResponse)
async def search_issues(
    params: Dict[str, Any] = Body(...),
    service: LinearService = Depends(get_linear_service)
):
    try:
        query = params.get('query')
        cursor = params.get('cursor')
        max_results = params.get('max_results', 50)
        
        result = service.search_issues(query, cursor, max_results)
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/filter_issues", response_model=ApiResponse)
async def filter_issues(
    params: Dict[str, Any] = Body(...),
    service: LinearService = Depends(get_linear_service)
):
    try:
        filters_data = params.get('filters', {})
        cursor = params.get('cursor')
        max_results = params.get('max_results', 50)
        
        filters = IssueFilter(**filters_data)
        result = service.filter_issues(filters, cursor, max_results)
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create_issue", response_model=ApiResponse)
async def create_issue(
    params: Dict[str, Any] = Body(...),
    service: LinearService = Depends(get_linear_service)
):
    try:
        issue_data = params.get('issue', params)
        
        issue = IssueCreate(**issue_data)
        result = service.create_issue(issue)
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update_issue", response_model=ApiResponse)
async def update_issue(
    params: Dict[str, Any] = Body(...),
    service: LinearService = Depends(get_linear_service)
):
    try:
        issue_id = params.get('issue_id')
        issue_data = params.get('issue_update', {})
        
        issue_update = IssueUpdate(**issue_data)
        result = service.update_issue(issue_id, issue_update)
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/comment_issue", response_model=ApiResponse)
async def comment_issue(
    params: Dict[str, Any] = Body(...),
    service: LinearService = Depends(get_linear_service)
):
    try:
        issue_id = params.get('issue_id')
        comment_data = params.get('comment', {})
        
        comment = CommentCreate(**comment_data)
        result = service.comment_issue(issue_id, comment)
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/list_projects", response_model=ApiResponse)
async def list_projects(
    params: Dict[str, Any] = Body(...),
    service: LinearService = Depends(get_linear_service)
):
    try:
        cursor = params.get('cursor')
        max_results = params.get('max_results', 50)
        
        result = service.list_projects(cursor, max_results)
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_project", response_model=ApiResponse)
async def get_project(
    params: Dict[str, Any] = Body(...),
    service: LinearService = Depends(get_linear_service)
):
    try:
        project_id = params.get('project_id')
        
        result = service.get_project(project_id)
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/list_users", response_model=ApiResponse)
async def list_users(
    params: Dict[str, Any] = Body(...),
    service: LinearService = Depends(get_linear_service)
):
    try:
        cursor = params.get('cursor')
        max_results = params.get('max_results', 50)
        
        result = service.list_users(cursor, max_results)
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/list_teams", response_model=ApiResponse)
async def list_teams(
    params: Dict[str, Any] = Body(...),
    service: LinearService = Depends(get_linear_service)
):
    try:
        cursor = params.get('cursor')
        max_results = params.get('max_results', 50)
        
        result = service.list_teams(cursor, max_results)
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_team", response_model=ApiResponse)
async def get_team(
    params: Dict[str, Any] = Body(...),
    service: LinearService = Depends(get_linear_service)
):
    try:
        team_id = params.get('team_id')
        
        result = service.get_team(team_id)
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/list_workflow_states", response_model=ApiResponse)
async def list_workflow_states(
    params: Dict[str, Any] = Body(...),
    service: LinearService = Depends(get_linear_service)
):
    try:
        cursor = params.get('cursor')
        max_results = params.get('max_results', 50)
        
        result = service.list_workflow_states(cursor, max_results)
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))