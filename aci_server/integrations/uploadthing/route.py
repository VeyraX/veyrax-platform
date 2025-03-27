from fastapi import APIRouter, Body, Depends, HTTPException, Header
from starlette.requests import Request as FastAPIRequest
from typing import Dict, Any, Optional
from .schema import (
    ListFilesParams,
    ListFilesResponse,
    PollUploadParams,
    PollUploadResponse,
    GetServerCallbackParams,
    GetServerCallbackResponse,
    SetServerCallbackParams,
    SetServerCallbackResponse,
    PrepareUploadParams,
    PrepareUploadResponse,
    UploadFilesParams,
    UploadFilesResponse,
    UploadFromUrlParams,
    UploadFromUrlResponse,
    RenameFilesParams,
    RenameFilesResponse,
    DeleteFilesParams,
    DeleteFilesResponse,
    GetAppInfoParams,
    GetAppInfoResponse,
    GetUsageInfoParams,
    GetUsageInfoResponse,
    FileToUpload,
    ApiResponse
)
from .service import UploadThingService
from .client import UploadThingClient
from ..common.auth import validate_provider_api_key
from ..common.input_schema_decorator import schema
from ..common.utils import apply_error_handler_to_service, apply_error_handler_to_router, apply_error_handler_to_client
from ..common.examples_handler import ExamplesLoader
import requests
import tempfile
import os


router = APIRouter(prefix="/uploadthing", tags=["uploadthing"])
examples = ExamplesLoader()

async def get_uploadthing_service(request: FastAPIRequest):
    try:
        api_key = await validate_provider_api_key(request, "uploadthing")
        client = UploadThingClient(api_key)
        apply_error_handler_to_client(client)
        service = UploadThingService(client)
        
        apply_error_handler_to_service(service)
        
        return service
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Failed to initialize UploadThing service: {str(e)}"
        )

@router.post("/list_files", response_model=ApiResponse)
@schema(
    input_schema_class=ListFilesParams,
    output_schema_class=ListFilesResponse,
    examples=examples["/uploadthing/list_files"]
)
async def list_files(
    params: Dict[str, Any] = Body(...),
    service: UploadThingService = Depends(get_uploadthing_service)
):
    validated_params = ListFilesParams(**params)
    return service.list_files(validated_params)

@router.post("/poll_upload", response_model=ApiResponse)
@schema(
    input_schema_class=PollUploadParams,
    output_schema_class=PollUploadResponse,
    examples=examples["/uploadthing/poll_upload"]
)
async def poll_upload(
    params: Dict[str, Any] = Body(...),
    service: UploadThingService = Depends(get_uploadthing_service)
):
    validated_params = PollUploadParams(**params)
    return service.poll_upload(validated_params)

@router.get("/get_server_callback", response_model=ApiResponse)
@schema(
    input_schema_class=GetServerCallbackParams,
    output_schema_class=GetServerCallbackResponse,
    examples=examples["/uploadthing/get_server_callback"]
)
async def get_server_callback(
    authorization: str = Header(...),
    service: UploadThingService = Depends(get_uploadthing_service)
):
    validated_params = GetServerCallbackParams(authorization=authorization)
    return service.get_server_callback(validated_params)

@router.post("/set_server_callback", response_model=ApiResponse)
@schema(
    input_schema_class=SetServerCallbackParams,
    output_schema_class=SetServerCallbackResponse,
    examples=examples["/uploadthing/set_server_callback"]
)
async def set_server_callback(
    params: Dict[str, Any] = Body(...),
    service: UploadThingService = Depends(get_uploadthing_service)
):
    validated_params = SetServerCallbackParams(**params)
    return service.set_server_callback(validated_params)

@router.post("/prepare_upload", response_model=ApiResponse)
@schema(
    input_schema_class=PrepareUploadParams,
    output_schema_class=PrepareUploadResponse,
    examples=examples["/uploadthing/prepare_upload"]
)
async def prepare_upload(
    params: Dict[str, Any] = Body(...),
    service: UploadThingService = Depends(get_uploadthing_service)
):
    validated_params = PrepareUploadParams(**params)
    return service.prepare_upload(validated_params)

@router.post("/upload_files", response_model=ApiResponse)
@schema(
    input_schema_class=UploadFilesParams,
    output_schema_class=UploadFilesResponse,
    examples=examples["/uploadthing/upload_files"]
)
async def upload_files(
    params: Dict[str, Any] = Body(...),
    service: UploadThingService = Depends(get_uploadthing_service)
):
    validated_params = UploadFilesParams(**params)
    return service.upload_files(validated_params)

@router.post("/validate_key")
async def validate_key(
    params: Dict[str, Any] = Body(...),
):
    try:
        api_key = params.get("api_key")
        if not api_key:
            return {"valid": False, "message": "API key is required"}
        
        client = UploadThingClient(api_key=api_key)
        valid = client.test_connection()
        
        if valid:
            return {"valid": True, "message": "API key is valid"}
        else:
            return {"valid": False, "message": "Invalid API key"}
    except Exception as e:
        return {"valid": False, "message": f"Invalid API key: {str(e)}"}

@router.post("/upload_from_url", response_model=ApiResponse)
@schema(
    input_schema_class=UploadFromUrlParams,
    output_schema_class=UploadFromUrlResponse,
    examples=examples["/uploadthing/upload_from_url"]
)
async def upload_from_url(
    params: Dict[str, Any] = Body(...),
    service: UploadThingService = Depends(get_uploadthing_service)
):
    validated_params = UploadFromUrlParams(**params)
    return service.upload_from_url(validated_params)

