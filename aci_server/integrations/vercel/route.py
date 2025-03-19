from fastapi import APIRouter, Depends, HTTPException, Request as FastAPIRequest, Body
from typing import Optional, Dict, Any, List
from .schema import (
    ListDeploymentsParams, GetDeploymentParams,
    DeleteDeploymentParams, CancelDeploymentParams,
    GetDeploymentEventsParams, ApiResponse, AddDomainToProjectParams, CreateProjectParams,
    CreateEnvVarsParams, DeleteProjectParams, EditEnvVarParams, GetProjectParams,
    GetProjectDomainParams, RemoveEnvVarParams, ListProjectsParams,
    GetProjectDomainsParams, VerifyProjectDomainParams, UpdateProjectParams,
    GetProjectEnvVarsParams, CreateDeploymentParams,
    DeploymentListResponse, DeploymentResponse, DeleteDeploymentResponse,
    DeploymentResponse, DeploymentEventListResponse, AddDomainResponse, ProjectResponse,
    CreateEnvVarsResponse, EnvVarResponse, ProjectDomainResponse, ProjectDomainsResponse, ProjectListResponse,
    DeleteProjectResponse, EnvVarListResponse
)
from .service import VercelService
from .client import VercelClient
import os
import pickle
from ..common.input_schema_decorator import schema, input_schema, output_schema
from pydantic import ValidationError
from ..common.examples_handler import ExamplesLoader
from ..common.auth import TokenService
from ..common.utils import apply_error_handler_to_router, apply_error_handler_to_service, apply_error_handler_to_client

router = APIRouter(prefix="/vercel", tags=["vercel"])

examples = ExamplesLoader()

async def get_vercel_service(request: FastAPIRequest) -> VercelService:
    try:
        token_data = await TokenService.get_user_token(request, 'vercel')
        if not token_data or not token_data.get('access_token'):
            raise HTTPException(
                status_code=401,
                detail="No Vercel token data found"
            )
            
        client = VercelClient(token_data['access_token'])
        apply_error_handler_to_client(client)
        service = VercelService(client)
        
        apply_error_handler_to_service(service)
        
        return service
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Failed to initialize Vercel service: {str(e)}"
        )

@router.post("/list_deployments", response_model=ApiResponse)
@schema(
    input_schema_class=ListDeploymentsParams, 
    output_schema_class=DeploymentListResponse,
    examples=examples["/vercel/list_deployments"]
)
async def list_deployments(
    params: Dict[str, Any] = Body(...),
    service: VercelService = Depends(get_vercel_service)
):
    validated_params = ListDeploymentsParams(**params)
    return service.list_deployments(validated_params)

@router.post("/get_deployment", response_model=ApiResponse)
@schema(
    input_schema_class=GetDeploymentParams, 
    output_schema_class=DeploymentResponse,
    examples=examples["/vercel/get_deployment"]
)
async def get_deployment(
    params: Dict[str, Any] = Body(...),
    service: VercelService = Depends(get_vercel_service)
):
    validated_params = GetDeploymentParams(**params)
    return service.get_deployment(
        validated_params.id_or_url,
        validated_params
    )

@router.post("/delete_deployment", response_model=ApiResponse)
@schema(
    input_schema_class=DeleteDeploymentParams, 
    output_schema_class=DeleteDeploymentResponse,
    examples=examples["/vercel/delete_deployment"]
)
async def delete_deployment(
    params: Dict[str, Any] = Body(...),
    service: VercelService = Depends(get_vercel_service)
):
    validated_params = DeleteDeploymentParams(**params)
    return service.delete_deployment(
        validated_params.deployment_id,
        validated_params
    )

@router.post("/cancel_deployment", response_model=ApiResponse)
@schema(
    input_schema_class=CancelDeploymentParams, 
    output_schema_class=DeploymentResponse,
    examples=examples["/vercel/cancel_deployment"]
)
async def cancel_deployment(
    params: Dict[str, Any] = Body(...),
    service: VercelService = Depends(get_vercel_service)
):
    validated_params = CancelDeploymentParams(**params)
    return service.cancel_deployment(
        validated_params.deployment_id,
        validated_params
    )

@router.post("/get_deployment_events", response_model=ApiResponse)
@schema(
    input_schema_class=GetDeploymentEventsParams, 
    output_schema_class=DeploymentEventListResponse,
    examples=examples["/vercel/get_deployment_events"]
)
async def get_deployment_events(
    params: Dict[str, Any] = Body(...),
    service: VercelService = Depends(get_vercel_service)
):
    validated_params = GetDeploymentEventsParams(**params)
    return service.get_deployment_events(
        validated_params.id_or_url,
        validated_params
    )

@router.post("/add_domain_to_project", response_model=ApiResponse)
@schema(
    input_schema_class=AddDomainToProjectParams, 
    output_schema_class=AddDomainResponse,
    examples=examples["/vercel/add_domain_to_project"]
)
async def add_domain_to_project(
    params: Dict[str, Any] = Body(...),
    service: VercelService = Depends(get_vercel_service)
):
    validated_params = AddDomainToProjectParams(**params)
    return service.add_domain_to_project(validated_params)

@router.post("/create_project", response_model=ApiResponse)
@schema(
    input_schema_class=CreateProjectParams, 
    output_schema_class=ProjectResponse,
    examples=examples["/vercel/create_project"]
)
async def create_project(
    params: Dict[str, Any] = Body(...),
    service: VercelService = Depends(get_vercel_service)
):
    validated_params = CreateProjectParams(**params)
    return service.create_project(validated_params)

