from fastapi import APIRouter, Body, Depends, HTTPException
from starlette.requests import Request as FastAPIRequest
from typing import Dict, Any
from .schema import (
    GetSessionParams,
    CreateSessionParams,
    UpdateSessionParams,
    ListSessionsParams,
    GetContextParams,
    CreateContextParams,
    DeleteContextParams,
    SessionLogsParams,
    SessionRecordingParams,
    SessionDebugParams,
    SessionDownloadsParams,
    SessionUploadsParams,
    ValidateApiKeyParams,
    ApiResponse,
    ListProjectsParams,
    GetProjectParams,
    GetProjectUsageParams,
    GetExtensionParams,
    DeleteExtensionParams,
    UploadExtensionParams
)
from .service import BrowserBaseService
from .client import BrowserBaseClient
from ..common.auth import validate_provider_api_key
from ..common.input_schema_decorator import schema
from ..common.utils import (
    apply_error_handler_to_service, 
    apply_error_handler_to_router, 
    apply_error_handler_to_client
)
from ..common.examples_handler import ExamplesLoader

router = APIRouter(prefix="/browserbase", tags=["browserbase"])
examples = ExamplesLoader()

async def get_browser_base_service(request: FastAPIRequest):
    try:
        api_key = await validate_provider_api_key(request, "browser-base")
        client = BrowserBaseClient(api_key)
        apply_error_handler_to_client(client)
        service = BrowserBaseService(client)
        
        apply_error_handler_to_service(service)
        
        return service
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Failed to initialize BrowserBase service: {str(e)}"
        )

@router.post("/get_session", response_model=ApiResponse)
@schema(
    input_schema_class=GetSessionParams,
    output_schema_class=ApiResponse,
    examples=examples["/browserbase/get_session"]
)
async def get_session(
    params: Dict[str, Any] = Body(...),
    service: BrowserBaseService = Depends(get_browser_base_service)
):
    validated_params = GetSessionParams(**params)
    return service.get_session(validated_params.id)

@router.post("/create_session", response_model=ApiResponse)
@schema(
    input_schema_class=CreateSessionParams,
    output_schema_class=ApiResponse,
    examples=examples["/browserbase/create_session"]
)
async def create_session(
    params: Dict[str, Any] = Body(...),
    service: BrowserBaseService = Depends(get_browser_base_service)
):
    validated_params = CreateSessionParams(**params)
    return service.create_session(validated_params.model_dump(exclude_none=True))

@router.post("/update_session", response_model=ApiResponse)
@schema(
    input_schema_class=UpdateSessionParams,
    output_schema_class=ApiResponse,
    examples=examples["/browserbase/update_session"]
)
async def update_session(
    params: Dict[str, Any] = Body(...),
    service: BrowserBaseService = Depends(get_browser_base_service)
):
    validated_params = UpdateSessionParams(**params)
    session_id = validated_params.id
    update_data = validated_params.model_dump(exclude={"id"}, exclude_none=True)
    return service.update_session(session_id, update_data)

@router.post("/list_sessions", response_model=ApiResponse)
@schema(
    input_schema_class=ListSessionsParams,
    output_schema_class=ApiResponse,
    examples=examples["/browserbase/list_sessions"]
)
async def list_sessions(
    params: Dict[str, Any] = Body(...),
    service: BrowserBaseService = Depends(get_browser_base_service)
):
    validated_params = ListSessionsParams(**params)
    return service.list_sessions(validated_params.model_dump(exclude_none=True))

@router.post("/get_context", response_model=ApiResponse)
@schema(
    input_schema_class=GetContextParams,
    output_schema_class=ApiResponse,
    examples=examples["/browserbase/get_context"]
)
async def get_context(
    params: Dict[str, Any] = Body(...),
    service: BrowserBaseService = Depends(get_browser_base_service)
):
    validated_params = GetContextParams(**params)
    return service.get_context(validated_params.id)

@router.post("/create_context", response_model=ApiResponse)
@schema(
    input_schema_class=CreateContextParams,
    output_schema_class=ApiResponse,
    examples=examples["/browserbase/create_context"]
)
async def create_context(
    params: Dict[str, Any] = Body(...),
    service: BrowserBaseService = Depends(get_browser_base_service)
):
    validated_params = CreateContextParams(**params)
    return service.create_context(validated_params.model_dump(exclude_none=True))

@router.post("/delete_context")
@schema(
    input_schema_class=DeleteContextParams,
    output_schema_class=None
)
async def delete_context(
    params: Dict[str, Any] = Body(...),
    service: BrowserBaseService = Depends(get_browser_base_service)
):
    validated_params = DeleteContextParams(**params)
    return service.delete_context(validated_params.id)

@router.post("/session_logs", response_model=ApiResponse)
@schema(
    input_schema_class=SessionLogsParams,
    output_schema_class=ApiResponse,
    examples=examples["/browserbase/session_logs"]
)
async def session_logs(
    params: Dict[str, Any] = Body(...),
    service: BrowserBaseService = Depends(get_browser_base_service)
):
    validated_params = SessionLogsParams(**params)
    return service.get_session_logs(validated_params.id)

