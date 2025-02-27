from fastapi import APIRouter, Depends, HTTPException, Request as FastAPIRequest, Body
from typing import Optional, List, Dict, Any
from .schema import (
    IssueList, Issue, ProjectList, Project,
    IssueCreate, IssueUpdate, CommentCreate, IssueFilter, CommentResponse,
    UserList, TeamList, Team, WorkflowStateList, ApiResponse,
    ListIssuesParams, SearchIssuesParams, FilterIssuesParams,
    CreateIssueParams, UpdateIssueParams, CommentIssueParams,
    ListProjectsParams, GetProjectParams, ListUsersParams,
    ListTeamsParams, GetTeamParams, ListWorkflowStatesParams
)
from .service import LinearService
from .client import LinearClient
from ..common.auth import TokenService
from ..common.input_schema_decorator import input_schema
from pydantic import ValidationError
from ..common.utils import format_validation_error

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
@input_schema(schema_class=ListIssuesParams)
async def list_issues(
    params: Dict[str, Any] = Body(...),
    service: LinearService = Depends(get_linear_service)
):
    try:
        validated_params = ListIssuesParams(**params)
        return service.list_issues(
            validated_params.cursor, 
            validated_params.max_results
        )
    except ValidationError as e:
            raise HTTPException(status_code=400, detail=format_validation_error(e, 'ListIssuesParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search_issues", response_model=ApiResponse)
@input_schema(schema_class=SearchIssuesParams)
async def search_issues(
    params: Dict[str, Any] = Body(...),
    service: LinearService = Depends(get_linear_service)
):
    try:
        validated_params = SearchIssuesParams(**params)
        return service.search_issues(
            validated_params.query,
            validated_params.cursor,
            validated_params.max_results
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'SearchIssuesParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/filter_issues", response_model=ApiResponse)
@input_schema(schema_class=FilterIssuesParams)
async def filter_issues(
    params: Dict[str, Any] = Body(...),
    service: LinearService = Depends(get_linear_service)
):
    try:
        validated_params = FilterIssuesParams(**params)
        return service.filter_issues(
            validated_params.filters,
            validated_params.cursor,
            validated_params.max_results
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'FilterIssuesParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create_issue", response_model=ApiResponse)
@input_schema(schema_class=CreateIssueParams)
async def create_issue(
    params: Dict[str, Any] = Body(...),
    service: LinearService = Depends(get_linear_service)
):
    try:
        validated_params = CreateIssueParams(**params)
        return service.create_issue(validated_params.issue)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'CreateIssueParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update_issue", response_model=ApiResponse)
@input_schema(schema_class=UpdateIssueParams)
async def update_issue(
    params: Dict[str, Any] = Body(...),
    service: LinearService = Depends(get_linear_service)
):
    try:
        validated_params = UpdateIssueParams(**params)
        return service.update_issue(
            validated_params.issue_id,
            validated_params.issue_update
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'UpdateIssueParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/comment_issue", response_model=ApiResponse)
@input_schema(schema_class=CommentIssueParams)
async def comment_issue(
    params: Dict[str, Any] = Body(...),
    service: LinearService = Depends(get_linear_service)
):
    try:
        validated_params = CommentIssueParams(**params)
        return service.comment_issue(
            validated_params.issue_id,
            validated_params.comment
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'CommentIssueParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/list_projects", response_model=ApiResponse)
@input_schema(schema_class=ListProjectsParams)
async def list_projects(
    params: Dict[str, Any] = Body(...),
    service: LinearService = Depends(get_linear_service)
):
    try:
        validated_params = ListProjectsParams(**params)
        return service.list_projects(
            validated_params.cursor,
            validated_params.max_results
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'ListProjectsParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_project", response_model=ApiResponse)
@input_schema(schema_class=GetProjectParams)
async def get_project(
    params: Dict[str, Any] = Body(...),
    service: LinearService = Depends(get_linear_service)
):
    try:
        validated_params = GetProjectParams(**params)
        return service.get_project(validated_params.project_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetProjectParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/list_users", response_model=ApiResponse)
@input_schema(schema_class=ListUsersParams)
async def list_users(
    params: Dict[str, Any] = Body(...),
    service: LinearService = Depends(get_linear_service)
):
    try:
        validated_params = ListUsersParams(**params)
        return service.list_users(
            validated_params.cursor,
            validated_params.max_results
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'ListUsersParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/list_teams", response_model=ApiResponse)
@input_schema(schema_class=ListTeamsParams)
async def list_teams(
    params: Dict[str, Any] = Body(...),
    service: LinearService = Depends(get_linear_service)
):
    try:
        validated_params = ListTeamsParams(**params)
        return service.list_teams(
            validated_params.cursor,
            validated_params.max_results
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'ListTeamsParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_team", response_model=ApiResponse)
@input_schema(schema_class=GetTeamParams)
async def get_team(
    params: Dict[str, Any] = Body(...),
    service: LinearService = Depends(get_linear_service)
):
    try:
        validated_params = GetTeamParams(**params)
        return service.get_team(validated_params.team_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetTeamParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/list_workflow_states", response_model=ApiResponse)
@input_schema(schema_class=ListWorkflowStatesParams)
async def list_workflow_states(
    params: Dict[str, Any] = Body(...),
    service: LinearService = Depends(get_linear_service)
):
    try:
        validated_params = ListWorkflowStatesParams(**params)
        return service.list_workflow_states(
            validated_params.cursor,
            validated_params.max_results
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'ListWorkflowStatesParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))