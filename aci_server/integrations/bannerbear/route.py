from fastapi import APIRouter, Depends, Body, HTTPException
from starlette.requests import Request as FastAPIRequest
from typing import Any, Dict

from .client import BannerbearClient
from .service import BannerbearService
from ..common.utils import apply_error_handler_to_service, apply_error_handler_to_router
from ..common.input_schema_decorator import schema
from ..common.examples_handler import ExamplesLoader
from ..common.auth import validate_provider_api_key

from .schema import *


router = APIRouter(prefix="/bannerbear", tags=["bannerbear"])
examples = ExamplesLoader()


async def get_bannerbear_service(request: FastAPIRequest):
    try:
        # Example: retrieve API key from request/env
        api_key = await validate_provider_api_key(request, "bannerbear")
        if not api_key:
            raise HTTPException(status_code=401, detail="Missing Bannerbear API key")
        client = BannerbearClient(api_key)
        service = BannerbearService(client)
        apply_error_handler_to_service(service)
        return service
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Initialization failed: {str(e)}")


@router.post("/validate_key")
@schema(
    input_schema_class=CheckAuthorizationParams
)
async def validate_key(
    params: Dict[str, Any] = Body(...),
):
    try:
        api_key = params.get("api_key")
        if not api_key:
            return {"valid": False, "message": str(e)}
        
        client = BannerbearClient(api_key)
        response = client.list_all_images({})
        return {"valid": True, "message": "API key is valid"}
    except Exception as e:
        return {"valid": False, "message": str(e)}


@router.post("/retrieve_account_status")
@schema(
    input_schema_class=RetrieveAccountStatusParams,
    output_schema_class=RetrieveAccountStatusResponse,
    examples=examples["/bannerbear/retrieve_account_status"]
)
async def retrieve_account_status(
    params: Dict[str, Any] = Body(...),
    service: BannerbearService = Depends(get_bannerbear_service)
):
    validated_params = RetrieveAccountStatusParams(**params)
    return service.retrieve_account_status(validated_params)


@router.post("/create_image")
@schema(
    input_schema_class=CreateImageParams,
    output_schema_class=CreateImageResponse,
    examples=examples["/bannerbear/create_image"]
)
async def create_image(
    params: Dict[str, Any] = Body(...),
    service: BannerbearService = Depends(get_bannerbear_service)
):
    validated_params = CreateImageParams(**params)
    return service.create_image(validated_params)


@router.post("/retrieve_image")
@schema(
    input_schema_class=RetrieveImageParams,
    output_schema_class=RetrieveImageResponse,
    examples=examples["/bannerbear/retrieve_image"]
)
async def retrieve_image(
    params: Dict[str, Any] = Body(...),
    service: BannerbearService = Depends(get_bannerbear_service)
):
    validated_params = RetrieveImageParams(**params)
    return service.retrieve_image(validated_params)


@router.post("/list_all_images")
@schema(
    input_schema_class=ListAllImagesParams,
    output_schema_class=ListAllImagesResponse,
    examples=examples["/bannerbear/list_all_images"]
)
async def list_all_images(
    params: Dict[str, Any] = Body(...),
    service: BannerbearService = Depends(get_bannerbear_service)
):
    validated_params = ListAllImagesParams(**params)
    return service.list_all_images(validated_params)


@router.post("/create_video")
@schema(
    input_schema_class=CreateVideoParams,
    output_schema_class=CreateVideoResponse,
    examples=examples["/bannerbear/create_video"]
)
async def create_video(
    params: Dict[str, Any] = Body(...),
    service: BannerbearService = Depends(get_bannerbear_service)
):
    validated_params = CreateVideoParams(**params)
    return service.create_video(validated_params)


@router.post("/retrieve_video")
@schema(
    input_schema_class=RetrieveVideoParams,
    output_schema_class=RetrieveVideoResponse,
    examples=examples["/bannerbear/retrieve_video"]
)
async def retrieve_video(
    params: Dict[str, Any] = Body(...),
    service: BannerbearService = Depends(get_bannerbear_service)
):
    validated_params = RetrieveVideoParams(**params)
    return service.retrieve_video(validated_params)


