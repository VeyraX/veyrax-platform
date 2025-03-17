from fastapi import APIRouter, Depends, HTTPException, Request, Body
from typing import Dict, Any
from .schema import (
    SandboxCreateRequest,
    SandboxPauseRequest,
    SandboxResumeRequest,
    SandboxTerminateRequest,
    SandboxRunCommandRequest,
    SandboxListRequest,
    CodeExecutionRequest,
    FileListRequest,
    GetHostRequest,
    GetHostResponse,
    E2BBaseResponse 
)
from .service import E2BService
from .client import E2BClient
from ..common.auth import validate_provider_api_key
from ..common.input_schema_decorator import schema
from ..common.utils import apply_error_handler_to_service, apply_error_handler_to_router
from ..common.examples_handler import ExamplesLoader

router = APIRouter(prefix="/e2b", tags=["e2b"])
examples = ExamplesLoader()

async def get_e2b_service(request: Request):
    try:
        api_key = await validate_provider_api_key(request, "e2b")
        client = E2BClient(api_key)
        service = E2BService(client)
        apply_error_handler_to_service(service)
        return service
    except Exception as e:
        raise HTTPException(500, f"Failed to initialize E2B service: {str(e)}")

@router.post("/create_sandbox", response_model=E2BBaseResponse)
@schema(
    input_schema_class=SandboxCreateRequest,
    output_schema_class=E2BBaseResponse,
    examples=examples["/e2b/create_sandbox"]
)
async def create_sandbox(
    params: Dict[str, Any] = Body(...),
    service: E2BService = Depends(get_e2b_service)
):
    validated = SandboxCreateRequest(**params)
    return service.create_sandbox(validated)

@router.post("/list_sandboxes", response_model=E2BBaseResponse)
@schema(
    input_schema_class=SandboxListRequest,
    output_schema_class=E2BBaseResponse,
    examples=examples["/e2b/list_sandboxes"]
)
async def list_sandboxes(
    params: Dict[str, Any] = Body(...),
    service: E2BService = Depends(get_e2b_service)
):
    validated = SandboxListRequest(**params)
    return service.list_sandboxes(validated)

@router.post("/run_command", response_model=E2BBaseResponse)
@schema(
    input_schema_class=SandboxRunCommandRequest,
    output_schema_class=E2BBaseResponse,
    examples=examples["/e2b/run_command"]
)
async def run_command(
    params: Dict[str, Any] = Body(...),
    service: E2BService = Depends(get_e2b_service)
):
    validated = SandboxRunCommandRequest(**params)
    return service.run_command(validated)

@schema(
    input_schema_class=GetHostRequest,
    output_schema_class=GetHostResponse,
    examples=examples["/e2b/get_host"]
)
async def get_host(
    params: Dict[str, Any] = Body(...),
    service: E2BService = Depends(get_e2b_service)
):
    validated = GetHostRequest(**params)
    return service.get_host(validated)

## DO NOT DELETE: IMPLEMENTED METHODS, BUT THEY ARE IN BETA VERSION ON E2B, SO THEY ARE NOT WORKING PUBLIC YET.
# @router.post("/pause_sandbox", response_model=E2BBaseResponse)
# @schema(
#     input_schema_class=SandboxPauseRequest,
#     output_schema_class=E2BBaseResponse,
#     examples=examples["/e2b/pause_sandbox"]
# )
# async def pause_sandbox(
#     params: Dict[str, Any] = Body(...),
#     service: E2BService = Depends(get_e2b_service)
# ):
#     validated = SandboxPauseRequest(**params)
#     return service.pause_sandbox(validated)

# @router.post("/resume_sandbox", response_model=E2BBaseResponse)
# @schema(
#     input_schema_class=SandboxResumeRequest,
#     output_schema_class=E2BBaseResponse,
#     examples=examples["/e2b/resume_sandbox"]
# )
# async def resume_sandbox(
#     params: Dict[str, Any] = Body(...),
#     service: E2BService = Depends(get_e2b_service)
# ):
#     validated = SandboxResumeRequest(**params)
#     return service.resume_sandbox(validated)

@router.post("/run_code", response_model=E2BBaseResponse)
@schema(
    input_schema_class=CodeExecutionRequest,
    output_schema_class=E2BBaseResponse,
    examples=examples["/e2b/run_code"]
)
async def run_code(
    params: Dict[str, Any] = Body(...),
    service: E2BService = Depends(get_e2b_service)
):
    validated = CodeExecutionRequest(**params)
    return service.run_code(validated)


@router.post("/kill_sandbox", response_model=E2BBaseResponse)
@schema(
    input_schema_class=SandboxTerminateRequest,
    output_schema_class=E2BBaseResponse,
    examples=examples["/e2b/kill_sandbox"]
)
async def kill_sandbox(
    params: Dict[str, Any] = Body(...),
    service: E2BService = Depends(get_e2b_service)
):
    validated = SandboxTerminateRequest(**params)
    return service.kill_sandbox(validated)
