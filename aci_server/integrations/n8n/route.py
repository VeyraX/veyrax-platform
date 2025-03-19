from fastapi import APIRouter, Depends, Body, HTTPException, Request
from typing import Dict, Any, Optional, List
from .schema import (
    ListUsersParams,
    GetUserParams,
    CreateUsersParams,
    DeleteUserParams,
    UpdateUserRoleParams,
    ListExecutionsParams,
    GetExecutionParams,
    DeleteExecutionParams,
    ApiResponse,
    User,
    UsersList,
    Execution,
    ExecutionsList,
    SuccessResponse,
    EmptyRequestBody,
    Workflow,
    WorkflowsList,
    ListWorkflowsParams,
    GetWorkflowParams,
    CreateWorkflowParams,
    UpdateWorkflowParams,
    DeleteWorkflowParams,
    ActivateWorkflowParams,
    CopyWorkflowParams,
    TagsList,
    ListCredentialsParams,
    Credential,
    CredentialsList,
    CreateCredentialParams,
    DeleteCredentialParams,
    GetCredentialTypeParams,
    CredentialTypeSchema,
    CreateTagParams,
    DeleteTagParams,
    UpdateTagParams,
    Tag,
    PullOptions,
    PullResult,
    Variable,
    VariablesList,
    CreateVariableParams,
    DeleteVariableParams,
    ListVariablesParams,
    Project,
    ProjectsList,
    CreateProjectParams,
    UpdateProjectParams,
    DeleteProjectParams,
    ListProjectsParams
)
from .service import N8nService
from .client import N8nClient
from ..common.auth import validate_provider_api_key
from ..common.input_schema_decorator import schema
from ..common.utils import apply_error_handler_to_service, apply_error_handler_to_router
from ..common.examples_handler import ExamplesLoader
from ..common.auth import get_custom_base_url

router = APIRouter(prefix="/n8n", tags=["n8n"])
examples = ExamplesLoader()

async def get_n8n_service(request: Request):
    try:
        api_key = await validate_provider_api_key(request, "n8n")
        base_url = await get_custom_base_url(request, "n8n")
        client = N8nClient(api_key, base_url)
        service = N8nService(client)
        apply_error_handler_to_service(service)
        return service
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"N8n service initialization failed: {str(e)}")

# Users routes
@router.post("/list_users", response_model=ApiResponse)
@schema(
    input_schema_class=ListUsersParams,
    output_schema_class=UsersList,
    examples=examples["/n8n/list_users"]
)
async def list_users(
    params: Dict[str, Any] = Body(...),
    service: N8nService = Depends(get_n8n_service)
):
    validated_params = ListUsersParams(**params)
    return service.list_users(validated_params)

@router.post("/get_user", response_model=ApiResponse)
@schema(
    input_schema_class=GetUserParams,
    output_schema_class=User,
    examples=examples["/n8n/get_user"]
)
async def get_user(
    params: Dict[str, Any] = Body(...),
    service: N8nService = Depends(get_n8n_service)
):
    validated_params = GetUserParams(**params)
    return service.get_user(validated_params)

@router.post("/create_users", response_model=ApiResponse)
@schema(
    input_schema_class=CreateUsersParams,
    output_schema_class=UsersList,
    examples=examples["/n8n/create_users"]
)
async def create_users(
    params: Dict[str, Any] = Body(...),
    service: N8nService = Depends(get_n8n_service)
):
    validated_params = CreateUsersParams(**params)
    return service.create_users(validated_params)

@router.post("/delete_user", response_model=ApiResponse)
@schema(
    input_schema_class=DeleteUserParams,
    output_schema_class=SuccessResponse,
    examples=examples["/n8n/delete_user"]
)
async def delete_user(
    params: Dict[str, Any] = Body(...),
    service: N8nService = Depends(get_n8n_service)
):
    validated_params = DeleteUserParams(**params)
    return service.delete_user(validated_params)

@router.post("/update_user_role", response_model=ApiResponse)
@schema(
    input_schema_class=UpdateUserRoleParams,
    output_schema_class=User,
    examples=examples["/n8n/update_user_role"]
)
async def update_user_role(
    params: Dict[str, Any] = Body(...),
    service: N8nService = Depends(get_n8n_service)
):
    validated_params = UpdateUserRoleParams(**params)
    return service.update_user_role(validated_params)

