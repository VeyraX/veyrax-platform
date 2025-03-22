from fastapi import APIRouter, Body, Depends, HTTPException
from starlette.requests import Request as FastAPIRequest
from typing import Dict, Any
from .schema import (
    GetProjectsParams,
    CreateProjectParams,
    GetProjectParams,
    UpdateProjectParams,
    DeleteProjectParams,
    GetCollaboratorsParams,
    GetSectionsParams,
    GetSectionParams,
    CreateSectionParams,
    UpdateSectionParams,
    DeleteSectionParams,
    GetTasksParams,
    GetTaskParams,
    CreateTaskParams,
    UpdateTaskParams,
    CloseTaskParams,
    ReopenTaskParams,
    DeleteTaskParams,
    GetProjectsResponse,
    CreateProjectResponse,
    GetProjectResponse,
    UpdateProjectResponse,
    DeleteProjectResponse,
    GetCollaboratorsResponse,
    GetSectionsResponse,
    GetSectionResponse,
    CreateSectionResponse,
    UpdateSectionResponse,
    DeleteSectionResponse,
    GetTasksResponse,
    GetTaskResponse,
    CreateTaskResponse,
    UpdateTaskResponse,
    CloseTaskResponse,
    ReopenTaskResponse,
    DeleteTaskResponse,
    ApiResponse,
    GetCommentsParams,
    GetCommentParams,
    CreateCommentParams,
    UpdateCommentParams,
    DeleteCommentParams,
    GetCommentsResponse,
    GetCommentResponse,
    CreateCommentResponse,
    UpdateCommentResponse,
    DeleteCommentResponse,
    GetPersonalLabelsParams,
    GetPersonalLabelParams,
    CreatePersonalLabelParams,
    UpdatePersonalLabelParams,
    DeletePersonalLabelParams,
    GetSharedLabelsParams,
    RenameSharedLabelParams,
    RemoveSharedLabelParams,
    GetPersonalLabelsResponse,
    GetPersonalLabelResponse,
    CreatePersonalLabelResponse,
    UpdatePersonalLabelResponse,
    DeletePersonalLabelResponse,
    GetSharedLabelsResponse,
    RenameSharedLabelResponse,
    RemoveSharedLabelResponse
)
from .service import TodoistService
from .client import TodoistClient
from ..common.auth import validate_provider_api_key
from ..common.input_schema_decorator import schema
from ..common.utils import apply_error_handler_to_service, apply_error_handler_to_router, apply_error_handler_to_client
from ..common.examples_handler import ExamplesLoader

router = APIRouter(prefix="/todoist", tags=["todoist"])
examples = ExamplesLoader()

async def get_todoist_service(request: FastAPIRequest):
    try:
        api_key = await validate_provider_api_key(request, "todoist")
        client = TodoistClient(api_key)
        apply_error_handler_to_client(client)
        service = TodoistService(client)
        
        apply_error_handler_to_service(service)
        
        return service
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Failed to initialize Todoist service: {str(e)}"
        )

@router.post("/get_projects", response_model=ApiResponse)
@schema(
    input_schema_class=GetProjectsParams,
    output_schema_class=GetProjectsResponse,
    examples=examples["/todoist/get_projects"]
)
async def get_projects(
    params: Dict[str, Any] = Body(...),
    service: TodoistService = Depends(get_todoist_service)
):
    validated_params = GetProjectsParams(**params)
    return service.get_projects(validated_params)

@router.post("/create_project", response_model=ApiResponse)
@schema(
    input_schema_class=CreateProjectParams,
    output_schema_class=CreateProjectResponse,
    examples=examples["/todoist/create_project"]
)
async def create_project(
    params: Dict[str, Any] = Body(...),
    service: TodoistService = Depends(get_todoist_service)
):
    validated_params = CreateProjectParams(**params)
    return service.create_project(validated_params)

@router.post("/get_project", response_model=ApiResponse)
@schema(
    input_schema_class=GetProjectParams,
    output_schema_class=GetProjectResponse,
    examples=examples["/todoist/get_project"]
)
async def get_project(
    params: Dict[str, Any] = Body(...),
    service: TodoistService = Depends(get_todoist_service)
):
    validated_params = GetProjectParams(**params)
    return service.get_project(validated_params.project_id)