@router.post("/create_env_vars", response_model=ApiResponse)
@schema(
    input_schema_class=CreateEnvVarsParams, 
    output_schema_class=CreateEnvVarsResponse,
    examples=examples["/vercel/create_env_vars"]
)
async def create_env_vars(
    params: Dict[str, Any] = Body(...),
    service: VercelService = Depends(get_vercel_service)
):
    validated_params = CreateEnvVarsParams(**params)
    return service.create_env_vars(validated_params)

@router.post("/delete_project", response_model=ApiResponse)
@schema(
    input_schema_class=DeleteProjectParams, 
    output_schema_class=DeleteProjectResponse,
    examples=examples["/vercel/delete_project"]
)
async def delete_project(
    params: Dict[str, Any] = Body(...),
    service: VercelService = Depends(get_vercel_service)
):
    validated_params = DeleteProjectParams(**params)
    return service.delete_project(validated_params)

@router.post("/edit_env_var", response_model=ApiResponse)
@schema(
    input_schema_class=EditEnvVarParams, 
    output_schema_class=EnvVarResponse,
    examples=examples["/vercel/edit_env_var"]
)
async def edit_env_var(
    params: Dict[str, Any] = Body(...),
    service: VercelService = Depends(get_vercel_service)
):
    validated_params = EditEnvVarParams(**params)
    return service.edit_env_var(validated_params)

@router.post("/get_project", response_model=ApiResponse)
@schema(
    input_schema_class=GetProjectParams, 
    output_schema_class=ProjectResponse,
    examples=examples["/vercel/get_project"]
)
async def get_project(
    params: Dict[str, Any] = Body(...),
    service: VercelService = Depends(get_vercel_service)
):
    validated_params = GetProjectParams(**params)
    return service.get_project(validated_params)

@router.post("/get_project_domain", response_model=ApiResponse)
@schema(
    input_schema_class=GetProjectDomainParams, 
    output_schema_class=ProjectDomainResponse,
    examples=examples["/vercel/get_project_domain"]
)
async def get_project_domain(
    params: Dict[str, Any] = Body(...),
    service: VercelService = Depends(get_vercel_service)
):
    validated_params = GetProjectDomainParams(**params)
    return service.get_project_domain(validated_params)

@router.post("/remove_env_var", response_model=ApiResponse)
@schema(
    input_schema_class=RemoveEnvVarParams, 
    output_schema_class=EnvVarListResponse,
    examples=examples["/vercel/remove_env_var"]
)
async def remove_env_var(
    params: Dict[str, Any] = Body(...),
    service: VercelService = Depends(get_vercel_service)
):
    validated_params = RemoveEnvVarParams(**params)
    return service.remove_env_var(validated_params)

@router.post("/list_projects", response_model=ApiResponse)
@schema(
    input_schema_class=ListProjectsParams, 
    output_schema_class=ProjectListResponse,
    examples=examples["/vercel/list_projects"]
)
async def list_projects(
    params: Dict[str, Any] = Body(...),
    service: VercelService = Depends(get_vercel_service)
):
    validated_params = ListProjectsParams(**params)
    return service.list_projects(validated_params)

@router.post("/get_project_domains", response_model=ApiResponse)
@schema(
    input_schema_class=GetProjectDomainsParams, 
    output_schema_class=ProjectDomainsResponse,
    examples=examples["/vercel/get_project_domains"]
)
async def get_project_domains(
    params: Dict[str, Any] = Body(...),
    service: VercelService = Depends(get_vercel_service)
):
    validated_params = GetProjectDomainsParams(**params)
    return service.get_project_domains(validated_params)

@router.post("/verify_project_domain", response_model=ApiResponse)
@schema(
    input_schema_class=VerifyProjectDomainParams, 
    output_schema_class=ProjectDomainResponse,
    examples=examples["/vercel/verify_project_domain"]
)
async def verify_project_domain(
    params: Dict[str, Any] = Body(...),
    service: VercelService = Depends(get_vercel_service)
):
    validated_params = VerifyProjectDomainParams(**params)
    return service.verify_project_domain(validated_params)

@router.post("/update_project", response_model=ApiResponse)
@schema(
    input_schema_class=UpdateProjectParams, 
    output_schema_class=ProjectResponse,
    examples=examples["/vercel/update_project"]
)
async def update_project(
    params: Dict[str, Any] = Body(...),
    service: VercelService = Depends(get_vercel_service)
):
    validated_params = UpdateProjectParams(**params)
    return service.update_project(validated_params)

@router.post("/get_project_env_vars", response_model=ApiResponse)
@schema(
    input_schema_class=GetProjectEnvVarsParams, 
    output_schema_class=EnvVarListResponse,
    examples=examples["/vercel/get_project_env_vars"]
)
async def get_project_env_vars(
    params: Dict[str, Any] = Body(...),
    service: VercelService = Depends(get_vercel_service)
):
    validated_params = GetProjectEnvVarsParams(**params)
    return service.get_project_env_vars(validated_params)

@router.post("/create_deployment", response_model=ApiResponse)
@schema(
    input_schema_class=CreateDeploymentParams, 
    output_schema_class=DeploymentResponse,
    examples=examples["/vercel/create_deployment"]
)
async def create_deployment(
    params: Dict[str, Any] = Body(...),
    service: VercelService = Depends(get_vercel_service)
):
    validated_params = CreateDeploymentParams(**params)
    return service.create_deployment(validated_params)

apply_error_handler_to_router(router)