# Executions routes
@router.post("/list_executions", response_model=ApiResponse)
@schema(
    input_schema_class=ListExecutionsParams,
    output_schema_class=ExecutionsList,
    examples=examples["/n8n/list_executions"]
)
async def list_executions(
    params: Dict[str, Any] = Body(...),
    service: N8nService = Depends(get_n8n_service)
):
    validated_params = ListExecutionsParams(**params)
    return service.list_executions(validated_params)

@router.post("/get_execution", response_model=ApiResponse)
@schema(
    input_schema_class=GetExecutionParams,
    output_schema_class=Execution,
    examples=examples["/n8n/get_execution"]
)
async def get_execution(
    params: Dict[str, Any] = Body(...),
    service: N8nService = Depends(get_n8n_service)
):
    validated_params = GetExecutionParams(**params)
    return service.get_execution(validated_params)

@router.post("/delete_execution", response_model=ApiResponse)
@schema(
    input_schema_class=DeleteExecutionParams,
    output_schema_class=SuccessResponse,
    examples=examples["/n8n/delete_execution"]
)
async def delete_execution(
    params: Dict[str, Any] = Body(...),
    service: N8nService = Depends(get_n8n_service)
):
    validated_params = DeleteExecutionParams(**params)
    return service.delete_execution(validated_params)

# Workflows routes
@router.post("/list_workflows", response_model=ApiResponse)
@schema(
    input_schema_class=ListWorkflowsParams,
    output_schema_class=WorkflowsList,
    examples=examples["/n8n/list_workflows"]
)
async def list_workflows(
    params: Dict[str, Any] = Body(...),
    service: N8nService = Depends(get_n8n_service)
):
    validated_params = ListWorkflowsParams(**params)
    return service.list_workflows(validated_params)

@router.post("/get_workflow", response_model=ApiResponse)
@schema(
    input_schema_class=GetWorkflowParams,
    output_schema_class=Workflow,
    examples=examples["/n8n/get_workflow"]
)
async def get_workflow(
    params: Dict[str, Any] = Body(...),
    service: N8nService = Depends(get_n8n_service)
):
    validated_params = GetWorkflowParams(**params)
    return service.get_workflow(validated_params)

@router.post("/create_workflow", response_model=ApiResponse)
@schema(
    input_schema_class=CreateWorkflowParams,
    output_schema_class=Workflow,
    examples=examples["/n8n/create_workflow"]
)
async def create_workflow(
    params: Dict[str, Any] = Body(...),
    service: N8nService = Depends(get_n8n_service)
):
    validated_params = CreateWorkflowParams(**params)
    return service.create_workflow(validated_params)

@router.post("/update_workflow", response_model=ApiResponse)
@schema(
    input_schema_class=UpdateWorkflowParams,
    output_schema_class=Workflow,
    examples=examples["/n8n/update_workflow"]
)
async def update_workflow(
    params: Dict[str, Any] = Body(...),
    service: N8nService = Depends(get_n8n_service)
):
    validated_params = UpdateWorkflowParams(**params)
    return service.update_workflow(validated_params)

@router.post("/delete_workflow", response_model=ApiResponse)
@schema(
    input_schema_class=DeleteWorkflowParams,
    output_schema_class=SuccessResponse,
    examples=examples["/n8n/delete_workflow"]
)
async def delete_workflow(
    params: Dict[str, Any] = Body(...),
    service: N8nService = Depends(get_n8n_service)
):
    validated_params = DeleteWorkflowParams(**params)
    return service.delete_workflow(validated_params)

@router.post("/activate_workflow", response_model=ApiResponse)
@schema(
    input_schema_class=ActivateWorkflowParams,
    output_schema_class=Workflow,
    examples=examples["/n8n/activate_workflow"]
)
async def activate_workflow(
    params: Dict[str, Any] = Body(...),
    service: N8nService = Depends(get_n8n_service)
):
    validated_params = ActivateWorkflowParams(**params)
    return service.activate_workflow(validated_params)

