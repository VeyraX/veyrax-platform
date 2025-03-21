from fastapi import APIRouter, Body, Depends, HTTPException
from starlette.requests import Request as FastAPIRequest
from typing import Dict, Any
from .schema import (
    UploadParams,
    ExplicitParams,
    ListAssetsParams,
    GetAssetDetailsParams,
    DeleteAssetParams,
    RenameAssetParams,
    ApiResponse
)
from .service import CloudinaryService
from .client import CloudinaryClient, CloudinaryAPIError
from ..common.auth import get_provider_custom_auth
from ..common.input_schema_decorator import schema
from ..common.utils import apply_error_handler_to_service, apply_error_handler_to_router, apply_error_handler_to_client
from ..common.examples_handler import ExamplesLoader

router = APIRouter(prefix="/cloudinary", tags=["cloudinary"])
examples = ExamplesLoader()

async def get_cloudinary_service(request: FastAPIRequest):
    try:
        auth_params = await get_provider_custom_auth(request, "cloudinary")
        
        cloud_name = auth_params.get("cloud_name")
        api_key = auth_params.get("api_key")
        api_secret = auth_params.get("api_secret")
        
        if not cloud_name:
            raise HTTPException(
                status_code=401,
                detail="Missing required parameter: cloud_name"
            )
        
        if not api_key:
            raise HTTPException(
                status_code=401,
                detail="Missing required parameter: api_key"
            )
        
        if not api_secret:
            raise HTTPException(
                status_code=401,
                detail="Missing required parameter: api_secret"
            )
        
        client = CloudinaryClient(cloud_name, api_key, api_secret)
        apply_error_handler_to_client(client)
        
        service = CloudinaryService(client)
        apply_error_handler_to_service(service)
        
        return service
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Failed to initialize Cloudinary service: {str(e)}"
        )

@router.post("/upload", response_model=ApiResponse)
@schema(
    input_schema_class=UploadParams,
    output_schema_class=ApiResponse,
    examples=examples["/cloudinary/upload"]
)
async def upload(
    params: Dict[str, Any] = Body(...),
    service: CloudinaryService = Depends(get_cloudinary_service)
):
    try:
        # Validate input parameters
        if "file" not in params or not params["file"]:
            raise HTTPException(
                status_code=400,
                detail="Missing required parameter: file"
            )
        
        validated_params = UploadParams(**params)
        return service.upload(validated_params)
    except HTTPException:
        raise
    except Exception as e:
        # Convert validation errors to HTTP exceptions
        raise HTTPException(
            status_code=400,
            detail=f"Invalid request parameters: {str(e)}"
        )

@router.post("/explicit", response_model=ApiResponse)
@schema(
    input_schema_class=ExplicitParams,
    output_schema_class=ApiResponse,
    examples=examples["/cloudinary/explicit"]
)
async def explicit(
    params: Dict[str, Any] = Body(...),
    service: CloudinaryService = Depends(get_cloudinary_service)
):
    try:
        validated_params = ExplicitParams(**params)
        return service.explicit(validated_params)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid request parameters: {str(e)}"
        )

@router.post("/list_assets", response_model=ApiResponse)
@schema(
    input_schema_class=ListAssetsParams,
    output_schema_class=ApiResponse,
    examples=examples["/cloudinary/list_assets"]
)
async def list_assets(
    params: Dict[str, Any] = Body(...),
    service: CloudinaryService = Depends(get_cloudinary_service)
):
    try:
        validated_params = ListAssetsParams(**params)
        return service.list_assets(validated_params)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid request parameters: {str(e)}"
        )

@router.post("/get_asset_details", response_model=ApiResponse)
@schema(
    input_schema_class=GetAssetDetailsParams,
    output_schema_class=ApiResponse,
    examples=examples["/cloudinary/get_asset_details"]
)
async def get_asset_details(
    params: Dict[str, Any] = Body(...),
    service: CloudinaryService = Depends(get_cloudinary_service)
):
    try:
        validated_params = GetAssetDetailsParams(**params)
        return service.get_asset_details(validated_params)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid request parameters: {str(e)}"
        )

@router.post("/delete_asset", response_model=ApiResponse)
@schema(
    input_schema_class=DeleteAssetParams,
    output_schema_class=ApiResponse,
    examples=examples["/cloudinary/delete_asset"]
)
async def delete_asset(
    params: Dict[str, Any] = Body(...),
    service: CloudinaryService = Depends(get_cloudinary_service)
):
    try:
        validated_params = DeleteAssetParams(**params)
        return service.delete_asset(validated_params)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid request parameters: {str(e)}"
        )

@router.post("/rename_asset", response_model=ApiResponse)
@schema(
    input_schema_class=RenameAssetParams,
    output_schema_class=ApiResponse,
    examples=examples["/cloudinary/rename_asset"]
)
async def rename_asset(
    params: Dict[str, Any] = Body(...),
    service: CloudinaryService = Depends(get_cloudinary_service)
):
    try:
        validated_params = RenameAssetParams(**params)
        return service.rename_asset(validated_params)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid request parameters: {str(e)}"
        )

@router.post("/validate_key")
async def validate_key(
    params: Dict[str, Any] = Body(...),
):
    try:
        cloud_name = params.get("cloud_name")
        api_key = params.get("api_key")
        api_secret = params.get("api_secret")
        
        if not cloud_name:
            return {
                "valid": False, 
                "message": "Missing required parameter: cloud_name"
            }
        
        if not api_key:
            return {
                "valid": False, 
                "message": "Missing required parameter: api_key"
            }
        
        if not api_secret:
            return {
                "valid": False, 
                "message": "Missing required parameter: api_secret"
            }
        
        client = CloudinaryClient(cloud_name, api_key, api_secret)
        
        # Test the API key with a simple list operation with minimal results
        test_params = {"max_results": 1}
        client.list_assets(test_params)
        
        return {"valid": True, "message": "Cloudinary credentials are valid"}
    except CloudinaryAPIError as e:
        return {"valid": False, "message": f"Invalid Cloudinary credentials: {e.message}"}
    except Exception as e:
        return {"valid": False, "message": f"Invalid Cloudinary credentials: {str(e)}"}

apply_error_handler_to_router(router) 