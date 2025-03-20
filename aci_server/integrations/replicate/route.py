from fastapi import APIRouter, Depends, HTTPException, Request, Body
from typing import Dict, Any
from .schema import (
    PredictionRequest, 
    DeploymentPredictionRequest, 
    OfficialModelPredictionRequest,
    KlingModelPredictionRequest,
    FluxProModelPredictionRequest,
    FluxSchnellModelPredictionRequest,
    MinimaxVideoModelPredictionRequest,
    StableDiffusionRequest,
    TrellisRequest,
    RemoveBgRequest,
    RealESRGANRequest,
    LogoAIRequest,
    BirefNetRequest,
    PredictionListParams,
    DeploymentCreationRequest,
    DeploymentUpdateRequest,
    DeploymentParamsBase,
    TrainingRequest,
    ModelCreationRequest,
    ModelParamsBase,
    TrainingParamsBase,
    ApiResponse, 
    PredictionResponseSchema,
    PredictionListSchema,
    PredictionParamsBase,
    TrainingResponseSchema,
    TrainingListSchema,
    ModelResponseSchema,
    ModelListSchema,
    ModelVersionResponseSchema,
    ModelVersionListSchema,
    ModelVersionParamsBase,
    DeploymentResponseSchema,
    DeploymentListSchema,
    CollectionResponseSchema,
    CollectionListSchema,
    CollectionParamsBase,
    ReadmeResponseSchema,
    AccountInfoSchema,
    ValidateKeyResponse
)
from .service import ReplicateService
from .client import ReplicateClient
from ..common.auth import validate_provider_api_key
from ..common.input_schema_decorator import schema
from ..common.utils import apply_error_handler_to_service, apply_error_handler_to_router, apply_error_handler_to_client
from ..common.examples_handler import ExamplesLoader

router = APIRouter(prefix="/replicate", tags=["replicate"])

examples = ExamplesLoader() 

async def get_replicate_service(request: Request):
    api_key = await validate_provider_api_key(request, "replicate")
    client = ReplicateClient(api_key)
    apply_error_handler_to_client(client)
    service = ReplicateService(client)
    apply_error_handler_to_service(service)
    return service

# ---------- Account ----------
@router.post("/get_account", response_model=ApiResponse)
@schema(output_schema_class=AccountInfoSchema, examples=examples["/replicate/get_account"])
async def get_account(
    params: Dict[str, Any] = Body(...),
    service: ReplicateService = Depends(get_replicate_service)
):
    return service.get_account_info()

# ---------- Predictions ----------
@router.post("/create_prediction_by_version_id", response_model=ApiResponse)
@schema(input_schema_class=PredictionRequest, output_schema_class=PredictionResponseSchema, examples=examples["/replicate/create_prediction_by_version_id"])
async def create_prediction(
    params: Dict[str, Any] = Body(...),
    service: ReplicateService = Depends(get_replicate_service)
):
    validated_params = PredictionRequest(**params)
    return service.create_prediction(validated_params)

@router.post("/list_predictions", response_model=ApiResponse)
@schema(input_schema_class=PredictionListParams, output_schema_class=PredictionListSchema, examples=examples["/replicate/list_predictions"])
async def list_predictions(
    params: Dict[str, Any] = Body(...),
    service: ReplicateService = Depends(get_replicate_service)
):
    validated_params = PredictionListParams(**params)
    return service.list_predictions(validated_params.created_after, validated_params.created_before)

@router.post("/get_prediction", response_model=ApiResponse)
@schema(input_schema_class=PredictionParamsBase, output_schema_class=PredictionResponseSchema, examples=examples["/replicate/get_prediction"])
async def get_prediction(
    params: Dict[str, Any] = Body(...),
    service: ReplicateService = Depends(get_replicate_service)
):
    validated_params = PredictionParamsBase(**params)
    return service.get_prediction(validated_params.id)

