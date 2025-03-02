from fastapi import APIRouter, Depends, HTTPException, Request as FastAPIRequest, Body
from typing import Optional, Dict, Any
from .schema import (
    FileList, FileFilters, FolderCreate, FileMove, DropboxFile, ApiResponse,
    ListFilesParams, GetFileParams, CreateFolderParams, UploadFileParams,
    DownloadFileParams, DeleteFileParams, MoveFileParams, ReadFileParams,
    ListFilesResponse, GetFileResponse, CreateFolderResponse, UploadFileResponse,
    DownloadFileResponse, DeleteFileResponse, MoveFileResponse, ReadFileResponse,
    CreateSharedLinkParams, CreateSharedLinkResponse,
    SearchParams, SearchContinueParams, SearchResponse, SearchContinueResponse
)
from .service import DropboxService
from .client import DropboxClient
import os
from pydantic import ValidationError
from ..common.input_schema_decorator import schema, input_schema, output_schema
from ..common.utils import format_validation_error
from ..common.auth import TokenService, DropboxTokenRefresher
from ..common.examples_handler import ExamplesLoader

router = APIRouter(prefix="/dropbox", tags=["dropbox"])

examples = ExamplesLoader() 

async def get_dropbox_service(request: FastAPIRequest) -> DropboxService:
    try:
        token_data = await TokenService.get_user_token(request, 'dropbox')
        
        if TokenService.is_token_expired(token_data):
            try:
                token_data = await DropboxTokenRefresher.refresh(request, token_data)
            except Exception as e:
                raise HTTPException(status_code=401, detail=f"Failed to refresh token: {str(e)}")
        
        return DropboxService(token_data['access_token'])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize Dropbox service: {str(e)}")

@router.post("/list_files", response_model=ApiResponse)
@schema(input_schema_class=ListFilesParams, output_schema_class=ListFilesResponse, examples=examples["/dropbox/list_files"])
async def list_files(
    params: Dict[str, Any] = Body(...),
    service: DropboxService = Depends(get_dropbox_service)
):
    try:
        validated_params = ListFilesParams(**params)
        return service.list_files(validated_params.filters)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'ListFilesParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_file", response_model=ApiResponse)
@schema(input_schema_class=GetFileParams, output_schema_class=GetFileResponse, examples=examples["/dropbox/get_file"])
async def get_file(
    params: Dict[str, Any] = Body(...),
    service: DropboxService = Depends(get_dropbox_service)
):
    try:
        validated_params = GetFileParams(**params)
        return service.get_file(validated_params.path)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetFileParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/create_folder", response_model=ApiResponse)
@schema(input_schema_class=CreateFolderParams, output_schema_class=CreateFolderResponse, examples=examples["/dropbox/create_folder"])
async def create_folder(
    params: Dict[str, Any] = Body(...),
    service: DropboxService = Depends(get_dropbox_service)
):
    try:
        validated_params = CreateFolderParams(**params)
        return service.create_folder(validated_params.folder.path, validated_params.autorename)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        # Check if this is a 409 Conflict error
        if "409 Client Error: Conflict for url" in str(e):
            raise HTTPException(status_code=409, detail="Folder with this name already exists")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/upload_file", response_model=ApiResponse)
@schema(input_schema_class=UploadFileParams, output_schema_class=UploadFileResponse, examples=examples["/dropbox/upload_file"])
async def upload_file(
    params: Dict[str, Any] = Body(...),
    service: DropboxService = Depends(get_dropbox_service)
):
    try:
        validated_params = UploadFileParams(**params)
        return service.upload_file_b64(
            validated_params.path, 
            validated_params.file_content, 
            validated_params.mode
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'UploadFileParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/download_file")
@schema(input_schema_class=DownloadFileParams, output_schema_class=DownloadFileResponse, examples=examples["/dropbox/download_file"])
async def download_file(
    params: Dict[str, Any] = Body(...),
    service: DropboxService = Depends(get_dropbox_service)
):
    try:
        validated_params = DownloadFileParams(**params)
        return service.download_file_b64(validated_params.path)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'DownloadFileParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        if hasattr(e, 'response') and e.response.status_code == 400:
            raise HTTPException(status_code=404, detail="File not found")
        raise HTTPException(status_code=500, detail=f"Download error: {str(e)}")

@router.post("/delete_file", response_model=ApiResponse)
@schema(input_schema_class=DeleteFileParams, output_schema_class=DeleteFileResponse, examples=examples["/dropbox/delete_file"])
async def delete_file(
    params: Dict[str, Any] = Body(...),
    service: DropboxService = Depends(get_dropbox_service)
):
    try:
        validated_params = DeleteFileParams(**params)
        return service.delete_file(validated_params.path)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'DeleteFileParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/move_file", response_model=ApiResponse)
@schema(input_schema_class=MoveFileParams, output_schema_class=MoveFileResponse, examples=examples["/dropbox/move_file"])
async def move_file(
    params: Dict[str, Any] = Body(...),
    service: DropboxService = Depends(get_dropbox_service)
):
    try:
        validated_params = MoveFileParams(**params)
        return service.move_file(validated_params.from_path, validated_params.to_path)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'MoveFileParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/read_file")
@schema(input_schema_class=ReadFileParams, output_schema_class=ReadFileResponse, examples=examples["/dropbox/read_file"])
async def read_file(
    params: Dict[str, Any] = Body(...),
    service: DropboxService = Depends(get_dropbox_service)
):
    try:
        validated_params = ReadFileParams(**params)
        return service.read_file_content(validated_params.path)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'ReadFileParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }

@router.post("/create_shared_link", response_model=ApiResponse)
@schema(input_schema_class=CreateSharedLinkParams, output_schema_class=CreateSharedLinkResponse, examples=examples["/dropbox/create_shared_link"])
async def create_shared_link(
    params: Dict[str, Any] = Body(...),
    service: DropboxService = Depends(get_dropbox_service)
):
    try:
        validated_params = CreateSharedLinkParams(**params)
        
        # Convert the settings to a dict and ensure enum values are converted to strings
        settings_dict = None
        if validated_params.settings:
            settings_dict = validated_params.settings.dict()
            # The dict() method will automatically convert enum values to their string values
        
        return service.create_shared_link(validated_params.path, settings_dict)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'CreateSharedLinkParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        if "shared_link_already_exists" in str(e):
            # This is handled in the service layer
            pass
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/search", response_model=ApiResponse)
@schema(input_schema_class=SearchParams, output_schema_class=SearchResponse, examples=examples["/dropbox/search"])
async def search_files(
    params: Dict[str, Any] = Body(...),
    service: DropboxService = Depends(get_dropbox_service)
):
    try:
        validated_params = SearchParams(**params)
        return service.search_files(
            query=validated_params.query,
            path=validated_params.path,
            max_results=validated_params.max_results,
            filename_only=validated_params.filename_only,
            file_status=validated_params.file_status
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'SearchParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search_continue", response_model=ApiResponse)
@schema(input_schema_class=SearchContinueParams, output_schema_class=SearchContinueResponse, examples=examples["/dropbox/search_continue"])
async def search_continue(
    params: Dict[str, Any] = Body(...),
    service: DropboxService = Depends(get_dropbox_service)
):
    try:
        validated_params = SearchContinueParams(**params)
        return service.search_continue(validated_params.cursor)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'SearchContinueParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))