@router.post("/session_recording", response_model=ApiResponse)
@schema(
    input_schema_class=SessionRecordingParams,
    output_schema_class=ApiResponse,
    examples=examples["/browserbase/session_recording"]
)
async def session_recording(
    params: Dict[str, Any] = Body(...),
    service: BrowserBaseService = Depends(get_browser_base_service)
):
    validated_params = SessionRecordingParams(**params)
    return service.get_session_recording(validated_params.id)

@router.post("/session_debug", response_model=ApiResponse)
@schema(
    input_schema_class=SessionDebugParams,
    output_schema_class=ApiResponse,
    examples=examples["/browserbase/session_debug"]
)
async def session_debug(
    params: Dict[str, Any] = Body(...),
    service: BrowserBaseService = Depends(get_browser_base_service)
):
    validated_params = SessionDebugParams(**params)
    return service.get_session_debug(validated_params.id)

@router.post("/session_downloads")
@schema(
    input_schema_class=SessionDownloadsParams,
    output_schema_class=None,
    examples=examples["/browserbase/session_downloads"]
)
async def session_downloads(
    params: Dict[str, Any] = Body(...),
    service: BrowserBaseService = Depends(get_browser_base_service)
):
    validated_params = SessionDownloadsParams(**params)
    return service.get_session_downloads(validated_params.id)

@router.post("/session_uploads", response_model=ApiResponse)
@schema(
    input_schema_class=SessionUploadsParams,
    output_schema_class=ApiResponse,
    examples=examples["/browserbase/session_uploads"]
)
async def session_uploads(
    params: Dict[str, Any] = Body(...),
    service: BrowserBaseService = Depends(get_browser_base_service)
):
    validated_params = SessionUploadsParams(**params)
    return service.create_session_uploads(validated_params.id, validated_params.file)

@router.post("/list_projects", response_model=ApiResponse)
@schema(
    input_schema_class=ListProjectsParams,
    output_schema_class=ApiResponse,
    examples=examples["/browserbase/list_projects"]
)
async def list_projects(
    params: Dict[str, Any] = Body(...),
    service: BrowserBaseService = Depends(get_browser_base_service)
):
    return service.list_projects()

@router.post("/get_project", response_model=ApiResponse)
@schema(
    input_schema_class=GetProjectParams,
    output_schema_class=ApiResponse,
    examples=examples["/browserbase/get_project"]
)
async def get_project(
    params: Dict[str, Any] = Body(...),
    service: BrowserBaseService = Depends(get_browser_base_service)
):
    validated_params = GetProjectParams(**params)
    return service.get_project(validated_params.id)

@router.post("/get_project_usage", response_model=ApiResponse)
@schema(
    input_schema_class=GetProjectUsageParams,
    output_schema_class=ApiResponse,
    examples=examples["/browserbase/get_project_usage"]
)
async def get_project_usage(
    params: Dict[str, Any] = Body(...),
    service: BrowserBaseService = Depends(get_browser_base_service)
):
    validated_params = GetProjectUsageParams(**params)
    return service.get_project_usage(validated_params.id)

@router.post("/get_extension", response_model=ApiResponse)
@schema(
    input_schema_class=GetExtensionParams,
    output_schema_class=ApiResponse,
    examples=examples["/browserbase/get_extension"]
)
async def get_extension(
    params: Dict[str, Any] = Body(...),
    service: BrowserBaseService = Depends(get_browser_base_service)
):
    validated_params = GetExtensionParams(**params)
    return service.get_extension(validated_params.id)

@router.post("/delete_extension")
@schema(
    input_schema_class=DeleteExtensionParams,
    output_schema_class=None,
    examples=examples["/browserbase/delete_extension"]
)
async def delete_extension(
    params: Dict[str, Any] = Body(...),
    service: BrowserBaseService = Depends(get_browser_base_service)
):
    validated_params = DeleteExtensionParams(**params)
    return service.delete_extension(validated_params.id)

@router.post("/upload_extension", response_model=ApiResponse)
@schema(
    input_schema_class=UploadExtensionParams,
    output_schema_class=ApiResponse,
    examples=examples["/browserbase/upload_extension"]
)
async def upload_extension(
    params: Dict[str, Any] = Body(...),
    service: BrowserBaseService = Depends(get_browser_base_service)
):
    validated_params = UploadExtensionParams(**params)
    return service.upload_extension(validated_params.file, validated_params.projectId)

@router.post("/validate_key")
async def validate_key(
    params: Dict[str, Any] = Body(...)
):
    try:
        api_key = params.get("api_key")
        if not api_key:
            return {"valid": False, "message": "API key is required"}
        
        client = BrowserBaseClient(api_key=api_key)
        is_valid = client.list_projects()
        if is_valid:
            return {"valid": True, "message": "API key is valid"}
        else:
            return {"valid": False, "message": "Invalid API key"}
    except Exception as e:
        return {"valid": False, "message": f"Invalid API key: {str(e)}"}


apply_error_handler_to_router(router)