@router.post("/cancel_prediction", response_model=ApiResponse)
@schema(input_schema_class=PredictionParamsBase, output_schema_class=PredictionResponseSchema, examples=examples["/replicate/cancel_prediction"])
async def cancel_prediction(
    params: Dict[str, Any] = Body(...),
    service: ReplicateService = Depends(get_replicate_service)
):
    validated_params = PredictionParamsBase(**params)
    return service.cancel_prediction(validated_params.id)

# ---------- Deployments ----------
@router.post("/create_deployment_prediction", response_model=ApiResponse)
@schema(input_schema_class=DeploymentPredictionRequest, output_schema_class=PredictionResponseSchema, examples=examples["/replicate/create_deployment_prediction"])
async def create_deployment_prediction(
    params: Dict[str, Any] = Body(...),
    service: ReplicateService = Depends(get_replicate_service)
):
    validated_params = DeploymentPredictionRequest(**params)
    deployment_owner = params.get("deployment_owner")
    deployment_name = params.get("deployment_name")
    wait = params.get("wait")
    
    return service.create_deployment_prediction(
        deployment_owner=deployment_owner, 
        deployment_name=deployment_name, 
        request=validated_params,
        wait=wait
    )

@router.post("/list_deployments", response_model=ApiResponse)
@schema(output_schema_class=DeploymentListSchema, examples=examples["/replicate/list_deployments"])
async def list_deployments(
    params: Dict[str, Any] = Body(...),
    service: ReplicateService = Depends(get_replicate_service)
):
    return service.list_deployments()

@router.post("/get_deployment", response_model=ApiResponse)
@schema(input_schema_class=DeploymentParamsBase, output_schema_class=DeploymentResponseSchema, examples=examples["/replicate/get_deployment"])
async def get_deployment(
    params: Dict[str, Any] = Body(...),
    service: ReplicateService = Depends(get_replicate_service)
):
    validated_params = DeploymentParamsBase(**params)
    return service.get_deployment(validated_params.owner, validated_params.name)

@router.post("/create_deployment", response_model=ApiResponse)
@schema(input_schema_class=DeploymentCreationRequest, output_schema_class=DeploymentResponseSchema, examples=examples["/replicate/create_deployment"])
async def create_deployment(
    params: Dict[str, Any] = Body(...),
    service: ReplicateService = Depends(get_replicate_service)
):
    validated_params = DeploymentCreationRequest(**params)
    return service.create_deployment(validated_params)

@router.post("/update_deployment", response_model=ApiResponse)
@schema(input_schema_class=DeploymentUpdateRequest, output_schema_class=DeploymentResponseSchema, examples=examples["/replicate/update_deployment"])
async def update_deployment(
    params: Dict[str, Any] = Body(...),
    service: ReplicateService = Depends(get_replicate_service)
):
    validated_params = DeploymentUpdateRequest(**params)
    deployment_owner = params.get("owner")
    deployment_name = params.get("name")
    
    return service.update_deployment(
        deployment_owner=deployment_owner,
        deployment_name=deployment_name,
        request=validated_params
    )

@router.post("/delete_deployment", response_model=ApiResponse)
@schema(input_schema_class=DeploymentParamsBase, output_schema_class=DeploymentResponseSchema, examples=examples["/replicate/delete_deployment"])
async def delete_deployment(
    params: Dict[str, Any] = Body(...),
    service: ReplicateService = Depends(get_replicate_service)
):
    validated_params = DeploymentParamsBase(**params)
    return service.delete_deployment(validated_params.owner, validated_params.name)

# ---------- Models ----------
@router.post("/create_prediction_by_model_name", response_model=ApiResponse)
@schema(input_schema_class=OfficialModelPredictionRequest, output_schema_class=PredictionResponseSchema, examples=examples["/replicate/create_prediction_by_model_name"])
async def create_model_prediction(
    params: Dict[str, Any] = Body(...),
    service: ReplicateService = Depends(get_replicate_service)
):
    validated_params = OfficialModelPredictionRequest(**params)
    model_owner = params.get("model_owner")
    model_name = params.get("model_name")
    
    return service.create_official_model_prediction(
        model_owner=model_owner, 
        model_name=model_name, 
        request=validated_params
    )

