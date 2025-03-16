from fastapi import APIRouter, Depends, HTTPException, Request as FastAPIRequest, Body
from typing import Optional, Dict, Any
from .schema import (
    ListDeploymentsParams, GetDeploymentParams, CreateDeploymentParams,
    DeleteDeploymentParams, CancelDeploymentParams, GetDeploymentFilesParams,
    GetDeploymentEventsParams, ApiResponse, AddDomainToProjectParams, CreateProjectParams,
    CreateEnvVarsParams, DeleteProjectParams, EditEnvVarParams, GetProjectParams,
    GetProjectDomainParams, RemoveEnvVarParams, ListProjectsParams,
    GetProjectDomainsParams, VerifyProjectDomainParams, UpdateProjectParams,
    GetProjectEnvVarsParams
)
from .service import VercelService
from .client import VercelClient
import os
import pickle
from ..common.input_schema_decorator import schema, input_schema, output_schema
from pydantic import ValidationError
from ..common.examples_handler import ExamplesLoader
from ..common.auth import TokenService
router = APIRouter(prefix="/vercel", tags=["vercel"])

examples = ExamplesLoader()

VERCEL_TOKEN_PATH = "credentials/vercel_token.pickle"

async def get_vercel_service(request: FastAPIRequest) -> VercelService:
    try:
        token_data = await TokenService.get_user_token(request, 'vercel')
        if not token_data or not token_data.get('access_token'):
            raise HTTPException(
                status_code=401,
                detail="No TickTick token data found"
            )
            
        client = VercelClient(token_data['access_token'])
        return VercelService(client)
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Failed to initialize TickTick service: {str(e)}"
        )

@router.post("/list_deployments", response_model=ApiResponse)
@schema(input_schema_class=ListDeploymentsParams, examples=examples["/vercel/list_deployments"])
async def list_deployments(
    params: Dict[str, Any] = Body(...),
    service: VercelService = Depends(get_vercel_service)
):
    try:
        validated_params = ListDeploymentsParams(**params)
        return service.list_deployments(validated_params)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_deployment", response_model=ApiResponse)
