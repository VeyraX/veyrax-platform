from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union, TypeVar, Generic

T = TypeVar('T')

# Common models
class WebhookEventsFilter(BaseModel):
    events: Optional[List[str]] = Field(
        default=None,
        description="Events that trigger webhook requests, can be one of: start, output, logs, completed"
    )

# Base parameter classes for routes
class PredictionParamsBase(BaseModel):
    id: str = Field(..., description="ID of the prediction")

class ModelParamsBase(BaseModel):
    owner: str = Field(..., description="Owner of the model")
    name: str = Field(..., description="Name of the model")

class ModelVersionParamsBase(BaseModel):
    owner: str = Field(..., description="Owner of the model")
    name: str = Field(..., description="Name of the model")
    version_id: str = Field(..., description="ID of the model version")

class DeploymentParamsBase(BaseModel):
    owner: str = Field(..., description="Owner of the deployment")
    name: str = Field(..., description="Name of the deployment")

class TrainingParamsBase(BaseModel):
    id: str = Field(..., description="ID of the training")

class CollectionParamsBase(BaseModel):
    slug: str = Field(..., description="Slug of the collection")

# Pagination
class PaginatedResponse(BaseModel, Generic[T]):
    next: Optional[str] = None
    previous: Optional[str] = None
    results: List[T]

# Account information
class AccountInfo(BaseModel):
    type: str = Field(description="Account type: user or organization")
    username: str
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    github_url: Optional[str] = None

# Hardware
class Hardware(BaseModel):
    name: str
    sku: str

# Prediction requests
class PredictionRequest(BaseModel):
    version: str = Field(description="The ID of the model version that you want to run")
    input: Dict[str, Any] = Field(description="The model's input as a JSON object")
    webhook: Optional[str] = Field(
        default=None,
        description="An HTTPS URL for receiving a webhook when the prediction has new output"
    )
    webhook_events_filter: Optional[List[str]] = Field(
        default=None,
        description="Which events trigger webhook requests. Valid values: start, output, logs, completed"
    )
    stream: Optional[bool] = Field(
        default=None,
        description="Request a URL to receive streaming output (deprecated, stream URL is always returned if supported)"
    )
    wait: Optional[int] = Field(
        default=None,
        description="Wait for the prediction to complete. Value is in seconds. Maximum 60 seconds."
    )

class DeploymentPredictionRequest(BaseModel):
    input: Dict[str, Any] = Field(description="The model's input as a JSON object")
    webhook: Optional[str] = Field(
        default=None,
        description="An HTTPS URL for receiving a webhook when the prediction has new output"
    )
    webhook_events_filter: Optional[List[str]] = Field(
        default=None,
        description="Which events trigger webhook requests. Valid values: start, output, logs, completed"
    )
    stream: Optional[bool] = Field(
        default=None,
        description="Request a URL to receive streaming output (deprecated, stream URL is always returned if supported)"
    )
    deployment_owner: str = Field(..., description="Owner of the deployment")
    deployment_name: str = Field(..., description="Name of the deployment")
    wait: Optional[int] = Field(
        default=None,
        description="Wait for the prediction to complete. Value is in seconds. Maximum 60 seconds."
    )

class OfficialModelPredictionRequest(BaseModel):
    input: Dict[str, Any] = Field(description="The model's input as a JSON object")
    webhook: Optional[str] = Field(
        default=None,
        description="An HTTPS URL for receiving a webhook when the prediction has new output"
    )
    webhook_events_filter: Optional[List[str]] = Field(
        default=None,
        description="Which events trigger webhook requests. Valid values: start, output, logs, completed"
    )
    stream: Optional[bool] = Field(
        default=None,
        description="Request a URL to receive streaming output (deprecated, stream URL is always returned if supported)"
    )
    model_owner: str = Field(..., description="Owner of the model")
    model_name: str = Field(..., description="Name of the model")
    wait: Optional[int] = Field(
        default=None,
        description="Wait for the prediction to complete. Value is in seconds. Maximum 60 seconds."
    )