@router.post("/list_models", response_model=ApiResponse)
@schema(output_schema_class=ModelListSchema, examples=examples["/replicate/list_models"])
async def list_models(
    params: Dict[str, Any] = Body(...),
    service: ReplicateService = Depends(get_replicate_service)
):
    return service.list_models()

@router.post("/create_model", response_model=ApiResponse)
@schema(input_schema_class=ModelCreationRequest, output_schema_class=ModelResponseSchema, examples=examples["/replicate/create_model"])
async def create_model(
    params: Dict[str, Any] = Body(...),
    service: ReplicateService = Depends(get_replicate_service)
):
    validated_params = ModelCreationRequest(**params)
    return service.create_model(validated_params)

@router.post("/get_model", response_model=ApiResponse)
@schema(input_schema_class=ModelParamsBase, output_schema_class=ModelResponseSchema, examples=examples["/replicate/get_model"])
async def get_model(
    params: Dict[str, Any] = Body(...),
    service: ReplicateService = Depends(get_replicate_service)
):
    validated_params = ModelParamsBase(**params)
    return service.get_model(validated_params.owner, validated_params.name)

@router.post("/delete_model", response_model=ApiResponse)
@schema(input_schema_class=ModelParamsBase, output_schema_class=ModelResponseSchema, examples=examples["/replicate/delete_model"])
async def delete_model(
    params: Dict[str, Any] = Body(...),
    service: ReplicateService = Depends(get_replicate_service)
):
    validated_params = ModelParamsBase(**params)
    return service.delete_model(validated_params.owner, validated_params.name)

@router.post("/search_models", response_model=ApiResponse)
@schema(input_schema_class=dict(query=str), output_schema_class=ModelListSchema, examples=examples["/replicate/search_models"])
async def search_models(
    params: Dict[str, Any] = Body(...),
    service: ReplicateService = Depends(get_replicate_service)
):
    query = params.get("query")
    return service.search_models(query)

@router.post("/list_model_examples", response_model=ApiResponse)
@schema(input_schema_class=ModelParamsBase, output_schema_class=PredictionListSchema, examples=examples["/replicate/list_model_examples"])
async def list_model_examples(
    params: Dict[str, Any] = Body(...),
    service: ReplicateService = Depends(get_replicate_service)
):
    validated_params = ModelParamsBase(**params)
    return service.list_model_examples(validated_params.owner, validated_params.name)

@router.post("/get_model_readme", response_model=ApiResponse)
@schema(input_schema_class=ModelParamsBase, output_schema_class=ReadmeResponseSchema, examples=examples["/replicate/get_model_readme"])
async def get_model_readme(
    params: Dict[str, Any] = Body(...),
    service: ReplicateService = Depends(get_replicate_service)
):
    validated_params = ModelParamsBase(**params)
    return service.get_model_readme(validated_params.owner, validated_params.name)

# ---------- Model versions ----------
@router.post("/list_model_versions", response_model=ApiResponse)
@schema(input_schema_class=ModelParamsBase, output_schema_class=ModelVersionListSchema, examples=examples["/replicate/list_model_versions"])
async def list_model_versions(
    params: Dict[str, Any] = Body(...),
    service: ReplicateService = Depends(get_replicate_service)
):
    validated_params = ModelParamsBase(**params)
    return service.list_model_versions(validated_params.owner, validated_params.name)

@router.post("/get_model_version", response_model=ApiResponse)
@schema(input_schema_class=ModelVersionParamsBase, output_schema_class=ModelVersionResponseSchema, examples=examples["/replicate/get_model_version"])
async def get_model_version(
    params: Dict[str, Any] = Body(...),
    service: ReplicateService = Depends(get_replicate_service)
):
    validated_params = ModelVersionParamsBase(**params)
    return service.get_model_version(validated_params.owner, validated_params.name, validated_params.version_id)

