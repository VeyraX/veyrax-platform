from fastapi import APIRouter, Depends, HTTPException, Request as FastAPIRequest, Body
from typing import Optional, List, Dict, Any
import os
from .service import JiraService
from .client import JiraClient
from .schema import (
    ApiResponse,
    GetIssuesParams, GetIssueParams, CreateIssueParams,
    UpdateIssueParams, DeleteIssueParams, GetProjectParams,
    GetProjectsParams, GetStatusesParams, GetPrioritiesParams,
    GetIssueTypesParams, GetFieldsParams, GetUsersParams,
    GetIssuesResponse, GetIssueResponse, CreateIssueResponse,
    UpdateIssueResponse, DeleteIssueResponse, GetProjectsResponse,
    GetProjectResponse, GetStatusesResponse, GetPrioritiesResponse,
    GetIssueTypesResponse, GetFieldsResponse, GetUsersResponse,
    GetTransitionsParams, GetTransitionsResponse
)
from ..common.auth import TokenService, JiraTokenRefresher
from ..common.input_schema_decorator import schema
from pydantic import ValidationError
from ..common.utils import format_validation_error
from ..common.examples_handler import ExamplesLoader

router = APIRouter(prefix="/jira", tags=["jira"])

examples = ExamplesLoader()  # Will automatically use /integrations/jira directory

async def get_jira_service(request: FastAPIRequest):
    try:
        token_data = await TokenService.get_user_token(request, 'jira')
        
        if TokenService.is_token_expired(token_data):
            try:
                token_data = await JiraTokenRefresher.refresh(request, token_data)
            except Exception as e:
                raise HTTPException(status_code=401, detail="Failed to refresh token")
        
        client = JiraClient(token_data['access_token'])
        return JiraService(client)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize Jira service: {str(e)}")

@router.post("/get_issues", response_model=ApiResponse)
@schema(input_schema_class=GetIssuesParams, output_schema_class=GetIssuesResponse, examples=examples["/jira/get_issues"])
async def get_issues(
    params: Dict[str, Any] = Body(...),
    service: JiraService = Depends(get_jira_service)
):
    try:
        validated_params = GetIssuesParams(**params)
        return service.get_issues(validated_params.filters)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetIssuesParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_issue", response_model=ApiResponse)
@schema(input_schema_class=GetIssueParams, output_schema_class=GetIssueResponse, examples=examples["/jira/get_issue"])
async def get_issue(
    params: Dict[str, Any] = Body(...),
    service: JiraService = Depends(get_jira_service)
):
    try:
        validated_params = GetIssueParams(**params)
        return service.get_issue(validated_params.issue_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetIssueParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create_issue", response_model=ApiResponse)
@schema(input_schema_class=CreateIssueParams, output_schema_class=CreateIssueResponse, examples=examples["/jira/create_issue"])
async def create_issue(
    params: Dict[str, Any] = Body(...),
    service: JiraService = Depends(get_jira_service)
):
    try:
        validated_params = CreateIssueParams(**params)
        return service.create_issue(validated_params.issue_args)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'CreateIssueParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update_issue", response_model=ApiResponse)
@schema(input_schema_class=UpdateIssueParams, output_schema_class=UpdateIssueResponse, examples=examples["/jira/update_issue"])
async def update_issue(
    params: Dict[str, Any] = Body(...),
    service: JiraService = Depends(get_jira_service)
):
    try:
        validated_params = UpdateIssueParams(**params)
        return service.update_issue(
            validated_params.issue_id, 
            validated_params.update_args
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'UpdateIssueParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/delete_issue")
@schema(input_schema_class=DeleteIssueParams, output_schema_class=DeleteIssueResponse, examples=examples["/jira/delete_issue"])
async def delete_issue(
    params: Dict[str, Any] = Body(...),
    service: JiraService = Depends(get_jira_service)
):
    try:
        validated_params = DeleteIssueParams(**params)
        return service.delete_issue(validated_params.issue_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'DeleteIssueParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_projects", response_model=ApiResponse)
@schema(input_schema_class=GetProjectsParams, output_schema_class=GetProjectsResponse, examples=examples["/jira/get_projects"])
async def get_projects(
    params: Dict[str, Any] = Body(...),
    service: JiraService = Depends(get_jira_service)
):
    try:
        validated_params = GetProjectsParams(**params)
        return service.get_all_projects()
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetProjectsParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_project", response_model=ApiResponse)
@schema(input_schema_class=GetProjectParams, output_schema_class=GetProjectResponse, examples=examples["/jira/get_project"])
async def get_project(
    params: Dict[str, Any] = Body(...),
    service: JiraService = Depends(get_jira_service)
):
    try:
        validated_params = GetProjectParams(**params)
        return service.get_project_details(validated_params.project_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetProjectParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_statuses", response_model=ApiResponse)
@schema(input_schema_class=GetStatusesParams, output_schema_class=GetStatusesResponse, examples=examples["/jira/get_statuses"])
async def get_statuses(
    params: Dict[str, Any] = Body(...),
    service: JiraService = Depends(get_jira_service)
):
    try:
        return service.get_all_statuses()
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetStatusesParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_priorities", response_model=ApiResponse)
@schema(input_schema_class=GetPrioritiesParams, output_schema_class=GetPrioritiesResponse, examples=examples["/jira/get_priorities"])
async def get_priorities(
    params: Dict[str, Any] = Body(...),
    service: JiraService = Depends(get_jira_service)
):
    try:
        validated_params = GetPrioritiesParams(**params)
        return service.get_all_priorities()
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetPrioritiesParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_issue_types", response_model=ApiResponse)
@schema(input_schema_class=GetIssueTypesParams, output_schema_class=GetIssueTypesResponse, examples=examples["/jira/get_issue_types"])
async def get_issue_types(
    params: Dict[str, Any] = Body(...),
    service: JiraService = Depends(get_jira_service)
):
    try:
        validated_params = GetIssueTypesParams(**params)
        return service.get_all_issue_types()
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetIssueTypesParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_fields", response_model=ApiResponse)
@schema(input_schema_class=GetFieldsParams, output_schema_class=GetFieldsResponse, examples=examples["/jira/get_fields"])
async def get_fields(
    params: Dict[str, Any] = Body(...),
    service: JiraService = Depends(get_jira_service)
):
    try:
        validated_params = GetFieldsParams(**params)
        return service.get_all_fields()
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetFieldsParams'))
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error in get_fields: {str(e)}")
        print(f"Traceback: {error_trace}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_users", response_model=ApiResponse)
@schema(input_schema_class=GetUsersParams, output_schema_class=GetUsersResponse, examples=examples["/jira/get_users"])
async def get_users(
    params: Dict[str, Any] = Body(...),
    service: JiraService = Depends(get_jira_service)
):
    try:
        validated_params = GetUsersParams(**params)
        return service.get_users(validated_params.query)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetUsersParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_transitions", response_model=ApiResponse)
@schema(
    input_schema_class=GetTransitionsParams,
    output_schema_class=GetTransitionsResponse,
    examples=examples["/jira/get_transitions"]
)
async def get_transitions(
    params: Dict[str, Any] = Body(...),
    service: JiraService = Depends(get_jira_service)
):
    try:
        validated_params = GetTransitionsParams(**params)
        return service.get_allowed_transitions(validated_params.issue_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetTransitionsParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))