from fastapi import APIRouter, Depends, HTTPException, Request as FastAPIRequest, Body
from typing import Dict, Any
from .schema import (
    GetCollectionsParams, GetCollectionParams, UpdateCollectionParams,
    DeleteCollectionParams, ApiResponse, CollectionListResponse,
    CollectionResponse, DeleteCollectionResponse, CreateCollectionParams,
    GetEnvironmentsParams, GetEnvironmentParams, CreateEnvironmentParams,
    UpdateEnvironmentParams, DeleteEnvironmentParams, EnvironmentListResponse,
    EnvironmentResponse, DeleteEnvironmentResponse, ForkCollectionParams,
    ForkCollectionResponse, GetWorkspacesParams, GetWorkspaceParams,
    WorkspaceListResponse, WorkspaceResponse, CreateWorkspaceParams,
    DeleteWorkspaceParams, DeleteWorkspaceResponse, UpdateWorkspaceParams
)
from .service import PostmanService
from .client import PostmanClient
from ..common.input_schema_decorator import schema
from ..common.examples_handler import ExamplesLoader
from ..common.auth import validate_provider_api_key
from ..common.utils import apply_error_handler_to_router, apply_error_handler_to_service

router = APIRouter(prefix="/postman", tags=["postman"])

examples = ExamplesLoader()

async def get_postman_service(request: FastAPIRequest) -> PostmanService:
    try:
        api_key = await validate_provider_api_key(request, "postman")
        client = PostmanClient(api_key)
        service = PostmanService(client)
        
        apply_error_handler_to_service(service)
        
        return service
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Failed to initialize Postman service: {str(e)}"
        )

@router.post("/get_collections", response_model=ApiResponse)
@schema(
    input_schema_class=GetCollectionsParams, 
    output_schema_class=CollectionListResponse,
    examples=examples["/postman/get_collections"]
)
async def get_collections(
    params: Dict[str, Any] = Body(...),
    service: PostmanService = Depends(get_postman_service)
):
    validated_params = GetCollectionsParams(**params)
    return service.get_collections(validated_params)

@router.post("/get_collection", response_model=ApiResponse)
@schema(
    input_schema_class=GetCollectionParams, 
    output_schema_class=CollectionResponse,
    examples=examples["/postman/get_collection"]
)
async def get_collection(
    params: Dict[str, Any] = Body(...),
    service: PostmanService = Depends(get_postman_service)
):
    validated_params = GetCollectionParams(**params)
    return service.get_collection(
        validated_params.collection_id,
        validated_params
    )

@router.post("/update_collection", response_model=ApiResponse)
@schema(
    input_schema_class=UpdateCollectionParams, 
    output_schema_class=CollectionResponse,
    examples=examples["/postman/update_collection"]
)
async def update_collection(
    params: Dict[str, Any] = Body(...),
    service: PostmanService = Depends(get_postman_service)
):
    validated_params = UpdateCollectionParams(**params)
    return service.update_collection(validated_params)

@router.post("/delete_collection", response_model=ApiResponse)
@schema(
    input_schema_class=DeleteCollectionParams, 
    output_schema_class=DeleteCollectionResponse,
    examples=examples["/postman/delete_collection"]
)
async def delete_collection(
    params: Dict[str, Any] = Body(...),
    service: PostmanService = Depends(get_postman_service)
):
    validated_params = DeleteCollectionParams(**params)
    return service.delete_collection(validated_params)

@router.post("/create_collection", response_model=ApiResponse)
@schema(
    input_schema_class=CreateCollectionParams, 
    output_schema_class=CollectionResponse,
    examples=examples["/postman/create_collection"]
)
async def create_collection(
    params: Dict[str, Any] = Body(...),
    service: PostmanService = Depends(get_postman_service)
):
    validated_params = CreateCollectionParams(**params)
    return service.create_collection(validated_params)

@router.post("/get_environments", response_model=ApiResponse)
@schema(
    input_schema_class=GetEnvironmentsParams, 
    output_schema_class=EnvironmentListResponse,
    examples=examples["/postman/get_environments"]
)
async def get_environments(
    params: Dict[str, Any] = Body(...),
    service: PostmanService = Depends(get_postman_service)
):
    validated_params = GetEnvironmentsParams(**params)
    return service.get_environments(validated_params)

@router.post("/get_environment", response_model=ApiResponse)
@schema(
    input_schema_class=GetEnvironmentParams, 
    output_schema_class=EnvironmentResponse,
    examples=examples["/postman/get_environment"]
)
async def get_environment(
    params: Dict[str, Any] = Body(...),
    service: PostmanService = Depends(get_postman_service)
):
    validated_params = GetEnvironmentParams(**params)
    return service.get_environment(
        validated_params.environment_id,
        validated_params
    )