@router.post("/delete_model_version", response_model=ApiResponse)
@schema(input_schema_class=ModelVersionParamsBase, output_schema_class=ModelVersionResponseSchema, examples=examples["/replicate/delete_model_version"])
async def delete_model_version(
    params: Dict[str, Any] = Body(...),
    service: ReplicateService = Depends(get_replicate_service)
):
    validated_params = ModelVersionParamsBase(**params)
    return service.delete_model_version(validated_params.owner, validated_params.name, validated_params.version_id)

# ---------- Trainings ----------
@router.post("/create_training", response_model=ApiResponse)
@schema(input_schema_class=TrainingRequest, output_schema_class=TrainingResponseSchema, examples=examples["/replicate/create_training"])
async def create_training(
    params: Dict[str, Any] = Body(...),
    service: ReplicateService = Depends(get_replicate_service)
):
    validated_params = TrainingRequest(**params)
    model_owner = params.get("model_owner")
    model_name = params.get("model_name")
    version_id = params.get("version_id")
    
    return service.create_training(
        model_owner=model_owner,
        model_name=model_name,
        version_id=version_id,
        request=validated_params
    )

@router.post("/list_trainings", response_model=ApiResponse)
@schema(output_schema_class=TrainingListSchema, examples=examples["/replicate/list_trainings"])
async def list_trainings(
    params: Dict[str, Any] = Body(...),
    service: ReplicateService = Depends(get_replicate_service)
):
    return service.list_trainings()

@router.post("/get_training", response_model=ApiResponse)
@schema(input_schema_class=TrainingParamsBase, output_schema_class=TrainingResponseSchema, examples=examples["/replicate/get_training"])
async def get_training(
    params: Dict[str, Any] = Body(...),
    service: ReplicateService = Depends(get_replicate_service)
):
    validated_params = TrainingParamsBase(**params)
    return service.get_training(validated_params.id)

@router.post("/cancel_training", response_model=ApiResponse)
@schema(input_schema_class=TrainingParamsBase, output_schema_class=TrainingResponseSchema, examples=examples["/replicate/cancel_training"])
async def cancel_training(
    params: Dict[str, Any] = Body(...),
    service: ReplicateService = Depends(get_replicate_service)
):
    validated_params = TrainingParamsBase(**params)
    return service.cancel_training(validated_params.id)

# ---------- Collections ----------
@router.post("/list_collections", response_model=ApiResponse)
@schema(output_schema_class=CollectionListSchema, examples=examples["/replicate/list_collections"])
async def list_collections(
    params: Dict[str, Any] = Body(...),
    service: ReplicateService = Depends(get_replicate_service)
):
    return service.list_collections()

@router.post("/get_collection", response_model=ApiResponse)
@schema(input_schema_class=CollectionParamsBase, output_schema_class=CollectionResponseSchema, examples=examples["/replicate/get_collection"])
async def get_collection(
    params: Dict[str, Any] = Body(...),
    service: ReplicateService = Depends(get_replicate_service)
):
    validated_params = CollectionParamsBase(**params)
    return service.get_collection(validated_params.slug)

# ---------- Hardware ----------
@router.post("/list_hardware", response_model=ApiResponse)
@schema(output_schema_class=ModelListSchema, examples=examples["/replicate/list_hardware"])
async def list_hardware(
    params: Dict[str, Any] = Body(...),
    service: ReplicateService = Depends(get_replicate_service)
):
    return service.list_hardware()

# ---------- Webhooks ----------
@router.post("/get_webhook_secret", response_model=ApiResponse)
@schema(output_schema_class=ModelListSchema, examples=examples["/replicate/get_webhook_secret"])
async def get_webhook_secret(
    params: Dict[str, Any] = Body(...),
    service: ReplicateService = Depends(get_replicate_service)
):
    return service.get_webhook_secret()

