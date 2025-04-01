from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union

# Common Parameters
class BaseParams(BaseModel):
    pass

# Models Related Parameters
class ModelsParams(BaseParams):
    page: Optional[int] = Field(
        None,
        description="The page number of models to retrieve"
    )
    total: Optional[int] = Field(
        None,
        description="The total number of models to retrieve per page"
    )
    max_results: Optional[int] = Field(
        30,
        description="The maximum number of models to return in total"
    )

class SearchModelParams(BaseParams):
    keywords: str = Field(
        ...,
        description="The search terms to find models"
    )

class SchemaModelParams(BaseParams):
    model_id: str = Field(
        ...,
        description="The ID of the model (e.g., 'fal-ai/flux/dev')"
    )

# Generation Related Parameters
class GenerateParams(BaseParams):
    model: str = Field(
        ...,
        description="The model ID to use (e.g., 'fal-ai/flux/dev')"
    )
    parameters: Dict[str, Any] = Field(
        ...,
        description="Model-specific parameters as a dictionary"
    )
    queue: Optional[bool] = Field(
        False,
        description="Whether to use the queuing system"
    )

class ResultParams(BaseParams):
    url: str = Field(
        ...,
        description="The response_url from a queued request"
    )

class StatusParams(BaseParams):
    url: str = Field(
        ...,
        description="The status_url from a queued request"
    )

class CancelParams(BaseParams):
    url: str = Field(
        ...,
        description="The cancel_url from a queued request"
    )

# Storage Related Parameters
class UploadParams(BaseParams):
    path: str = Field(
        ...,
        description="The absolute path to the file to upload"
    )

# Response Models
class Model(BaseModel):
    id: str
    name: Optional[str] = None
    description: Optional[str] = None
    owner: Optional[str] = None
    created_at: Optional[str] = None
    visibility: Optional[str] = None
    tags: Optional[List[str]] = None

class ModelList(BaseModel):
    models: List[Model]

class UploadResult(BaseModel):
    file_url: str
    file_name: str
    file_size: int
    content_type: str

class GenerationResult(BaseModel):
    status: Optional[str] = None
    completed: Optional[bool] = None
    result: Optional[Dict[str, Any]] = None
    status_url: Optional[str] = None
    response_url: Optional[str] = None
    cancel_url: Optional[str] = None

class SchemaInfo(BaseModel):
    openapi: str
    info: Dict[str, Any]
    paths: Dict[str, Any]
    components: Optional[Dict[str, Any]] = None

# Output Schema Models
class ModelsResponse(BaseModel):
    data: ModelList

class SchemaResponse(BaseModel):
    data: SchemaInfo

class GenerateResponse(BaseModel):
    data: GenerationResult

class ResultResponse(BaseModel):
    data: GenerationResult

class StatusResponse(BaseModel):
    data: GenerationResult

class CancelResponse(BaseModel):
    data: GenerationResult

class UploadResponse(BaseModel):
    data: UploadResult

# API Response (Union of all possible response types)
class ApiResponse(BaseModel):
    data: Union[ModelList, GenerationResult, SchemaInfo, UploadResult]
    component: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None