@router.post("/update_video")
@schema(
    input_schema_class=UpdateVideoParams,
    output_schema_class=UpdateVideoResponse,
    examples=examples["/bannerbear/update_video"]
)
async def update_video(
    params: Dict[str, Any] = Body(...),
    service: BannerbearService = Depends(get_bannerbear_service)
):
    validated_params = UpdateVideoParams(**params)
    return service.update_video(validated_params)


@router.post("/list_all_videos")
@schema(
    input_schema_class=ListAllVideosParams,
    output_schema_class=ListAllVideosResponse,
    examples=examples["/bannerbear/list_all_videos"]
)
async def list_all_videos(
    params: Dict[str, Any] = Body(...),
    service: BannerbearService = Depends(get_bannerbear_service)
):
    validated_params = ListAllVideosParams(**params)
    return service.list_all_videos(validated_params)


@router.post("/create_collection")
@schema(
    input_schema_class=CreateCollectionParams,
    output_schema_class=CreateCollectionResponse,
    examples=examples["/bannerbear/create_collection"]
)
async def create_collection(
    params: Dict[str, Any] = Body(...),
    service: BannerbearService = Depends(get_bannerbear_service)
):
    validated_params = CreateCollectionParams(**params)
    return service.create_collection(validated_params)


@router.post("/retrieve_collection")
@schema(
    input_schema_class=RetrieveCollectionParams,
    output_schema_class=RetrieveCollectionResponse,
    examples=examples["/bannerbear/retrieve_collection"]
)
async def retrieve_collection(
    params: Dict[str, Any] = Body(...),
    service: BannerbearService = Depends(get_bannerbear_service)
):
    validated_params = RetrieveCollectionParams(**params)
    return service.retrieve_collection(validated_params)


@router.post("/list_all_collections")
@schema(
    input_schema_class=ListAllCollectionsParams,
    output_schema_class=ListAllCollectionsResponse,
    examples=examples["/bannerbear/list_all_collections"]
)
async def list_all_collections(
    params: Dict[str, Any] = Body(...),
    service: BannerbearService = Depends(get_bannerbear_service)
):
    validated_params = ListAllCollectionsParams(**params)
    return service.list_all_collections(validated_params)


@router.post("/create_animated_gif")
@schema(
    input_schema_class=CreateAnimatedGifParams,
    output_schema_class=CreateAnimatedGifResponse,
    examples=examples["/bannerbear/create_animated_gif"]
)
async def create_animated_gif(
    params: Dict[str, Any] = Body(...),
    service: BannerbearService = Depends(get_bannerbear_service)
):
    validated_params = CreateAnimatedGifParams(**params)
    return service.create_animated_gif(validated_params)


@router.post("/retrieve_animated_gif")
@schema(
    input_schema_class=RetrieveAnimatedGifParams,
    output_schema_class=RetrieveAnimatedGifResponse,
    examples=examples["/bannerbear/retrieve_animated_gif"]
)
async def retrieve_animated_gif(
    params: Dict[str, Any] = Body(...),
    service: BannerbearService = Depends(get_bannerbear_service)
):
    validated_params = RetrieveAnimatedGifParams(**params)
    return service.retrieve_animated_gif(validated_params)


@router.post("/list_all_animated_gifs")
@schema(
    input_schema_class=ListAllAnimatedGifsParams,
    output_schema_class=ListAllAnimatedGifsResponse,
    examples=examples["/bannerbear/list_all_animated_gifs"]
)
async def list_all_animated_gifs(
    params: Dict[str, Any] = Body(...),
    service: BannerbearService = Depends(get_bannerbear_service)
):
    validated_params = ListAllAnimatedGifsParams(**params)
    return service.list_all_animated_gifs(validated_params)


@router.post("/create_screenshot")
@schema(
    input_schema_class=CreateScreenshotParams,
    output_schema_class=CreateScreenshotResponse,
    examples=examples["/bannerbear/create_screenshot"]
)
async def create_screenshot(
    params: Dict[str, Any] = Body(...),
    service: BannerbearService = Depends(get_bannerbear_service)
):
    validated_params = CreateScreenshotParams(**params)
    return service.create_screenshot(validated_params)


@router.post("/retrieve_screenshot")
@schema(
    input_schema_class=RetrieveScreenshotParams,
    output_schema_class=RetrieveScreenshotResponse,
    examples=examples["/bannerbear/retrieve_screenshot"]
)
async def retrieve_screenshot(
    params: Dict[str, Any] = Body(...),
    service: BannerbearService = Depends(get_bannerbear_service)
):
    validated_params = RetrieveScreenshotParams(**params)
    return service.retrieve_screenshot(validated_params)