# ---------- Key validation ----------
@router.post("/validate_key", response_model=ValidateKeyResponse)
async def validate_key(
    params: Dict[str, Any] = Body(...),
):
    try:
        api_key = params.get("api_key")
        if not api_key:
            return {"valid": False, "message": "API key is required"}
        
        client = ReplicateClient(api_key=api_key)
        # Use a simple prediction request to validate the API key
        # Just create a client but don't actually run a prediction
        return {"valid": True, "message": "API key is valid"}
    except Exception as e:
        return {"valid": False, "message": f"Invalid API key: {str(e)}"}



### WORKFLOWS


@router.post("/create_kling_prediction", response_model=ApiResponse)
@schema(input_schema_class=KlingModelPredictionRequest, output_schema_class=PredictionResponseSchema, examples=examples["/replicate/create_kling_prediction"])
async def create_kling_prediction(
    params: Dict[str, Any] = Body(...),
    service: ReplicateService = Depends(get_replicate_service)
):
    validated_params = KlingModelPredictionRequest(**params)
    
    return service.create_official_model_prediction(
        model_owner="kwaivgi", 
        model_name="kling-v1.6-pro", 
        request=validated_params
    )

@router.post("/create_flux_pro_prediction", response_model=ApiResponse)
@schema(input_schema_class=FluxProModelPredictionRequest, output_schema_class=PredictionResponseSchema, examples=examples["/replicate/create_flux_pro_prediction"])
async def create_flux_pro_prediction(
    params: Dict[str, Any] = Body(...),
    service: ReplicateService = Depends(get_replicate_service)
):
    validated_params = FluxProModelPredictionRequest(**params)
    
    return service.create_official_model_prediction(
        model_owner="black-forest-labs", 
        model_name="flux-1.1-pro", 
        request=validated_params
    )

@router.post("/create_flux_schnell_prediction", response_model=ApiResponse)
@schema(input_schema_class=FluxSchnellModelPredictionRequest, output_schema_class=PredictionResponseSchema, examples=examples["/replicate/create_flux_schnell_prediction"])
async def create_flux_schnell_prediction(
    params: Dict[str, Any] = Body(...),
    service: ReplicateService = Depends(get_replicate_service)
):
    validated_params = FluxSchnellModelPredictionRequest(**params)
    
    return service.create_official_model_prediction(
        model_owner="black-forest-labs", 
        model_name="flux-schnell", 
        request=validated_params
    )

@router.post("/create_minimax_video_prediction", response_model=ApiResponse)
@schema(input_schema_class=MinimaxVideoModelPredictionRequest, output_schema_class=PredictionResponseSchema, examples=examples["/replicate/create_minimax_video_prediction"])
async def create_minimax_video_prediction(
    params: Dict[str, Any] = Body(...),
    service: ReplicateService = Depends(get_replicate_service)
):
    validated_params = MinimaxVideoModelPredictionRequest(**params)
    
    return service.create_official_model_prediction(
        model_owner="minimax", 
        model_name="video-01", 
        request=validated_params
    )

# Version-based model routes
@router.post("/create_stable_diffusion_prediction", response_model=ApiResponse)
@schema(input_schema_class=StableDiffusionRequest, output_schema_class=PredictionResponseSchema, examples=examples["/replicate/create_stable_diffusion_prediction"])
async def create_stable_diffusion_prediction(
    params: Dict[str, Any] = Body(...),
    service: ReplicateService = Depends(get_replicate_service)
):
    validated_params = StableDiffusionRequest(**params)
    return service.create_prediction(validated_params)

@router.post("/create_trellis_prediction", response_model=ApiResponse)
@schema(input_schema_class=TrellisRequest, output_schema_class=PredictionResponseSchema, examples=examples["/replicate/create_trellis_prediction"])
async def create_trellis_prediction(
    params: Dict[str, Any] = Body(...),
    service: ReplicateService = Depends(get_replicate_service)
):
    validated_params = TrellisRequest(**params)
    return service.create_prediction(validated_params)

@router.post("/create_remove_bg_prediction", response_model=ApiResponse)
@schema(input_schema_class=RemoveBgRequest, output_schema_class=PredictionResponseSchema, examples=examples["/replicate/create_remove_bg_prediction"])
async def create_remove_bg_prediction(
    params: Dict[str, Any] = Body(...),
    service: ReplicateService = Depends(get_replicate_service)
):
    validated_params = RemoveBgRequest(**params)
    return service.create_prediction(validated_params)