@router.post("/copy_workflow", response_model=ApiResponse)
@schema(
    input_schema_class=CopyWorkflowParams,
    output_schema_class=Workflow,
    examples=examples["/n8n/copy_workflow"]
)
async def copy_workflow(
    params: Dict[str, Any] = Body(...),
    service: N8nService = Depends(get_n8n_service)
):
    validated_params = CopyWorkflowParams(**params)
    return service.copy_workflow(validated_params)

@router.post("/list_tags", response_model=ApiResponse)
@schema(
    input_schema_class=EmptyRequestBody,
    output_schema_class=TagsList,
    examples=examples["/n8n/list_tags"]
)
async def list_tags(
    params: Dict[str, Any] = Body(...),
    service: N8nService = Depends(get_n8n_service)
):
    return service.list_tags()

@router.post("/deactivate_workflow", response_model=ApiResponse)
@schema(
    input_schema_class=GetWorkflowParams,
    output_schema_class=Workflow,
    examples=examples["/n8n/deactivate_workflow"]
)
async def deactivate_workflow(
    params: Dict[str, Any] = Body(...),
    service: N8nService = Depends(get_n8n_service)
):
    validated_params = GetWorkflowParams(**params)
    return service.deactivate_workflow(validated_params)

# Credential routes
@router.post("/list_credentials", response_model=ApiResponse)
@schema(
    input_schema_class=ListCredentialsParams,
    output_schema_class=CredentialsList,
    examples=examples["/n8n/list_credentials"]
)
async def list_credentials(
    params: Dict[str, Any] = Body(...),
    service: N8nService = Depends(get_n8n_service)
):
    validated_params = ListCredentialsParams(**params)
    return service.list_credentials(validated_params)

@router.post("/create_credential", response_model=ApiResponse)
@schema(
    input_schema_class=CreateCredentialParams,
    output_schema_class=Credential,
    examples=examples["/n8n/create_credential"]
)
async def create_credential(
    params: Dict[str, Any] = Body(...),
    service: N8nService = Depends(get_n8n_service)
):
    validated_params = CreateCredentialParams(**params)
    return service.create_credential(validated_params)

@router.post("/delete_credential", response_model=ApiResponse)
@schema(
    input_schema_class=DeleteCredentialParams,
    output_schema_class=SuccessResponse,
    examples=examples["/n8n/delete_credential"]
)
async def delete_credential(
    params: Dict[str, Any] = Body(...),
    service: N8nService = Depends(get_n8n_service)
):
    validated_params = DeleteCredentialParams(**params)
    return service.delete_credential(validated_params)

@router.post("/get_credential_type", response_model=ApiResponse)
@schema(
    input_schema_class=GetCredentialTypeParams,
    output_schema_class=CredentialTypeSchema,
    examples=examples["/n8n/get_credential_type"]
)
async def get_credential_type(
    params: Dict[str, Any] = Body(...),
    service: N8nService = Depends(get_n8n_service)
):
    validated_params = GetCredentialTypeParams(**params)
    return service.get_credential_type(validated_params)

# Additional Tag routes
@router.post("/create_tag", response_model=ApiResponse)
@schema(
    input_schema_class=CreateTagParams,
    output_schema_class=Tag,
    examples=examples["/n8n/create_tag"]
)
async def create_tag(
    params: Dict[str, Any] = Body(...),
    service: N8nService = Depends(get_n8n_service)
):
    validated_params = CreateTagParams(**params)
    return service.create_tag(validated_params)

@router.post("/delete_tag", response_model=ApiResponse)
@schema(
    input_schema_class=DeleteTagParams,
    output_schema_class=SuccessResponse,
    examples=examples["/n8n/delete_tag"]
)
async def delete_tag(
    params: Dict[str, Any] = Body(...),
    service: N8nService = Depends(get_n8n_service)
):
    validated_params = DeleteTagParams(**params)
    return service.delete_tag(validated_params)

@router.post("/update_tag", response_model=ApiResponse)
@schema(
    input_schema_class=UpdateTagParams,
    output_schema_class=Tag,
    examples=examples["/n8n/update_tag"]
)
async def update_tag(
    params: Dict[str, Any] = Body(...),
    service: N8nService = Depends(get_n8n_service)
):
    validated_params = UpdateTagParams(**params)
    return service.update_tag(validated_params)