@router.post("/create_environment", response_model=ApiResponse)
@schema(
    input_schema_class=CreateEnvironmentParams, 
    output_schema_class=EnvironmentResponse,
    examples=examples["/postman/create_environment"]
)
async def create_environment(
    params: Dict[str, Any] = Body(...),
    service: PostmanService = Depends(get_postman_service)
):
    validated_params = CreateEnvironmentParams(**params)
    return service.create_environment(validated_params)

@router.post("/update_environment", response_model=ApiResponse)
@schema(
    input_schema_class=UpdateEnvironmentParams, 
    output_schema_class=EnvironmentResponse,
    examples=examples["/postman/update_environment"]
)
async def update_environment(
    params: Dict[str, Any] = Body(...),
    service: PostmanService = Depends(get_postman_service)
):
    validated_params = UpdateEnvironmentParams(**params)
    return service.update_environment(validated_params)

@router.post("/delete_environment", response_model=ApiResponse)
@schema(
    input_schema_class=DeleteEnvironmentParams, 
    output_schema_class=DeleteEnvironmentResponse,
    examples=examples["/postman/delete_environment"]
)
async def delete_environment(
    params: Dict[str, Any] = Body(...),
    service: PostmanService = Depends(get_postman_service)
):
    validated_params = DeleteEnvironmentParams(**params)
    return service.delete_environment(validated_params)

@router.post("/fork_collection", response_model=ApiResponse)
@schema(
    input_schema_class=ForkCollectionParams, 
    output_schema_class=ForkCollectionResponse,
    examples=examples["/postman/fork_collection"]
)
async def fork_collection(
    params: Dict[str, Any] = Body(...),
    service: PostmanService = Depends(get_postman_service)
):
    validated_params = ForkCollectionParams(**params)
    return service.fork_collection(validated_params)

@router.post("/get_workspaces", response_model=ApiResponse)
@schema(
    input_schema_class=GetWorkspacesParams, 
    output_schema_class=WorkspaceListResponse,
    examples=examples["/postman/get_workspaces"]
)
async def get_workspaces(
    params: Dict[str, Any] = Body(...),
    service: PostmanService = Depends(get_postman_service)
):
    validated_params = GetWorkspacesParams(**params)
    return service.get_workspaces(validated_params)

@router.post("/get_workspace", response_model=ApiResponse)
@schema(
    input_schema_class=GetWorkspaceParams, 
    output_schema_class=WorkspaceResponse,
    examples=examples["/postman/get_workspace"]
)
async def get_workspace(
    params: Dict[str, Any] = Body(...),
    service: PostmanService = Depends(get_postman_service)
):
    validated_params = GetWorkspaceParams(**params)
    return service.get_workspace(
        validated_params.workspace_id,
        validated_params
    )

@router.post("/create_workspace", response_model=ApiResponse)
@schema(
    input_schema_class=CreateWorkspaceParams, 
    output_schema_class=WorkspaceResponse,
    examples=examples["/postman/create_workspace"]
)
async def create_workspace(
    params: Dict[str, Any] = Body(...),
    service: PostmanService = Depends(get_postman_service)
):
    validated_params = CreateWorkspaceParams(**params)
    return service.create_workspace(validated_params)

@router.post("/update_workspace", response_model=ApiResponse)
@schema(
    input_schema_class=UpdateWorkspaceParams, 
    output_schema_class=WorkspaceResponse,
    examples=examples["/postman/update_workspace"]
)
async def update_workspace(
    params: Dict[str, Any] = Body(...),
    service: PostmanService = Depends(get_postman_service)
):
    validated_params = UpdateWorkspaceParams(**params)
    return service.update_workspace(validated_params)

@router.post("/delete_workspace", response_model=ApiResponse)
@schema(
    input_schema_class=DeleteWorkspaceParams, 
    output_schema_class=DeleteWorkspaceResponse,
    examples=examples["/postman/delete_workspace"]
)
async def delete_workspace(
    params: Dict[str, Any] = Body(...),
    service: PostmanService = Depends(get_postman_service)
):
    validated_params = DeleteWorkspaceParams(**params)
    return service.delete_workspace(validated_params)

@router.post("/validate_key")
async def validate_key(
    params: Dict[str, Any] = Body(...),
):
    try:
        api_key = params.get("api_key")
        if not api_key:
            return {"valid": False, "message": "API key is required"}
        
        client = PostmanClient(api_key=api_key)
        test_response = client.get_collections()
        return {"valid": True, "message": "API key is valid"}
    except Exception as e:
        return {"valid": False, "message": f"Invalid API key"}

apply_error_handler_to_router(router)