class KlingModelPredictionRequest(OfficialModelPredictionRequest):
    class KlingInput(BaseModel):
        prompt: str = Field(description="Text prompt for image generation")
        duration: Optional[int] = Field(default=5, description="Duration in seconds, recommended 5-10")
        cfg_scale: Optional[float] = Field(default=0.5, description="Configuration scale parameter, recommended 0-1.0")
        start_image: Optional[str] = Field(default=None, description="URL to the starting image")
        end_image: Optional[str] = Field(default=None, description="URL to the ending image")
        aspect_ratio: Optional[str] = Field(default="16:9", description="Aspect ratio of the output, e.g. '16:9'")
        negative_prompt: Optional[str] = Field(default="", description="Negative prompt to guide what not to generate")
    
    input: KlingInput = Field(description="The Kling model's specific input parameters")
    
    model_owner: Optional[str] = Field(default="kwaivgi", description="Owner of the model")
    model_name: Optional[str] = Field(default="kling-v1.6-pro", description="Name of the model")

class FluxProModelPredictionRequest(OfficialModelPredictionRequest):
    class FluxProInput(BaseModel):
        prompt: str = Field(description="Text prompt for image generation")
        aspect_ratio: Optional[str] = Field(default="1:1", description="Aspect ratio of the output, e.g. '1:1'")
        output_format: Optional[str] = Field(default="webp", description="Output format for the image")
        output_quality: Optional[int] = Field(default=80, description="Output quality (1-100)")
        safety_tolerance: Optional[int] = Field(default=2, description="Safety tolerance level")
        prompt_upsampling: Optional[bool] = Field(default=True, description="Whether to upsample the prompt")
    
    input: FluxProInput = Field(description="The Flux 1.1 Pro model's specific input parameters")
    
    model_owner: Optional[str] = Field(default="black-forest-labs", description="Owner of the model")
    model_name: Optional[str] = Field(default="flux-1.1-pro", description="Name of the model")

class FluxSchnellModelPredictionRequest(OfficialModelPredictionRequest):
    class FluxSchnellInput(BaseModel):
        prompt: str = Field(description="Text prompt for image generation")
        go_fast: Optional[bool] = Field(default=True, description="Enable fast generation mode")
        num_outputs: Optional[int] = Field(default=1, description="Number of images to generate")
        aspect_ratio: Optional[str] = Field(default="1:1", description="Aspect ratio of the output, e.g. '1:1'")
        output_format: Optional[str] = Field(default="webp", description="Output format for the image")
        output_quality: Optional[int] = Field(default=80, description="Output quality (1-100)")
    
    input: FluxSchnellInput = Field(description="The Flux Schnell model's specific input parameters")
    
    model_owner: Optional[str] = Field(default="black-forest-labs", description="Owner of the model")
    model_name: Optional[str] = Field(default="flux-schnell", description="Name of the model")

class MinimaxVideoModelPredictionRequest(OfficialModelPredictionRequest):
    class MinimaxVideoInput(BaseModel):
        prompt: str = Field(description="Text prompt for video generation")
        prompt_optimizer: Optional[bool] = Field(default=True, description="Whether to optimize the prompt")
    
    input: MinimaxVideoInput = Field(description="The Minimax Video-01 model's specific input parameters")
    
    model_owner: Optional[str] = Field(default="minimax", description="Owner of the model")
    model_name: Optional[str] = Field(default="video-01", description="Name of the model")

# Direct version-based model requests
class StableDiffusionRequest(PredictionRequest):
    class StableDiffusionInput(BaseModel):
        prompt: str = Field(description="Text prompt for image generation")
        scheduler: Optional[str] = Field(default="K_EULER", description="Scheduler type")
        
    input: StableDiffusionInput = Field(description="Stable Diffusion input parameters")
    version: Optional[str] = Field(
        default="ac732df83cea7fff18b8472768c88ad041fa750ff7682a21affe81863cbe77e4",
        description="Stable Diffusion model version ID"
    )