@router.post("/update_project", response_model=ApiResponse)
@schema(
    input_schema_class=UpdateProjectParams,
    output_schema_class=UpdateProjectResponse,
    examples=examples["/todoist/update_project"]
)
async def update_project(
    params: Dict[str, Any] = Body(...),
    service: TodoistService = Depends(get_todoist_service)
):
    validated_params = UpdateProjectParams(**params)
    return service.update_project(validated_params.project_id, validated_params)

@router.post("/delete_project", response_model=ApiResponse)
@schema(
    input_schema_class=DeleteProjectParams,
    output_schema_class=DeleteProjectResponse,
    examples=examples["/todoist/delete_project"]
)
async def delete_project(
    params: Dict[str, Any] = Body(...),
    service: TodoistService = Depends(get_todoist_service)
):
    validated_params = DeleteProjectParams(**params)
    return service.delete_project(validated_params.project_id)

@router.post("/get_collaborators", response_model=ApiResponse)
@schema(
    input_schema_class=GetCollaboratorsParams,
    output_schema_class=GetCollaboratorsResponse,
    examples=examples["/todoist/get_collaborators"]
)
async def get_collaborators(
    params: Dict[str, Any] = Body(...),
    service: TodoistService = Depends(get_todoist_service)
):
    validated_params = GetCollaboratorsParams(**params)
    return service.get_collaborators(validated_params.project_id)

@router.post("/get_sections", response_model=ApiResponse)
@schema(
    input_schema_class=GetSectionsParams,
    output_schema_class=GetSectionsResponse,
    examples=examples["/todoist/get_sections"]
)
async def get_sections(
    params: Dict[str, Any] = Body(...),
    service: TodoistService = Depends(get_todoist_service)
):
    validated_params = GetSectionsParams(**params)
    return service.get_sections(validated_params)

@router.post("/get_section", response_model=ApiResponse)
@schema(
    input_schema_class=GetSectionParams,
    output_schema_class=GetSectionResponse,
    examples=examples["/todoist/get_section"]
)
async def get_section(
    params: Dict[str, Any] = Body(...),
    service: TodoistService = Depends(get_todoist_service)
):
    validated_params = GetSectionParams(**params)
    return service.get_section(validated_params.section_id)

@router.post("/create_section", response_model=ApiResponse)
@schema(
    input_schema_class=CreateSectionParams,
    output_schema_class=CreateSectionResponse,
    examples=examples["/todoist/create_section"]
)
async def create_section(
    params: Dict[str, Any] = Body(...),
    service: TodoistService = Depends(get_todoist_service)
):
    validated_params = CreateSectionParams(**params)
    return service.create_section(validated_params)

@router.post("/update_section", response_model=ApiResponse)
@schema(
    input_schema_class=UpdateSectionParams,
    output_schema_class=UpdateSectionResponse,
    examples=examples["/todoist/update_section"]
)
async def update_section(
    params: Dict[str, Any] = Body(...),
    service: TodoistService = Depends(get_todoist_service)
):
    validated_params = UpdateSectionParams(**params)
    return service.update_section(validated_params.section_id, validated_params)

@router.post("/delete_section", response_model=ApiResponse)
@schema(
    input_schema_class=DeleteSectionParams,
    output_schema_class=DeleteSectionResponse,
    examples=examples["/todoist/delete_section"]
)
async def delete_section(
    params: Dict[str, Any] = Body(...),
    service: TodoistService = Depends(get_todoist_service)
):
    validated_params = DeleteSectionParams(**params)
    return service.delete_section(validated_params.section_id)

@router.post("/get_tasks", response_model=ApiResponse)
@schema(
    input_schema_class=GetTasksParams,
    output_schema_class=GetTasksResponse,
    examples=examples["/todoist/get_tasks"]
)
async def get_tasks(
    params: Dict[str, Any] = Body(...),
    service: TodoistService = Depends(get_todoist_service)
):
    validated_params = GetTasksParams(**params)
    return service.get_tasks(validated_params)

@router.post("/get_task", response_model=ApiResponse)
@schema(
    input_schema_class=GetTaskParams,
    output_schema_class=GetTaskResponse,
    examples=examples["/todoist/get_task"]
)
async def get_task(
    params: Dict[str, Any] = Body(...),
    service: TodoistService = Depends(get_todoist_service)
):
    validated_params = GetTaskParams(**params)
    return service.get_task(validated_params.task_id)

