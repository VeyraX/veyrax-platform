from fastapi import APIRouter, Depends, HTTPException, Request as FastAPIRequest, Body
from typing import Optional, List, Dict, Any
import os
import pickle
from datetime import datetime
from .service import JiraService
from .client import JiraClient
from .schema import (
    IssueList, Issue, IssueCreate, IssueUpdate, 
    IssueFilters, JiraServerInfo, JiraCredentials,
    Project, Status, Priority, IssueType, Field,
    JiraUser, ApiResponse
)
from ..common.auth import TokenService, JiraTokenRefresher

router = APIRouter(prefix="/jira", tags=["jira"])

async def get_jira_service(request: FastAPIRequest):
    token_data = await TokenService.get_user_token(request, 'jira')
    
    if TokenService.is_token_expired(token_data):
        try:
            token_data = await JiraTokenRefresher.refresh(request, token_data)
        except Exception as e:
            raise HTTPException(status_code=401, detail="Failed to refresh token")
    
    client = JiraClient(token_data['access_token'])
    return JiraService(client)

@router.post("/get_issues", response_model=ApiResponse)
async def get_issues(
    params: Dict[str, Any] = Body(...),
    service: JiraService = Depends(get_jira_service)
):
    try:
        filters_data = params.get('filters', {})
        filters = IssueFilters(**filters_data)
        return service.get_issues(filters)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_issue", response_model=ApiResponse)
async def get_issue(
    params: Dict[str, Any] = Body(...),
    service: JiraService = Depends(get_jira_service)
):
    try:
        issue_id = params.get('issue_id')
        if not issue_id:
            raise HTTPException(status_code=400, detail="issue_id is required")
        return service.get_issue(issue_id)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create_issue", response_model=ApiResponse)
async def create_issue(
    params: Dict[str, Any] = Body(...),
    service: JiraService = Depends(get_jira_service)
):
    try:
        issue_data = params.get('issue_args', params)
        issue_args = IssueCreate(**issue_data)
        return service.create_issue(issue_args)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update_issue", response_model=ApiResponse)
async def update_issue(
    params: Dict[str, Any] = Body(...),
    service: JiraService = Depends(get_jira_service)
):
    try:
        issue_id = params.get('issue_id')
        update_data = params.get('update_args', {})
        
        if not issue_id:
            raise HTTPException(status_code=400, detail="issue_id is required")
            
        update_args = IssueUpdate(**update_data)
        return service.update_issue(issue_id, update_args)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/delete_issue")
async def delete_issue(
    params: Dict[str, Any] = Body(...),
    service: JiraService = Depends(get_jira_service)
):
    try:
        issue_id = params.get('issue_id')
        if not issue_id:
            raise HTTPException(status_code=400, detail="issue_id is required")
            
        return service.delete_issue(issue_id)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_projects", response_model=ApiResponse)
async def get_projects(
    params: Dict[str, Any] = Body(...),
    service: JiraService = Depends(get_jira_service)
):
    try:
        return service.get_all_projects()
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_project", response_model=ApiResponse)
async def get_project(
    params: Dict[str, Any] = Body(...),
    service: JiraService = Depends(get_jira_service)
):
    try:
        project_id = params.get('project_id')
        if not project_id:
            raise HTTPException(status_code=400, detail="project_id is required")
        return service.get_project_details(project_id)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_statuses", response_model=ApiResponse)
async def get_statuses(
    params: Dict[str, Any] = Body(...),
    service: JiraService = Depends(get_jira_service)
):
    try:
        return service.get_all_statuses()
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_priorities", response_model=ApiResponse)
async def get_priorities(
    params: Dict[str, Any] = Body(...),
    service: JiraService = Depends(get_jira_service)
):
    try:
        return service.get_all_priorities()
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_issue_types", response_model=ApiResponse)
async def get_issue_types(
    params: Dict[str, Any] = Body(...),
    service: JiraService = Depends(get_jira_service)
):
    try:
        return service.get_all_issue_types()
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_fields", response_model=ApiResponse)
async def get_fields(
    params: Dict[str, Any] = Body(...),
    service: JiraService = Depends(get_jira_service)
):
    try:
        return service.get_all_fields()
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error in get_fields: {str(e)}")
        print(f"Traceback: {error_trace}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_users", response_model=ApiResponse)
async def get_users(
    params: Dict[str, Any] = Body(...),
    service: JiraService = Depends(get_jira_service)
):
    try:
        query = params.get('query')
        return service.get_users(query)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))