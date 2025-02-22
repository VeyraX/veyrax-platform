from fastapi import APIRouter, Depends, HTTPException, Request as FastAPIRequest
from typing import Optional, List
import os
import pickle
from datetime import datetime
from .service import JiraService
from .client import JiraClient
from .schema import (
    IssueList, Issue, IssueCreate, IssueUpdate, 
    IssueFilters, JiraServerInfo, JiraCredentials,
    Project, Status, Priority, IssueType, Field,
    JiraUser
)
from ..common.auth import TokenService

router = APIRouter(prefix="/jira", tags=["jira"])

async def get_jira_service(request: FastAPIRequest):
    token_data = await TokenService.get_user_token(request, 'jira')
    client = JiraClient(token_data['access_token'])
    return JiraService(client)

@router.get("/issues", response_model=IssueList)
async def get_issues(
    filters: IssueFilters = Depends(),
    service: JiraService = Depends(get_jira_service)
):
    return service.get_issues(filters)

@router.get("/issues/{issue_id}", response_model=Issue)
async def get_issue(
    issue_id: str,
    service: JiraService = Depends(get_jira_service)
):
    return service.get_issue(issue_id)

@router.post("/issues", response_model=Issue)
async def create_issue(
    issue: IssueCreate,
    service: JiraService = Depends(get_jira_service)
):
    return service.create_issue(issue)

@router.patch("/issues/{issue_id}", response_model=Issue)
async def update_issue(
    issue_id: str,
    update: IssueUpdate,
    service: JiraService = Depends(get_jira_service)
):
    return service.update_issue(issue_id, update)

@router.delete("/issues/{issue_id}")
async def delete_issue(
    issue_id: str,
    service: JiraService = Depends(get_jira_service)
):
    service.delete_issue(issue_id)
    return {"status": "success"}

@router.get("/projects", response_model=List[Project])
async def get_projects(
    service: JiraService = Depends(get_jira_service)
):
    return service.get_all_projects()

@router.get("/projects/{project_id}", response_model=Project)
async def get_project(
    project_id: str,
    service: JiraService = Depends(get_jira_service)
):
    return service.get_project_details(project_id)

@router.get("/statuses", response_model=List[Status])
async def get_statuses(
    service: JiraService = Depends(get_jira_service)
):
    return service.get_all_statuses()

@router.get("/priorities", response_model=List[Priority])
async def get_priorities(
    service: JiraService = Depends(get_jira_service)
):
    return service.get_all_priorities()

@router.get("/issue-types", response_model=List[IssueType])
async def get_issue_types(
    service: JiraService = Depends(get_jira_service)
):
    return service.get_all_issue_types()

@router.get("/fields", response_model=List[Field])
async def get_fields(
    service: JiraService = Depends(get_jira_service)
):
    return service.get_all_fields()

@router.get("/users", response_model=List[JiraUser])
async def get_users(
    query: Optional[str] = None,
    service: JiraService = Depends(get_jira_service)
):
    return service.get_users(query)