@router.post("/create_task", response_model=ApiResponse)
@schema(
    input_schema_class=CreateTaskParams,
    output_schema_class=CreateTaskResponse,
    examples=examples["/todoist/create_task"]
)
async def create_task(
    params: Dict[str, Any] = Body(...),
    service: TodoistService = Depends(get_todoist_service)
):
    validated_params = CreateTaskParams(**params)
    return service.create_task(validated_params)

@router.post("/update_task", response_model=ApiResponse)
@schema(
    input_schema_class=UpdateTaskParams,
    output_schema_class=UpdateTaskResponse,
    examples=examples["/todoist/update_task"]
)
async def update_task(
    params: Dict[str, Any] = Body(...),
    service: TodoistService = Depends(get_todoist_service)
):
    validated_params = UpdateTaskParams(**params)
    return service.update_task(validated_params.task_id, validated_params)

@router.post("/close_task", response_model=ApiResponse)
@schema(
    input_schema_class=CloseTaskParams,
    output_schema_class=CloseTaskResponse,
    examples=examples["/todoist/close_task"]
)
async def close_task(
    params: Dict[str, Any] = Body(...),
    service: TodoistService = Depends(get_todoist_service)
):
    validated_params = CloseTaskParams(**params)
    return service.close_task(validated_params.task_id)

@router.post("/reopen_task", response_model=ApiResponse)
@schema(
    input_schema_class=ReopenTaskParams,
    output_schema_class=ReopenTaskResponse,
    examples=examples["/todoist/reopen_task"]
)
async def reopen_task(
    params: Dict[str, Any] = Body(...),
    service: TodoistService = Depends(get_todoist_service)
):
    validated_params = ReopenTaskParams(**params)
    return service.reopen_task(validated_params.task_id)

@router.post("/delete_task", response_model=ApiResponse)
@schema(
    input_schema_class=DeleteTaskParams,
    output_schema_class=DeleteTaskResponse,
    examples=examples["/todoist/delete_task"]
)
async def delete_task(
    params: Dict[str, Any] = Body(...),
    service: TodoistService = Depends(get_todoist_service)
):
    validated_params = DeleteTaskParams(**params)
    return service.delete_task(validated_params.task_id)

@router.post("/validate_key")
async def validate_key(
    params: Dict[str, Any] = Body(...),
):
    try:
        api_key = params.get("api_key")
        if not api_key:
            return {"valid": False, "message": "API key is required"}
        
        client = TodoistClient(api_key=api_key)
        client.get_projects()
        return {"valid": True, "message": "API key is valid"}
    except Exception as e:
        return {"valid": False, "message": f"Invalid API key: {str(e)}"}

@router.post("/get_comments", response_model=ApiResponse)
@schema(
    input_schema_class=GetCommentsParams,
    output_schema_class=GetCommentsResponse,
    examples=examples["/todoist/get_comments"]
)
async def get_comments(
    params: Dict[str, Any] = Body(...),
    service: TodoistService = Depends(get_todoist_service)
):
    validated_params = GetCommentsParams(**params)
    return service.get_comments(validated_params)

@router.post("/get_comment", response_model=ApiResponse)
@schema(
    input_schema_class=GetCommentParams,
    output_schema_class=GetCommentResponse,
    examples=examples["/todoist/get_comment"]
)
async def get_comment(
    params: Dict[str, Any] = Body(...),
    service: TodoistService = Depends(get_todoist_service)
):
    validated_params = GetCommentParams(**params)
    return service.get_comment(validated_params.comment_id)

@router.post("/create_comment", response_model=ApiResponse)
@schema(
    input_schema_class=CreateCommentParams,
    output_schema_class=CreateCommentResponse,
    examples=examples["/todoist/create_comment"]
)
async def create_comment(
    params: Dict[str, Any] = Body(...),
    service: TodoistService = Depends(get_todoist_service)
):
    validated_params = CreateCommentParams(**params)
    return service.create_comment(validated_params)

@router.post("/update_comment", response_model=ApiResponse)
@schema(
    input_schema_class=UpdateCommentParams,
    output_schema_class=UpdateCommentResponse,
    examples=examples["/todoist/update_comment"]
)
async def update_comment(
    params: Dict[str, Any] = Body(...),
    service: TodoistService = Depends(get_todoist_service)
):
    validated_params = UpdateCommentParams(**params)
    return service.update_comment(validated_params.comment_id, validated_params)