@router.post("/create_real_esrgan_prediction", response_model=ApiResponse)
@schema(input_schema_class=RealESRGANRequest, output_schema_class=PredictionResponseSchema, examples=examples["/replicate/create_real_esrgan_prediction"])
async def create_real_esrgan_prediction(
    params: Dict[str, Any] = Body(...),
    service: ReplicateService = Depends(get_replicate_service)
):
    validated_params = RealESRGANRequest(**params)
    return service.create_prediction(validated_params)

@router.post("/create_logo_ai_prediction", response_model=ApiResponse)
@schema(input_schema_class=LogoAIRequest, output_schema_class=PredictionResponseSchema, examples=examples["/replicate/create_logo_ai_prediction"])
async def create_logo_ai_prediction(
    params: Dict[str, Any] = Body(...),
    service: ReplicateService = Depends(get_replicate_service)
):
    validated_params = LogoAIRequest(**params)
    return service.create_prediction(validated_params)

@router.post("/create_birefnet_prediction", response_model=ApiResponse)
@schema(input_schema_class=BirefNetRequest, output_schema_class=PredictionResponseSchema, examples=examples["/replicate/create_birefnet_prediction"])
async def create_birefnet_prediction(
    params: Dict[str, Any] = Body(...),
    service: ReplicateService = Depends(get_replicate_service)
):
    validated_params = BirefNetRequest(**params)
    return service.create_prediction(validated_params)

# User-friendly abstracted routes
@router.post("/generate_image", response_model=ApiResponse)
@schema(input_schema_class=FluxProModelPredictionRequest, output_schema_class=PredictionResponseSchema, examples=examples["/replicate/create_flux_pro_prediction"])
async def generate_image(
    params: Dict[str, Any] = Body(...),
    service: ReplicateService = Depends(get_replicate_service)
):
    """Generate a high-quality image using Flux 1.1 Pro model."""
    validated_params = FluxProModelPredictionRequest(**params)
    
    return service.create_official_model_prediction(
        model_owner="black-forest-labs", 
        model_name="flux-1.1-pro", 
        request=validated_params
    )

@router.post("/generate_video", response_model=ApiResponse)
@schema(input_schema_class=MinimaxVideoModelPredictionRequest, output_schema_class=PredictionResponseSchema, examples=examples["/replicate/create_minimax_video_prediction"])
async def generate_video(
    params: Dict[str, Any] = Body(...),
    service: ReplicateService = Depends(get_replicate_service)
):
    """Generate a video from a text prompt using Minimax Video-01 model."""
    validated_params = MinimaxVideoModelPredictionRequest(**params)
    
    return service.create_official_model_prediction(
        model_owner="minimax", 
        model_name="video-01", 
        request=validated_params
    )

@router.post("/generate_3d_asset", response_model=ApiResponse)
@schema(input_schema_class=TrellisRequest, output_schema_class=PredictionResponseSchema, examples=examples["/replicate/create_trellis_prediction"])
async def generate_3d_asset(
    params: Dict[str, Any] = Body(...),
    service: ReplicateService = Depends(get_replicate_service)
):
    """Generate a 3D model from images using Trellis model."""
    validated_params = TrellisRequest(**params)
    return service.create_prediction(validated_params)

@router.post("/remove_background_best_model", response_model=ApiResponse)
@schema(input_schema_class=BirefNetRequest, output_schema_class=PredictionResponseSchema, examples=examples["/replicate/create_birefnet_prediction"])
async def remove_background_best_model(
    params: Dict[str, Any] = Body(...),
    service: ReplicateService = Depends(get_replicate_service)
):
    """Remove the background from an image using BirefNet model (best quality)."""
    validated_params = BirefNetRequest(**params)
    return service.create_prediction(validated_params)

apply_error_handler_to_router(router) 