@router.post("/list_all_screenshots")
@schema(
    input_schema_class=ListAllScreenshotsParams,
    output_schema_class=ListAllScreenshotsResponse,
    examples=examples["/bannerbear/list_all_screenshots"]
)
async def list_all_screenshots(
    params: Dict[str, Any] = Body(...),
    service: BannerbearService = Depends(get_bannerbear_service)
):
    validated_params = ListAllScreenshotsParams(**params)
    return service.list_all_screenshots(validated_params)


@router.post("/create_template")
@schema(
    input_schema_class=CreateTemplateParams,
    output_schema_class=CreateTemplateResponse,
    examples=examples["/bannerbear/create_template"]
)
async def create_template(
    params: Dict[str, Any] = Body(...),
    service: BannerbearService = Depends(get_bannerbear_service)
):
    validated_params = CreateTemplateParams(**params)
    return service.create_template(validated_params)


@router.post("/duplicate_template")
@schema(
    input_schema_class=DuplicateTemplateParams,
    output_schema_class=DuplicateTemplateResponse,
    examples=examples["/bannerbear/duplicate_template"]
)
async def duplicate_template(
    params: Dict[str, Any] = Body(...),
    service: BannerbearService = Depends(get_bannerbear_service)
):
    validated_params = DuplicateTemplateParams(**params)
    return service.duplicate_template(validated_params)


@router.post("/retrieve_template")
@schema(
    input_schema_class=RetrieveTemplateParams,
    output_schema_class=RetrieveTemplateResponse,
    examples=examples["/bannerbear/retrieve_template"]
)
async def retrieve_template(
    params: Dict[str, Any] = Body(...),
    service: BannerbearService = Depends(get_bannerbear_service)
):
    validated_params = RetrieveTemplateParams(**params)
    return service.retrieve_template(validated_params)


@router.post("/update_template")
@schema(
    input_schema_class=UpdateTemplateParams,
    output_schema_class=UpdateTemplateResponse,
    examples=examples["/bannerbear/update_template"]
)
async def update_template(
    params: Dict[str, Any] = Body(...),
    service: BannerbearService = Depends(get_bannerbear_service)
):
    validated_params = UpdateTemplateParams(**params)
    return service.update_template(validated_params)


@router.post("/list_all_templates")
@schema(
    input_schema_class=ListAllTemplatesParams,
    output_schema_class=ListAllTemplatesResponse,
    examples=examples["/bannerbear/list_all_templates"]
)
async def list_all_templates(
    params: Dict[str, Any] = Body(...),
    service: BannerbearService = Depends(get_bannerbear_service)
):
    validated_params = ListAllTemplatesParams(**params)
    return service.list_all_templates(validated_params)


@router.post("/import_templates")
@schema(
    input_schema_class=ImportTemplatesParams,
    output_schema_class=ImportTemplatesResponse,
    examples=examples["/bannerbear/import_templates"]
)
async def import_templates(
    params: Dict[str, Any] = Body(...),
    service: BannerbearService = Depends(get_bannerbear_service)
):
    validated_params = ImportTemplatesParams(**params)
    return service.import_templates(validated_params)


@router.post("/create_template_set")
@schema(
    input_schema_class=CreateTemplateSetParams,
    output_schema_class=CreateTemplateSetResponse,
    examples=examples["/bannerbear/create_template_set"]
)
async def create_template_set(
    params: Dict[str, Any] = Body(...),
    service: BannerbearService = Depends(get_bannerbear_service)
):
    validated_params = CreateTemplateSetParams(**params)
    return service.create_template_set(validated_params)


@router.post("/update_template_set")
@schema(
    input_schema_class=UpdateTemplateSetParams,
    output_schema_class=UpdateTemplateSetResponse,
    examples=examples["/bannerbear/update_template_set"]
)
async def update_template_set(
    params: Dict[str, Any] = Body(...),
    service: BannerbearService = Depends(get_bannerbear_service)
):
    validated_params = UpdateTemplateSetParams(**params)
    return service.update_template_set(validated_params)