@schema(input_schema_class=GetDeploymentParams, examples=examples["/vercel/get_deployment"])
async def get_deployment(
    params: Dict[str, Any] = Body(...),
    service: VercelService = Depends(get_vercel_service)
):
    try:
        validated_params = GetDeploymentParams(**params)
        return service.get_deployment(
            validated_params.id_or_url,
            validated_params
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create_deployment", response_model=ApiResponse)
@schema(input_schema_class=CreateDeploymentParams, examples=examples["/vercel/create_deployment"])
async def create_deployment(
    params: Dict[str, Any] = Body(...),
    service: VercelService = Depends(get_vercel_service)
):
    try:
        # Check if parameters are nested under a 'parameters' key
        if "parameters" in params and isinstance(params["parameters"], dict):
            params = params["parameters"]
            
        # If git_source contains 'repo' instead of 'repo_id', fix it
        if "git_source" in params and isinstance(params["git_source"], dict):
            if "repo" in params["git_source"] and "repo_id" not in params["git_source"]:
                params["git_source"]["repo_id"] = params["git_source"].pop("repo")
        
        validated_params = CreateDeploymentParams(**params)
        return service.create_deployment(validated_params)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/delete_deployment", response_model=ApiResponse)
@schema(input_schema_class=DeleteDeploymentParams, examples=examples["/vercel/delete_deployment"])
async def delete_deployment(
    params: Dict[str, Any] = Body(...),
    service: VercelService = Depends(get_vercel_service)
):
    try:
        validated_params = DeleteDeploymentParams(**params)
        return service.delete_deployment(
            validated_params.deployment_id,
            validated_params
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cancel_deployment", response_model=ApiResponse)
@schema(input_schema_class=CancelDeploymentParams, examples=examples["/vercel/cancel_deployment"])
async def cancel_deployment(
    params: Dict[str, Any] = Body(...),
    service: VercelService = Depends(get_vercel_service)
):
    try:
        validated_params = CancelDeploymentParams(**params)
        return service.cancel_deployment(
            validated_params.deployment_id,
            validated_params
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_deployment_files", response_model=ApiResponse)
@schema(input_schema_class=GetDeploymentFilesParams, examples=examples["/vercel/get_deployment_files"])
async def get_deployment_files(
    params: Dict[str, Any] = Body(...),
    service: VercelService = Depends(get_vercel_service)
):
    try:
        validated_params = GetDeploymentFilesParams(**params)
        return service.get_deployment_files(
            validated_params.deployment_id,
            validated_params
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_deployment_events", response_model=ApiResponse)
@schema(input_schema_class=GetDeploymentEventsParams, examples=examples["/vercel/get_deployment_events"])
async def get_deployment_events(
    params: Dict[str, Any] = Body(...),
    service: VercelService = Depends(get_vercel_service)
):
    try:
        validated_params = GetDeploymentEventsParams(**params)
        return service.get_deployment_events(
            validated_params.id_or_url,
            validated_params
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/add_domain_to_project", response_model=ApiResponse)
@schema(input_schema_class=AddDomainToProjectParams, examples=examples["/vercel/add_domain_to_project"])
async def add_domain_to_project(
    params: Dict[str, Any] = Body(...),
    service: VercelService = Depends(get_vercel_service)
):
    try:
        validated_params = AddDomainToProjectParams(**params)
        return service.add_domain_to_project(validated_params)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create_project", response_model=ApiResponse)
@schema(input_schema_class=CreateProjectParams, examples=examples["/vercel/create_project"])
async def create_project(
    params: Dict[str, Any] = Body(...),
    service: VercelService = Depends(get_vercel_service)
):
    try:
        validated_params = CreateProjectParams(**params)
        return service.create_project(validated_params)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create_env_vars", response_model=ApiResponse)
@schema(input_schema_class=CreateEnvVarsParams, examples=examples["/vercel/create_env_vars"])
async def create_env_vars(
    params: Dict[str, Any] = Body(...),
    service: VercelService = Depends(get_vercel_service)
):
    try:
        validated_params = CreateEnvVarsParams(**params)
        return service.create_env_vars(validated_params)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/delete_project", response_model=ApiResponse)
@schema(input_schema_class=DeleteProjectParams, examples=examples["/vercel/delete_project"])
async def delete_project(
    params: Dict[str, Any] = Body(...),
    service: VercelService = Depends(get_vercel_service)
):
    try:
        validated_params = DeleteProjectParams(**params)
        return service.delete_project(validated_params)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/edit_env_var", response_model=ApiResponse)
@schema(input_schema_class=EditEnvVarParams, examples=examples["/vercel/edit_env_var"])
async def edit_env_var(
    params: Dict[str, Any] = Body(...),
    service: VercelService = Depends(get_vercel_service)
):
    try:
        validated_params = EditEnvVarParams(**params)
        return service.edit_env_var(validated_params)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_project", response_model=ApiResponse)
@schema(input_schema_class=GetProjectParams, examples=examples["/vercel/get_project"])
async def get_project(
    params: Dict[str, Any] = Body(...),
    service: VercelService = Depends(get_vercel_service)
):
    try:
        validated_params = GetProjectParams(**params)
        return service.get_project(validated_params)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_project_domain", response_model=ApiResponse)
@schema(input_schema_class=GetProjectDomainParams, examples=examples["/vercel/get_project_domain"])
async def get_project_domain(
    params: Dict[str, Any] = Body(...),
    service: VercelService = Depends(get_vercel_service)
):
    try:
        validated_params = GetProjectDomainParams(**params)
        return service.get_project_domain(validated_params)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/remove_env_var", response_model=ApiResponse)
@schema(input_schema_class=RemoveEnvVarParams, examples=examples["/vercel/remove_env_var"])
async def remove_env_var(
    params: Dict[str, Any] = Body(...),
    service: VercelService = Depends(get_vercel_service)
):
    try:
        validated_params = RemoveEnvVarParams(**params)
        return service.remove_env_var(validated_params)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/list_projects", response_model=ApiResponse)
@schema(input_schema_class=ListProjectsParams, examples=examples["/vercel/list_projects"])
async def list_projects(
    params: Dict[str, Any] = Body(...),
    service: VercelService = Depends(get_vercel_service)
):
    try:
        validated_params = ListProjectsParams(**params)
        return service.list_projects(validated_params)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_project_domains", response_model=ApiResponse)
@schema(input_schema_class=GetProjectDomainsParams, examples=examples["/vercel/get_project_domains"])
async def get_project_domains(
    params: Dict[str, Any] = Body(...),
    service: VercelService = Depends(get_vercel_service)
):
    try:
        validated_params = GetProjectDomainsParams(**params)
        return service.get_project_domains(validated_params)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/verify_project_domain", response_model=ApiResponse)
@schema(input_schema_class=VerifyProjectDomainParams, examples=examples["/vercel/verify_project_domain"])
async def verify_project_domain(
    params: Dict[str, Any] = Body(...),
    service: VercelService = Depends(get_vercel_service)
):
    try:
        validated_params = VerifyProjectDomainParams(**params)
        return service.verify_project_domain(validated_params)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update_project", response_model=ApiResponse)
@schema(input_schema_class=UpdateProjectParams, examples=examples["/vercel/update_project"])
async def update_project(
    params: Dict[str, Any] = Body(...),
    service: VercelService = Depends(get_vercel_service)
):
    try:
        validated_params = UpdateProjectParams(**params)
        return service.update_project(validated_params)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_project_env_vars", response_model=ApiResponse)
@schema(input_schema_class=GetProjectEnvVarsParams, examples=examples["/vercel/get_project_env_vars"])
async def get_project_env_vars(
    params: Dict[str, Any] = Body(...),
    service: VercelService = Depends(get_vercel_service)
):
    try:
        validated_params = GetProjectEnvVarsParams(**params)
        return service.get_project_env_vars(validated_params)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