class TrellisRequest(PredictionRequest):
    class TrellisInput(BaseModel):
        seed: Optional[int] = Field(default=0, description="Random seed")
        images: List[str] = Field(description="URLs of input images")
        texture_size: Optional[int] = Field(default=2048, description="Texture size")
        mesh_simplify: Optional[float] = Field(default=0.9, description="Mesh simplification factor (0-1)")
        generate_color: Optional[bool] = Field(default=True, description="Generate color texture")
        generate_model: Optional[bool] = Field(default=True, description="Generate 3D model")
        randomize_seed: Optional[bool] = Field(default=True, description="Randomize seed")
        generate_normal: Optional[bool] = Field(default=False, description="Generate normal map")
        save_gaussian_ply: Optional[bool] = Field(default=True, description="Save Gaussian PLY file")
        ss_sampling_steps: Optional[int] = Field(default=38, description="Sampling steps for single shot")
        slat_sampling_steps: Optional[int] = Field(default=12, description="Sampling steps for slats")
        return_no_background: Optional[bool] = Field(default=False, description="Return without background")
        ss_guidance_strength: Optional[float] = Field(default=7.5, description="Guidance strength for single shot")
        slat_guidance_strength: Optional[float] = Field(default=3, description="Guidance strength for slats")
        
    input: TrellisInput = Field(description="Trellis 3D model generation input parameters")
    version: Optional[str] = Field(
        default="4876f2a8da1c544772dffa32e8889da4a1bab3a1f5c1937bfcfccb99ae347251",
        description="Trellis model version ID"
    )

class RemoveBgRequest(PredictionRequest):
    class RemoveBgInput(BaseModel):
        image: str = Field(description="URL of image to remove background from")
        
    input: RemoveBgInput = Field(description="Remove background input parameters")
    version: Optional[str] = Field(
        default="95fcc2a26d3899cd6c2691c900465aaeff466285a65c14638cc5f36f34befaf1",
        description="Remove Background model version ID"
    )

class RealESRGANRequest(PredictionRequest):
    class RealESRGANInput(BaseModel):
        image: str = Field(description="URL of image to upscale")
        scale: Optional[int] = Field(default=2, description="Scale factor for upscaling (2-4)")
        
    input: RealESRGANInput = Field(description="Real-ESRGAN upscaling input parameters")
    version: Optional[str] = Field(
        default="f121d640bd286e1fdc67f9799164c1d5be36ff74576ee11c803ae5b665dd46aa",
        description="Real-ESRGAN model version ID"
    )

class LogoAIRequest(PredictionRequest):
    class LogoAIInput(BaseModel):
        prompt: str = Field(description="Text prompt describing the logo to generate")
        
    input: LogoAIInput = Field(description="LogoAI generation input parameters")
    version: str = Field(
        default="67ed00e8999fecd32035074fa0f2e9a31ee03b57a8415e6a5e2f93a242ddd8d2",
        description="LogoAI model version ID"
    )

class BirefNetRequest(PredictionRequest):
    class BirefNetInput(BaseModel):
        image: str = Field(description="URL of image to remove background from")
        resolution: Optional[str] = Field(default="", description="Resolution for output")
        
    input: BirefNetInput = Field(description="BirefNet background removal input parameters")
    version: str = Field(
        default="f74986db0355b58403ed20963af156525e2891ea3c2d499bfbfb2a28cd87c5d7",
        description="BirefNet model version ID"
    )

# Prediction listing query params
class PredictionListParams(BaseModel):
    created_after: Optional[str] = Field(
        default=None,
        description="Include only predictions created at or after this date-time, in ISO 8601 format"
    )
    created_before: Optional[str] = Field(
        default=None,
        description="Include only predictions created before this date-time, in ISO 8601 format"
    )

# Prediction response
class PredictionUrls(BaseModel):
    get: str = Field(description="Retrieve the latest state of the prediction")
    cancel: str = Field(description="Cancel the prediction")
    stream: Optional[str] = Field(
        default=None,
        description="An event source to stream the output of the prediction"
    )