@router.post("/retrieve_template_set")
@schema(
    input_schema_class=RetrieveTemplateSetParams,
    output_schema_class=RetrieveTemplateSetResponse,
    examples=examples["/bannerbear/retrieve_template_set"]
)
async def retrieve_template_set(
    params: Dict[str, Any] = Body(...),
    service: BannerbearService = Depends(get_bannerbear_service)
):
    validated_params = RetrieveTemplateSetParams(**params)
    return service.retrieve_template_set(validated_params)


@router.post("/list_all_template_sets")
@schema(
    input_schema_class=ListAllTemplateSetsParams,
    output_schema_class=ListAllTemplateSetsResponse,
    examples=examples["/bannerbear/list_all_template_sets"]
)
async def list_all_template_sets(
    params: Dict[str, Any] = Body(...),
    service: BannerbearService = Depends(get_bannerbear_service)
):
    validated_params = ListAllTemplateSetsParams(**params)
    return service.list_all_template_sets(validated_params)


@router.post("/create_video_template")
@schema(
    input_schema_class=CreateVideoTemplateParams,
    output_schema_class=CreateVideoTemplateResponse,
    examples=examples["/bannerbear/create_video_template"]
)
async def create_video_template(
    params: Dict[str, Any] = Body(...),
    service: BannerbearService = Depends(get_bannerbear_service)
):
    validated_params = CreateVideoTemplateParams(**params)
    return service.create_video_template(validated_params)


@router.post("/retrieve_video_template")
@schema(
    input_schema_class=RetrieveVideoTemplateParams,
    output_schema_class=RetrieveVideoTemplateResponse,
    examples=examples["/bannerbear/retrieve_video_template"]
)
async def retrieve_video_template(
    params: Dict[str, Any] = Body(...),
    service: BannerbearService = Depends(get_bannerbear_service)
):
    validated_params = RetrieveVideoTemplateParams(**params)
    return service.retrieve_video_template(validated_params)


@router.post("/list_all_video_templates")
@schema(
    input_schema_class=ListAllVideoTemplatesParams,
    output_schema_class=ListAllVideoTemplatesResponse,
    examples=examples["/bannerbear/list_all_video_templates"]
)
async def list_all_video_templates(
    params: Dict[str, Any] = Body(...),
    service: BannerbearService = Depends(get_bannerbear_service)
):
    validated_params = ListAllVideoTemplatesParams(**params)
    return service.list_all_video_templates(validated_params)


@router.post("/create_session")
@schema(
    input_schema_class=CreateSessionParams,
    output_schema_class=CreateSessionResponse,
    examples=examples["/bannerbear/create_session"]
)
async def create_session(
    params: Dict[str, Any] = Body(...),
    service: BannerbearService = Depends(get_bannerbear_service)
):
    validated_params = CreateSessionParams(**params)
    return service.create_session(validated_params)


@router.post("/retrieve_session")
@schema(
    input_schema_class=RetrieveSessionParams,
    output_schema_class=RetrieveSessionResponse,
    examples=examples["/bannerbear/retrieve_session"]
)
async def retrieve_session(
    params: Dict[str, Any] = Body(...),
    service: BannerbearService = Depends(get_bannerbear_service)
):
    validated_params = RetrieveSessionParams(**params)
    return service.retrieve_session(validated_params)


@router.post("/list_all_sessions")
@schema(
    input_schema_class=ListAllSessionsParams,
    output_schema_class=ListAllSessionsResponse,
    examples=examples["/bannerbear/list_all_sessions"]
)
async def list_all_sessions(
    params: Dict[str, Any] = Body(...),
    service: BannerbearService = Depends(get_bannerbear_service)
):
    validated_params = ListAllSessionsParams(**params)
    return service.list_all_sessions(validated_params)


@router.post("/create_webhook")
@schema(
    input_schema_class=CreateWebhookParams,
    output_schema_class=CreateWebhookResponse,
    examples=examples["/bannerbear/create_webhook"]
)
async def create_webhook(
    params: Dict[str, Any] = Body(...),
    service: BannerbearService = Depends(get_bannerbear_service)
):
    validated_params = CreateWebhookParams(**params)
    return service.create_webhook(validated_params)