def upload_uploadthing_file(data):
    upload_data = data
    upload_url = upload_data.url
    fields = upload_data.fields
    file_path = "/app/integrations/uploadthing/component.json"  # Local path to file

    with open(file_path, "rb") as f:
        files = {
            "file": (fields["key"], f, fields["Content-Type"])
        }
        response = requests.post(upload_url, data=fields, files=files)

    if response.ok:
        print("✅ Upload succeeded:", upload_data.fileUrl)
    else:
        print("❌ Upload failed:", response.status_code, response.text)

@router.post("/debug_upload", response_model=ApiResponse)
@schema(
    input_schema_class=ListFilesParams,
    output_schema_class=ListFilesResponse
)
async def get_test_file_params(
    params: Dict[str, Any] = Body(...),
    service: UploadThingService = Depends(get_uploadthing_service)
):
    root_dir = "/app/integrations/uploadthing/"
    params = service._get_file_params(root_dir+"component.json")

    params = PrepareUploadParams(
        callbackUrl="https://example.com/callback",
        callbackSlug="test-callback",
        files=[params],
        routeConfig=["blob"],
        metadata={}
    )

    data = service.prepare_upload(params)

    print("[get_test_file_params] data", data)

    files_for_upload = data.data
    for data_for_upload  in files_for_upload:
        upload_uploadthing_file(data_for_upload)
    return params

def upload_from_url_helper(url: str, upload_data):
    # Download the file from URL
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    upload_url = upload_data.url
    fields = upload_data.fields
    
    # Create a temporary file to store the downloaded content
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        try:
            # Write the downloaded content to the temporary file
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    temp_file.write(chunk)
            
            temp_file.flush()
            
            # Upload the temporary file
            with open(temp_file.name, "rb") as f:
                files = {
                    "file": (fields["key"], f, fields.get("Content-Type", "application/octet-stream"))
                }
                upload_response = requests.post(upload_url, data=fields, files=files)
            
            if upload_response.ok:
                print("✅ Upload succeeded:", upload_data.fileUrl)
                return True
            else:
                print("❌ Upload failed:", upload_response.status_code, upload_response.text)
                return False
        finally:
            # Clean up the temporary file
            try:
                os.unlink(temp_file.name)
            except Exception:
                pass

@router.post("/debug_upload_from_url", response_model=ApiResponse)
@schema(
    input_schema_class=UploadFromUrlParams,
    output_schema_class=UploadFromUrlResponse
)
async def debug_upload_from_url(
    params: Dict[str, Any] = Body(...),
    service: UploadThingService = Depends(get_uploadthing_service)
):
    validated_params = UploadFromUrlParams(**params)
    
    # Get file parameters from URL
    file_params = service._get_file_params_from_url(str(validated_params.url), validated_params.customId)
    
    # Create FileToUpload object
    file_to_upload = FileToUpload(
        name=file_params["name"],
        size=file_params["size"],
        customId=validated_params.customId
    )
    
    # Create PrepareUploadParams
    prepare_params = PrepareUploadParams(
        callbackUrl=validated_params.callbackUrl,
        callbackSlug=validated_params.callbackSlug,
        files=[file_to_upload],
        routeConfig=validated_params.routeConfig,
        metadata=validated_params.metadata
    )
    
    # Prepare the upload
    data = service.prepare_upload(prepare_params)
    
    print("[debug_upload_from_url] data", data)
    
    # Upload each prepared file
    success = True
    files_for_upload = data.data
    for upload_data in files_for_upload:
        if hasattr(upload_data, "url") and hasattr(upload_data, "fields"):
            # Single-part upload
            success = upload_from_url_helper(str(validated_params.url), upload_data) and success
    
    return data

@router.post("/rename_files", response_model=ApiResponse)
@schema(
    input_schema_class=RenameFilesParams,
    output_schema_class=RenameFilesResponse,
    examples=examples["/uploadthing/rename_files"]
)
async def rename_files(
    params: Dict[str, Any] = Body(...),
    service: UploadThingService = Depends(get_uploadthing_service)
):
    validated_params = RenameFilesParams(**params)
    return service.rename_files(validated_params)

@router.post("/delete_files", response_model=ApiResponse)
@schema(
    input_schema_class=DeleteFilesParams,
    output_schema_class=DeleteFilesResponse,
    examples=examples["/uploadthing/delete_files"]
)
async def delete_files(
    params: Dict[str, Any] = Body(...),
    service: UploadThingService = Depends(get_uploadthing_service)
):
    validated_params = DeleteFilesParams(**params)
    return service.delete_files(validated_params)

@router.post("/get_app_info", response_model=ApiResponse)
@schema(
    input_schema_class=GetAppInfoParams,
    output_schema_class=GetAppInfoResponse,
    examples=examples["/uploadthing/get_app_info"]
)
async def get_app_info(
    service: UploadThingService = Depends(get_uploadthing_service)
):
    return service.get_app_info()

@router.post("/get_usage_info", response_model=ApiResponse)
@schema(
    input_schema_class=GetUsageInfoParams,
    output_schema_class=GetUsageInfoResponse,
    examples=examples["/uploadthing/get_usage_info"]
)
async def get_usage_info(
    service: UploadThingService = Depends(get_uploadthing_service)
):
    return service.get_usage_info()

apply_error_handler_to_router(router) 