class PredictionResponse(BaseModel):
    id: str
    model: str
    created_at: str
    input: Dict[str, Any]

    version: Optional[str] = Field(None, description="Model version ID. May be 'hidden' for official models")
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    status: str = Field(description="Status of the prediction. Valid values: starting, processing, succeeded, failed, canceled")
    output: Optional[Any] = None
    error: Optional[str] = None
    logs: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None
    urls: PredictionUrls
    data_removed: bool = False
    deployment: Optional[str] = None
    source: Optional[str] = Field(default=None, description="Source of the prediction. Valid values: web, api")
    component: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None

    class Config:
        extra = "allow"

class PredictionList(PaginatedResponse[PredictionResponse]):
    pass

# Training
class TrainingUrls(BaseModel):
    get: str
    cancel: str

class TrainingResponse(BaseModel):
    id: str
    model: str
    version: str
    input: Dict[str, Any]
    logs: Optional[str] = None
    error: Optional[str] = None
    output: Optional[Dict[str, Any]] = None
    status: str = Field(description="Status of the training. Valid values: starting, processing, succeeded, failed, canceled")
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None
    urls: TrainingUrls
    source: Optional[str] = Field(default=None, description="Source of the training. Valid values: web, api")

class TrainingList(PaginatedResponse[TrainingResponse]):
    pass

class TrainingRequest(BaseModel):
    destination: str = Field(
        description="A string representing the desired model to push to in the format `{destination_model_owner}/{destination_model_name}`"
    )
    input: Dict[str, Any] = Field(
        description="An object containing inputs to the Cog model's `train()` function"
    )
    webhook: Optional[str] = Field(
        default=None,
        description="An HTTPS URL for receiving a webhook when the training completes"
    )
    webhook_events_filter: Optional[List[str]] = Field(
        default=None,
        description="Which events trigger webhook requests. Valid values: start, output, logs, completed"
    )
    model_owner: str = Field(..., description="Owner of the model")
    model_name: str = Field(..., description="Name of the model")
    version_id: str = Field(..., description="ID of the model version to train")

# Models
class ModelVersion(BaseModel):
    id: str
    created_at: str
    cog_version: Optional[str] = None
    openapi_schema: Optional[Dict[str, Any]] = None

class ModelVersionList(PaginatedResponse[ModelVersion]):
    pass

class Model(BaseModel):
    url: str
    owner: str
    name: str
    description: Optional[str] = None
    visibility: str = Field(description="Model visibility. Valid values: public, private")
    github_url: Optional[str] = None
    paper_url: Optional[str] = None
    license_url: Optional[str] = None
    run_count: int
    cover_image_url: Optional[str] = None
    default_example: Optional[PredictionResponse] = None
    latest_version: Optional[ModelVersion] = None

class ModelList(PaginatedResponse[Model]):
    pass

class ModelCreationRequest(BaseModel):
    owner: str = Field(description="The name of the user or organization that will own the model")
    name: str = Field(description="The name of the model")
    visibility: str = Field(description="Whether the model should be public or private. Valid values: public, private")
    hardware: str = Field(description="The SKU for the hardware used to run the model")
    description: Optional[str] = Field(default=None, description="A description of the model")
    github_url: Optional[str] = Field(default=None, description="A URL for the model's source code on GitHub")
    paper_url: Optional[str] = Field(default=None, description="A URL for the model's paper")
    license_url: Optional[str] = Field(default=None, description="A URL for the model's license")
    cover_image_url: Optional[str] = Field(default=None, description="A URL for the model's cover image")

# Deployments
class DeploymentConfigurationResponse(BaseModel):
    hardware: str
    min_instances: int
    max_instances: int

class CreatedByInfo(BaseModel):
    type: str = Field(description="Account type: user or organization")
    username: str
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    github_url: Optional[str] = None