@router.post("/retrieve_webhook")
@schema(
    input_schema_class=RetrieveWebhookParams,
    output_schema_class=RetrieveWebhookResponse,
    examples=examples["/bannerbear/retrieve_webhook"]
)
async def retrieve_webhook(
    params: Dict[str, Any] = Body(...),
    service: BannerbearService = Depends(get_bannerbear_service)
):
    validated_params = RetrieveWebhookParams(**params)
    return service.retrieve_webhook(validated_params)


@router.post("/delete_webhook")
@schema(
    input_schema_class=DeleteWebhookParams,
    output_schema_class=DeleteWebhookResponse,
    examples=examples["/bannerbear/delete_webhook"]
)
async def delete_webhook(
    params: Dict[str, Any] = Body(...),
    service: BannerbearService = Depends(get_bannerbear_service)
):
    validated_params = DeleteWebhookParams(**params)
    return service.delete_webhook(validated_params)


@router.post("/create_movie")
@schema(
    input_schema_class=CreateMovieParams,
    output_schema_class=CreateMovieResponse,
    examples=examples["/bannerbear/create_movie"]
)
async def create_movie(
    params: Dict[str, Any] = Body(...),
    service: BannerbearService = Depends(get_bannerbear_service)
):
    validated_params = CreateMovieParams(**params)
    return service.create_movie(validated_params)


@router.post("/retrieve_movie")
@schema(
    input_schema_class=RetrieveMovieParams,
    output_schema_class=RetrieveMovieResponse,
    examples=examples["/bannerbear/retrieve_movie"]
)
async def retrieve_movie(
    params: Dict[str, Any] = Body(...),
    service: BannerbearService = Depends(get_bannerbear_service)
):
    validated_params = RetrieveMovieParams(**params)
    return service.retrieve_movie(validated_params)


@router.post("/list_all_movies")
@schema(
    input_schema_class=ListAllMoviesParams,
    output_schema_class=ListAllMoviesResponse,
    examples=examples["/bannerbear/list_all_movies"]
)
async def list_all_movies(
    params: Dict[str, Any] = Body(...),
    service: BannerbearService = Depends(get_bannerbear_service)
):
    validated_params = ListAllMoviesParams(**params)
    return service.list_all_movies(validated_params)


@router.post("/create_diagnosis")
@schema(
    input_schema_class=CreateDiagnosisParams,
    output_schema_class=CreateDiagnosisResponse,
    examples=examples["/bannerbear/create_diagnosis"]
)
async def create_diagnosis(
    params: Dict[str, Any] = Body(...),
    service: BannerbearService = Depends(get_bannerbear_service)
):
    validated_params = CreateDiagnosisParams(**params)
    return service.create_diagnosis(validated_params)


@router.post("/retrieve_diagnosis")
@schema(
    input_schema_class=RetrieveDiagnosisParams,
    output_schema_class=RetrieveDiagnosisResponse,
    examples=examples["/bannerbear/retrieve_diagnosis"]
)
async def retrieve_diagnosis(
    params: Dict[str, Any] = Body(...),
    service: BannerbearService = Depends(get_bannerbear_service)
):
    validated_params = RetrieveDiagnosisParams(**params)
    return service.retrieve_diagnosis(validated_params)


@router.post("/create_signed_base")
@schema(
    input_schema_class=CreateSignedBaseParams,
    output_schema_class=CreateSignedBaseResponse,
    examples=examples["/bannerbear/create_signed_base"]
)
async def create_signed_base(
    params: Dict[str, Any] = Body(...),
    service: BannerbearService = Depends(get_bannerbear_service)
):
    validated_params = CreateSignedBaseParams(**params)
    return service.create_signed_base(validated_params)


@router.post("/list_signed_bases")
@schema(
    input_schema_class=ListSignedBasesParams,
    output_schema_class=ListSignedBasesResponse,
    examples=examples["/bannerbear/list_signed_bases"]
)
async def list_signed_bases(
    params: Dict[str, Any] = Body(...),
    service: BannerbearService = Depends(get_bannerbear_service)
):
    validated_params = ListSignedBasesParams(**params)
    return service.list_signed_bases(validated_params)


@router.post("/create_project")
@schema(
    input_schema_class=CreateProjectParams,
    output_schema_class=CreateProjectResponse,
    examples=examples["/bannerbear/create_project"]
)
async def create_project(
    params: Dict[str, Any] = Body(...),
    service: BannerbearService = Depends(get_bannerbear_service)
):
    validated_params = CreateProjectParams(**params)
    return service.create_project(validated_params)


