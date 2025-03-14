from fastapi import APIRouter, Depends, HTTPException, Request as FastAPIRequest, Body
from typing import Dict, Any, List
from .schema import (
    ApiResponse,
    GetFileParams, GetFileNodesParams, GetImageParams, GetFileComponentsParams,
    GetComponentSetsParams, GetStylesParams,
    GetTeamProjectsParams, GetTeamComponentsParams, GetTeamComponentSetsParams, GetTeamStylesParams,
    GetProjectFilesParams,
    GetFileResponse, GetFileNodesResponse, GetImageResponse, GetFileComponentsResponse,
    GetComponentSetsResponse, GetStylesResponse,
    GetMeResponse, GetTeamProjectsResponse, GetTeamComponentsResponse, GetTeamComponentSetsResponse,
    GetTeamStylesResponse, GetProjectFilesResponse
)

from .service import FigmaService
from .client import FigmaClient
from ..common.auth import TokenService, FigmaTokenRefresher
from ..common.input_schema_decorator import schema
from pydantic import ValidationError
from ..common.utils import format_validation_error
from ..common.examples_handler import ExamplesLoader

router = APIRouter(prefix="/figma", tags=["figma"])

examples = ExamplesLoader() 

async def get_figma_service(request: FastAPIRequest) -> FigmaService:
    token_data = await TokenService.get_user_token(request, 'figma')
    
    if TokenService.is_token_expired(token_data):
        try:
            token_data = await FigmaTokenRefresher.refresh(request, token_data)
        except Exception as e:
            raise HTTPException(status_code=401, detail="Failed to refresh token")
    
    access_token = token_data['access_token']
    client = FigmaClient(access_token)
    return FigmaService(client)

@router.post("/get_file", response_model=ApiResponse)
@schema(input_schema_class=GetFileParams, output_schema_class=GetFileResponse, examples=examples["/figma/get_file"])
async def get_file(
    params: Dict[str, Any] = Body(...),
    service: FigmaService = Depends(get_figma_service)
):
    try:
        validated_params = GetFileParams(**params)
        return service.get_file(validated_params.file_key)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetFileParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_file_nodes", response_model=ApiResponse)
@schema(input_schema_class=GetFileNodesParams, output_schema_class=GetFileNodesResponse, examples=examples["/figma/get_file_nodes"])
async def get_file_nodes(
    params: Dict[str, Any] = Body(...),
    service: FigmaService = Depends(get_figma_service)
):
    try:
        validated_params = GetFileNodesParams(**params)
        return service.get_file_nodes(
            file_key=validated_params.file_key,
            node_ids=validated_params.node_ids
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetFileNodesParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_image", response_model=ApiResponse)
@schema(input_schema_class=GetImageParams, output_schema_class=GetImageResponse, examples=examples["/figma/get_image"])
async def get_image(
    params: Dict[str, Any] = Body(...),
    service: FigmaService = Depends(get_figma_service)
):
    try:
        validated_params = GetImageParams(**params)
        return service.get_image(
            file_key=validated_params.file_key,
            node_ids=validated_params.node_ids,
            format=validated_params.format,
            scale=validated_params.scale
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetImageParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_file_components", response_model=ApiResponse)
@schema(input_schema_class=GetFileComponentsParams, output_schema_class=GetFileComponentsResponse, examples=examples["/figma/get_file_components"])
async def get_file_components(
    params: Dict[str, Any] = Body(...),
    service: FigmaService = Depends(get_figma_service)
):
    try:
        validated_params = GetFileComponentsParams(**params)
        return service.get_file_components(validated_params.file_key)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetFileComponentsParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_component_sets", response_model=ApiResponse)
@schema(input_schema_class=GetComponentSetsParams, output_schema_class=GetComponentSetsResponse, examples=examples["/figma/get_component_sets"])
async def get_component_sets(
    params: Dict[str, Any] = Body(...),
    service: FigmaService = Depends(get_figma_service)
):
    try:
        validated_params = GetComponentSetsParams(**params)
        return service.get_component_sets(validated_params.file_key)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetComponentSetsParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_styles", response_model=ApiResponse)
@schema(input_schema_class=GetStylesParams, output_schema_class=GetStylesResponse, examples=examples["/figma/get_styles"])
async def get_styles(
    params: Dict[str, Any] = Body(...),
    service: FigmaService = Depends(get_figma_service)
):
    try:
        validated_params = GetStylesParams(**params)
        return service.get_styles(validated_params.file_key)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetStylesParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_me", response_model=ApiResponse)
@schema(output_schema_class=GetMeResponse, examples=examples["/figma/get_me"])
async def get_me(
    service: FigmaService = Depends(get_figma_service)
):
    try:
        return service.get_me()
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_team_projects", response_model=ApiResponse)
@schema(input_schema_class=GetTeamProjectsParams, output_schema_class=GetTeamProjectsResponse, examples=examples["/figma/get_team_projects"])
async def get_team_projects(
    params: Dict[str, Any] = Body(...),
    service: FigmaService = Depends(get_figma_service)
):
    try:
        validated_params = GetTeamProjectsParams(**params)
        return service.get_team_projects(validated_params.team_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetTeamProjectsParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_team_components", response_model=ApiResponse)
@schema(input_schema_class=GetTeamComponentsParams, output_schema_class=GetTeamComponentsResponse, examples=examples["/figma/get_team_components"])
async def get_team_components(
    params: Dict[str, Any] = Body(...),
    service: FigmaService = Depends(get_figma_service)
):
    try:
        validated_params = GetTeamComponentsParams(**params)
        return service.get_team_components(validated_params.team_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetTeamComponentsParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_team_component_sets", response_model=ApiResponse)
@schema(input_schema_class=GetTeamComponentSetsParams, output_schema_class=GetTeamComponentSetsResponse, examples=examples["/figma/get_team_component_sets"])
async def get_team_component_sets(
    params: Dict[str, Any] = Body(...),
    service: FigmaService = Depends(get_figma_service)
):
    try:
        validated_params = GetTeamComponentSetsParams(**params)
        return service.get_team_component_sets(validated_params.team_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetTeamComponentSetsParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_team_styles", response_model=ApiResponse)
@schema(input_schema_class=GetTeamStylesParams, output_schema_class=GetTeamStylesResponse, examples=examples["/figma/get_team_styles"])
async def get_team_styles(
    params: Dict[str, Any] = Body(...),
    service: FigmaService = Depends(get_figma_service)
):
    try:
        validated_params = GetTeamStylesParams(**params)
        return service.get_team_styles(validated_params.team_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetTeamStylesParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_project_files", response_model=ApiResponse)
@schema(input_schema_class=GetProjectFilesParams, output_schema_class=GetProjectFilesResponse, examples=examples["/figma/get_project_files"])
async def get_project_files(
    params: Dict[str, Any] = Body(...),
    service: FigmaService = Depends(get_figma_service)
):
    try:
        validated_params = GetProjectFilesParams(**params)
        return service.get_project_files(
            project_id=validated_params.project_id,
            branch_name=validated_params.branch_name
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetProjectFilesParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_all_nodes", response_model=ApiResponse)
@schema(input_schema_class=GetFileParams, output_schema_class=GetFileNodesResponse, examples=examples["/figma/get_all_nodes"])
async def get_all_nodes(
    params: Dict[str, Any] = Body(...),
    service: FigmaService = Depends(get_figma_service)
):
    try:
        validated_params = GetFileParams(**params)
        return service.get_all_nodes(validated_params.file_key)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetFileParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