class DeploymentReleaseResponse(BaseModel):
    number: int
    model: str
    version: str
    created_at: str
    created_by: CreatedByInfo
    configuration: DeploymentConfigurationResponse

class DeploymentResponse(BaseModel):
    owner: str
    name: str
    current_release: DeploymentReleaseResponse

class DeploymentList(PaginatedResponse[DeploymentResponse]):
    pass

class DeploymentCreationRequest(BaseModel):
    name: str = Field(description="The name of the deployment")
    model: str = Field(description="The full name of the model that you want to deploy")
    version: str = Field(description="The 64-character string ID of the model version that you want to deploy")
    hardware: str = Field(description="The SKU for the hardware used to run the model")
    min_instances: int = Field(description="The minimum number of instances for scaling", ge=0, le=5)
    max_instances: int = Field(description="The maximum number of instances for scaling", ge=0, le=20)

class DeploymentUpdateRequest(BaseModel):
    owner: str = Field(..., description="Owner of the deployment")
    name: str = Field(..., description="Name of the deployment")
    hardware: Optional[str] = Field(default=None, description="The SKU for the hardware used to run the model")
    min_instances: Optional[int] = Field(default=None, description="The minimum number of instances for scaling", ge=0, le=5)
    max_instances: Optional[int] = Field(default=None, description="The maximum number of instances for scaling", ge=0, le=20)
    version: Optional[str] = Field(default=None, description="The ID of the model version that you want to deploy")

# Collections
class Collection(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None

class CollectionList(PaginatedResponse[Collection]):
    pass

class CollectionWithModels(Collection):
    models: List[Model]

# Webhooks
class WebhookSecret(BaseModel):
    key: str

# API responses
class ApiResponse(BaseModel):
    data: Union[
        PredictionResponse, 
        PredictionList,
        TrainingResponse,
        TrainingList,
        Model,
        ModelList,
        ModelVersion,
        ModelVersionList,
        Collection,
        CollectionList,
        CollectionWithModels,
        DeploymentResponse,
        DeploymentList,
        List[Hardware],
        WebhookSecret,
        str,  # For README content
        AccountInfo
    ]
    component: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None

# Response schema classes
class PredictionResponseSchema(BaseModel):
    data: PredictionResponse
    message: Optional[str] = None

class PredictionListSchema(BaseModel):
    data: PredictionList
    message: Optional[str] = None

class TrainingResponseSchema(BaseModel):
    data: TrainingResponse
    message: Optional[str] = None

class TrainingListSchema(BaseModel):
    data: TrainingList
    message: Optional[str] = None

class ModelResponseSchema(BaseModel):
    data: Model
    message: Optional[str] = None

class ModelListSchema(BaseModel):
    data: ModelList
    message: Optional[str] = None

class ModelVersionResponseSchema(BaseModel):
    data: ModelVersion
    message: Optional[str] = None

class ModelVersionListSchema(BaseModel):
    data: ModelVersionList
    message: Optional[str] = None

class DeploymentResponseSchema(BaseModel):
    data: DeploymentResponse
    message: Optional[str] = None

class DeploymentListSchema(BaseModel):
    data: DeploymentList
    message: Optional[str] = None

class HardwareListSchema(BaseModel):
    data: List[Hardware]
    message: Optional[str] = None

class WebhookSecretSchema(BaseModel):
    data: WebhookSecret
    message: Optional[str] = None

class CollectionResponseSchema(BaseModel):
    data: Collection
    message: Optional[str] = None

class CollectionListSchema(BaseModel):
    data: CollectionList
    message: Optional[str] = None

class CollectionWithModelsSchema(BaseModel):
    data: CollectionWithModels
    message: Optional[str] = None

class ReadmeResponseSchema(BaseModel):
    data: str
    message: Optional[str] = None

class AccountInfoSchema(BaseModel):
    data: AccountInfo
    message: Optional[str] = None

# Key validation
class ValidateKeyResponse(BaseModel):
    valid: bool
    message: str 