@router.post("/retrieve_project")
@schema(
    input_schema_class=RetrieveProjectParams,
    output_schema_class=RetrieveProjectResponse,
    examples=examples["/bannerbear/retrieve_project"]
)
async def retrieve_project(
    params: Dict[str, Any] = Body(...),
    service: BannerbearService = Depends(get_bannerbear_service)
):
    validated_params = RetrieveProjectParams(**params)
    return service.retrieve_project(validated_params)


@router.post("/hydrate_project")
@schema(
    input_schema_class=HydrateProjectParams,
    output_schema_class=HydrateProjectResponse,
    examples=examples["/bannerbear/hydrate_project"]
)
async def hydrate_project(
    params: Dict[str, Any] = Body(...),
    service: BannerbearService = Depends(get_bannerbear_service)
):
    validated_params = HydrateProjectParams(**params)
    return service.hydrate_project(validated_params)


@router.post("/list_all_projects")
@schema(
    input_schema_class=ListAllProjectsParams,
    output_schema_class=ListAllProjectsResponse,
    examples=examples["/bannerbear/list_all_projects"]
)
async def list_all_projects(
    params: Dict[str, Any] = Body(...),
    service: BannerbearService = Depends(get_bannerbear_service)
):
    validated_params = ListAllProjectsParams(**params)
    return service.list_all_projects(validated_params)


@router.post("/list_fonts")
@schema(
    input_schema_class=ListFontsParams,
    output_schema_class=FontsResponse,
    examples=examples["/bannerbear/list_fonts"]
)
async def list_fonts(
    params: Dict[str, Any] = Body(...),
    service: BannerbearService = Depends(get_bannerbear_service)
):
    validated_params = ListFontsParams(**params)
    return service.list_fonts(validated_params)

@router.post("/list_effects")
@schema(
    input_schema_class=ListEffectsParams,
    output_schema_class=EffectsResponse,
    examples=examples["/bannerbear/list_effects"]
)
async def list_effects(
    params: Dict[str, Any] = Body(...),
    service: BannerbearService = Depends(get_bannerbear_service)
):
    validated_params = ListEffectsParams(**params)
    return service.list_effects(validated_params)


@router.post("/join_pdf")
@schema(
    input_schema_class=JoinPdfParams,
    output_schema_class=JoinPdfResponse,
    examples=examples["/bannerbear/join_pdf"]
)
async def join_pdf(
    params: Dict[str, Any] = Body(...),
    service: BannerbearService = Depends(get_bannerbear_service)
):
    validated_params = JoinPdfParams(**params)
    return service.join_pdf(validated_params)


@router.post("/retrieve_joined_pdf")
@schema(
    input_schema_class=RetrieveJoinedPdfParams,
    output_schema_class=RetrieveJoinedPdfResponse,
    examples=examples["/bannerbear/retrieve_joined_pdf"]
)
async def retrieve_joined_pdf(
    params: Dict[str, Any] = Body(...),
    service: BannerbearService = Depends(get_bannerbear_service)
):
    validated_params = RetrieveJoinedPdfParams(**params)
    return service.retrieve_joined_pdf(validated_params)


@router.post("/rasterize_pdf")
@schema(
    input_schema_class=RasterizePdfParams,
    output_schema_class=RasterizePdfResponse,
    examples=examples["/bannerbear/rasterize_pdf"]
)
async def rasterize_pdf(
    params: Dict[str, Any] = Body(...),
    service: BannerbearService = Depends(get_bannerbear_service)
):
    validated_params = RasterizePdfParams(**params)
    return service.rasterize_pdf(validated_params)


@router.post("/retrieve_rasterized_pdf")
@schema(
    input_schema_class=RetrieveRasterizedPdfParams,
    output_schema_class=RetrieveRasterizedPdfResponse,
    examples=examples["/bannerbear/retrieve_rasterized_pdf"]
)
async def retrieve_rasterized_pdf(
    params: Dict[str, Any] = Body(...),
    service: BannerbearService = Depends(get_bannerbear_service)
):
    validated_params = RetrieveRasterizedPdfParams(**params)
    return service.retrieve_rasterized_pdf(validated_params)


apply_error_handler_to_router(router)