# Source Control routes
@router.post("/pull_from_source_control", response_model=ApiResponse)
@schema(
    input_schema_class=PullOptions,
    output_schema_class=PullResult,
    examples=examples["/n8n/pull_from_source_control"]
)
async def pull_from_source_control(
    params: Dict[str, Any] = Body(...),
    service: N8nService = Depends(get_n8n_service)
):
    validated_params = PullOptions(**params)
    return service.pull_from_source_control(validated_params)

# Variable routes
@router.post("/list_variables", response_model=ApiResponse)
@schema(
    input_schema_class=ListVariablesParams,
    output_schema_class=VariablesList,
    examples=examples["/n8n/list_variables"]
)
async def list_variables(
    params: Dict[str, Any] = Body(...),
    service: N8nService = Depends(get_n8n_service)
):
    validated_params = ListVariablesParams(**params)
    return service.list_variables(validated_params)

@router.post("/create_variable", response_model=ApiResponse)
@schema(
    input_schema_class=CreateVariableParams,
    output_schema_class=Variable,
    examples=examples["/n8n/create_variable"]
)
async def create_variable(
    params: Dict[str, Any] = Body(...),
    service: N8nService = Depends(get_n8n_service)
):
    validated_params = CreateVariableParams(**params)
    return service.create_variable(validated_params)

@router.post("/delete_variable", response_model=ApiResponse)
@schema(
    input_schema_class=DeleteVariableParams,
    output_schema_class=SuccessResponse,
    examples=examples["/n8n/delete_variable"]
)
async def delete_variable(
    params: Dict[str, Any] = Body(...),
    service: N8nService = Depends(get_n8n_service)
):
    validated_params = DeleteVariableParams(**params)
    return service.delete_variable(validated_params)

# Project routes
@router.post("/list_projects", response_model=ApiResponse)
@schema(
    input_schema_class=ListProjectsParams,
    output_schema_class=ProjectsList,
    examples=examples["/n8n/list_projects"]
)
async def list_projects(
    params: Dict[str, Any] = Body(...),
    service: N8nService = Depends(get_n8n_service)
):
    validated_params = ListProjectsParams(**params)
    return service.list_projects(validated_params)

@router.post("/create_project", response_model=ApiResponse)
@schema(
    input_schema_class=CreateProjectParams,
    output_schema_class=Project,
    examples=examples["/n8n/create_project"]
)
async def create_project(
    params: Dict[str, Any] = Body(...),
    service: N8nService = Depends(get_n8n_service)
):
    validated_params = CreateProjectParams(**params)
    return service.create_project(validated_params)

@router.post("/update_project", response_model=ApiResponse)
@schema(
    input_schema_class=UpdateProjectParams,
    output_schema_class=SuccessResponse,
    examples=examples["/n8n/update_project"]
)
async def update_project(
    params: Dict[str, Any] = Body(...),
    service: N8nService = Depends(get_n8n_service)
):
    validated_params = UpdateProjectParams(**params)
    return service.update_project(validated_params)

@router.post("/delete_project", response_model=ApiResponse)
@schema(
    input_schema_class=DeleteProjectParams,
    output_schema_class=SuccessResponse,
    examples=examples["/n8n/delete_project"]
)
async def delete_project(
    params: Dict[str, Any] = Body(...),
    service: N8nService = Depends(get_n8n_service)
):
    validated_params = DeleteProjectParams(**params)
    return service.delete_project(validated_params)

@router.post("/validate_key")
async def validate_key(
    params: Dict[str, Any] = Body(...),
):
    try:
        api_key = params.get("api_key", "")
        base_url = params.get("base_url", "")
        if not api_key:
            return {"valid": False, "message": "API key is required"}
        if not base_url:
            return {"valid": False, "message": "Base URL is required"}
        
        if base_url.endswith('/'):
            return {"valid": False, "message": "Base URL cannot end with a slash"}
        
        client = N8nClient(api_key, base_url)
        client.list_workflows()
        
        return {"valid": True, "message": "API key is valid"}
    except Exception as e:
        return {"valid": False, "message": f"Invalid API key: {str(e)}"}
    
apply_error_handler_to_router(router)