@router.post("/delete_comment", response_model=ApiResponse)
@schema(
    input_schema_class=DeleteCommentParams,
    output_schema_class=DeleteCommentResponse,
    examples=examples["/todoist/delete_comment"]
)
async def delete_comment(
    params: Dict[str, Any] = Body(...),
    service: TodoistService = Depends(get_todoist_service)
):
    validated_params = DeleteCommentParams(**params)
    return service.delete_comment(validated_params.comment_id)

@router.post("/get_personal_labels", response_model=ApiResponse)
@schema(
    input_schema_class=GetPersonalLabelsParams,
    output_schema_class=GetPersonalLabelsResponse,
    examples=examples["/todoist/get_personal_labels"]
)
async def get_personal_labels(
    params: Dict[str, Any] = Body(...),
    service: TodoistService = Depends(get_todoist_service)
):
    validated_params = GetPersonalLabelsParams(**params)
    return service.get_personal_labels(validated_params)

@router.post("/get_personal_label", response_model=ApiResponse)
@schema(
    input_schema_class=GetPersonalLabelParams,
    output_schema_class=GetPersonalLabelResponse,
    examples=examples["/todoist/get_personal_label"]
)
async def get_personal_label(
    params: Dict[str, Any] = Body(...),
    service: TodoistService = Depends(get_todoist_service)
):
    validated_params = GetPersonalLabelParams(**params)
    return service.get_personal_label(validated_params.label_id)

@router.post("/create_personal_label", response_model=ApiResponse)
@schema(
    input_schema_class=CreatePersonalLabelParams,
    output_schema_class=CreatePersonalLabelResponse,
    examples=examples["/todoist/create_personal_label"]
)
async def create_personal_label(
    params: Dict[str, Any] = Body(...),
    service: TodoistService = Depends(get_todoist_service)
):
    validated_params = CreatePersonalLabelParams(**params)
    return service.create_personal_label(validated_params)

@router.post("/update_personal_label", response_model=ApiResponse)
@schema(
    input_schema_class=UpdatePersonalLabelParams,
    output_schema_class=UpdatePersonalLabelResponse,
    examples=examples["/todoist/update_personal_label"]
)
async def update_personal_label(
    params: Dict[str, Any] = Body(...),
    service: TodoistService = Depends(get_todoist_service)
):
    validated_params = UpdatePersonalLabelParams(**params)
    return service.update_personal_label(validated_params.label_id, validated_params)

@router.post("/delete_personal_label", response_model=ApiResponse)
@schema(
    input_schema_class=DeletePersonalLabelParams,
    output_schema_class=DeletePersonalLabelResponse,
    examples=examples["/todoist/delete_personal_label"]
)
async def delete_personal_label(
    params: Dict[str, Any] = Body(...),
    service: TodoistService = Depends(get_todoist_service)
):
    validated_params = DeletePersonalLabelParams(**params)
    return service.delete_personal_label(validated_params.label_id)

@router.post("/get_shared_labels", response_model=ApiResponse)
@schema(
    input_schema_class=GetSharedLabelsParams,
    output_schema_class=GetSharedLabelsResponse,
    examples=examples["/todoist/get_shared_labels"]
)
async def get_shared_labels(
    params: Dict[str, Any] = Body(...),
    service: TodoistService = Depends(get_todoist_service)
):
    validated_params = GetSharedLabelsParams(**params)
    return service.get_shared_labels(validated_params)

@router.post("/rename_shared_label", response_model=ApiResponse)
@schema(
    input_schema_class=RenameSharedLabelParams,
    output_schema_class=RenameSharedLabelResponse,
    examples=examples["/todoist/rename_shared_label"]
)
async def rename_shared_label(
    params: Dict[str, Any] = Body(...),
    service: TodoistService = Depends(get_todoist_service)
):
    validated_params = RenameSharedLabelParams(**params)
    return service.rename_shared_label(validated_params.name, validated_params.new_name)

@router.post("/remove_shared_label", response_model=ApiResponse)
@schema(
    input_schema_class=RemoveSharedLabelParams,
    output_schema_class=RemoveSharedLabelResponse,
    examples=examples["/todoist/remove_shared_label"]
)
async def remove_shared_label(
    params: Dict[str, Any] = Body(...),
    service: TodoistService = Depends(get_todoist_service)
):
    validated_params = RemoveSharedLabelParams(**params)
    return service.remove_shared_label(validated_params.name)

apply_error_handler_to_router(router)
