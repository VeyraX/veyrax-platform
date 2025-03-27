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
    input_schema_class=CheckAuthorizationParams,
    output_schema_class=CheckAuthorizationResponse,
    examples=examples["/bannerbear/check_authorization"]
)
async def check_authorization(
    params: Dict[str, Any] = Body(...),
    service: BannerbearService = Depends(get_bannerbear_service)
):
    validated_params = CheckAuthorizationParams(**params)
    r = service.check_authorization(validated_params)
    return CheckAuthorizationResponse(
        status_code=r.data.get("status_code", 200),
        message=r.data.get("message", "Authorized"),
        project=r.data.get("project")
    )


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
    r = service.retrieve_account_status(validated_params)
    return RetrieveAccountStatusResponse(
        status_code=r.data.get("status_code", 200),
        created_at=r.data.get("created_at"),
        uid=r.data.get("uid"),
        paid_plan_name=r.data.get("paid_plan_name"),
        api_usage=r.data.get("api_usage"),
        api_quota=r.data.get("api_quota"),
        current_project=r.data.get("current_project")
    )


@router.post("/create_image")
@schema(
    input_schema_class=CreateImageParams,
    output_schema_class=CreateImageResponse,  # or CreateImageResponse, if you prefer a specialized schema
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
    r = service.list_all_images(validated_params)
    return ListAllImagesResponse(
        status_code=r.data.get("status_code", 200),
        images=r.data.get("images", [])
    )


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
    r = service.create_video(validated_params)
    return CreateVideoResponse(**r.data)


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
    r = service.retrieve_video(validated_params)
    return RetrieveVideoResponse(
        status_code=r.data.get("status_code", 200),
        video=r.data.get("video", {})
    )


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
    r = service.update_video(validated_params)
    return UpdateVideoResponse(
        status_code=r.data.get("status_code", 200),
        video=r.data.get("video", {})
    )


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
    r = service.list_all_videos(validated_params)
    return ListAllVideosResponse(
        status_code=r.data.get("status_code", 200),
        videos=r.data.get("videos", [])
    )


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
    r = service.create_collection(validated_params)
    return CreateCollectionResponse(**r.data)


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
    r = service.retrieve_collection(validated_params)
    return RetrieveCollectionResponse(
        status_code=r.data.get("status_code", 200),
        collection=r.data.get("collection", {})
    )


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
    r = service.list_all_collections(validated_params)
    return ListAllCollectionsResponse(
        status_code=r.data.get("status_code", 200),
        collections=r.data.get("collections", [])
    )


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
    r = service.create_animated_gif(validated_params)
    return CreateAnimatedGifResponse(**r.data)


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
    r = service.retrieve_animated_gif(validated_params)
    return RetrieveAnimatedGifResponse(
        status_code=r.data.get("status_code", 200),
        animated_gif=r.data.get("animated_gif", {})
    )


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
    r = service.list_all_animated_gifs(validated_params)
    return ListAllAnimatedGifsResponse(
        status_code=r.data.get("status_code", 200),
        animated_gifs=r.data.get("animated_gifs", [])
    )


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
    r = service.create_screenshot(validated_params)
    return CreateScreenshotResponse(**r.data)


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
    r = service.retrieve_screenshot(validated_params)
    return RetrieveScreenshotResponse(
        status_code=r.data.get("status_code", 200),
        screenshot=r.data.get("screenshot", {})
    )


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
    r = service.list_all_screenshots(validated_params)
    return ListAllScreenshotsResponse(
        status_code=r.data.get("status_code", 200),
        screenshots=r.data.get("screenshots", [])
    )


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
    r = service.create_template(validated_params)
    return CreateTemplateResponse(**r.data)


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
    r = service.duplicate_template(validated_params)
    return DuplicateTemplateResponse(**r.data)


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
    r = service.retrieve_template(validated_params)
    return RetrieveTemplateResponse(
        status_code=r.data.get("status_code", 200),
        template=r.data.get("template", {})
    )


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
    r = service.update_template(validated_params)
    return UpdateTemplateResponse(
        status_code=r.data.get("status_code", 200),
        template=r.data.get("template", {})
    )


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
    r = service.list_all_templates(validated_params)
    return ListAllTemplatesResponse(
        status_code=r.data.get("status_code", 200),
        templates=r.data.get("templates", [])
    )


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
    r = service.import_templates(validated_params)
    return ImportTemplatesResponse(**r.data)


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
    r = service.create_template_set(validated_params)
    return CreateTemplateSetResponse(**r.data)


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
    r = service.update_template_set(validated_params)
    return UpdateTemplateSetResponse(
        status_code=r.data.get("status_code", 200),
        template_set=r.data.get("template_set", {})
    )


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
    r = service.retrieve_template_set(validated_params)
    return RetrieveTemplateSetResponse(
        status_code=r.data.get("status_code", 200),
        template_set=r.data.get("template_set", {})
    )


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
    r = service.list_all_template_sets(validated_params)
    return ListAllTemplateSetsResponse(
        status_code=r.data.get("status_code", 200),
        template_sets=r.data.get("template_sets", [])
    )


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
    r = service.create_video_template(validated_params)
    return CreateVideoTemplateResponse(**r.data)


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
    r = service.retrieve_video_template(validated_params)
    return RetrieveVideoTemplateResponse(
        status_code=r.data.get("status_code", 200),
        video_template=r.data.get("video_template", {})
    )


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
    r = service.list_all_video_templates(validated_params)
    return ListAllVideoTemplatesResponse(
        status_code=r.data.get("status_code", 200),
        video_templates=r.data.get("video_templates", [])
    )


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
    r = service.create_session(validated_params)
    return CreateSessionResponse(
        status_code=r.data.get("status_code", 200),
        session=r.data.get("session", {})
    )


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
    r = service.retrieve_session(validated_params)
    return RetrieveSessionResponse(
        status_code=r.data.get("status_code", 200),
        session=r.data.get("session", {})
    )


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
    r = service.list_all_sessions(validated_params)
    return ListAllSessionsResponse(
        status_code=r.data.get("status_code", 200),
        sessions=r.data.get("sessions", [])
    )


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
    r = service.create_webhook(validated_params)
    return CreateWebhookResponse(
        status_code=r.data.get("status_code", 200),
        webhook=r.data.get("webhook", {})
    )


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
    r = service.retrieve_webhook(validated_params)
    return RetrieveWebhookResponse(
        status_code=r.data.get("status_code", 200),
        webhook=r.data.get("webhook", {})
    )


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
    r = service.delete_webhook(validated_params)
    return DeleteWebhookResponse(
        status_code=r.data.get("status_code", 204),
        message="Webhook deleted"
    )


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
    r = service.create_movie(validated_params)
    return CreateMovieResponse(**r.data)


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
    r = service.retrieve_movie(validated_params)
    return RetrieveMovieResponse(
        status_code=r.data.get("status_code", 200),
        movie=r.data.get("movie", {})
    )


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
    r = service.list_all_movies(validated_params)
    return ListAllMoviesResponse(
        status_code=r.data.get("status_code", 200),
        movies=r.data.get("movies", [])
    )


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
    r = service.create_diagnosis(validated_params)
    return CreateDiagnosisResponse(**r.data)


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
    r = service.retrieve_diagnosis(validated_params)
    return RetrieveDiagnosisResponse(
        status_code=r.data.get("status_code", 200),
        diagnosis=r.data.get("diagnosis", {})
    )


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
    r = service.create_signed_base(validated_params)
    return CreateSignedBaseResponse(
        status_code=r.data.get("status_code", 200),
        signed_base=r.data.get("signed_base", {})
    )


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
    r = service.list_signed_bases(validated_params)
    return ListSignedBasesResponse(
        status_code=r.data.get("status_code", 200),
        signed_bases=r.data.get("signed_bases", [])
    )


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
    r = service.create_project(validated_params)
    return CreateProjectResponse(
        status_code=r.data.get("status_code", 200),
        project=r.data.get("project", {})
    )


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
    r = service.retrieve_project(validated_params)
    return RetrieveProjectResponse(
        status_code=r.data.get("status_code", 200),
        project=r.data.get("project", {})
    )


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
    r = service.hydrate_project(validated_params)
    return HydrateProjectResponse(**r.data)


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
    r = service.list_all_projects(validated_params)
    return ListAllProjectsResponse(
        status_code=r.data.get("status_code", 200),
        projects=r.data.get("projects", [])
    )


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
    r = service.list_fonts(validated_params)
    return FontsResponse(
        status_code=r.data.get("status_code", 200),
        fonts=r.data.get("fonts", {})
    )


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
    r = service.list_effects(validated_params)
    return EffectsResponse(
        status_code=r.data.get("status_code", 200),
        effects=r.data.get("effects", [])
    )


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
    r = service.join_pdf(validated_params)
    return JoinPdfResponse(**r.data)


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
    r = service.retrieve_joined_pdf(validated_params)
    return RetrieveJoinedPdfResponse(
        status_code=r.data.get("status_code", 200),
        joined_pdf=r.data.get("joined_pdf", {})
    )


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
    r = service.rasterize_pdf(validated_params)
    return RasterizePdfResponse(**r.data)


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
    r = service.retrieve_rasterized_pdf(validated_params)
    return RetrieveRasterizedPdfResponse(
        status_code=r.data.get("status_code", 200),
        rasterization=r.data.get("rasterization", {})
    )


apply_error_handler_to_router(router)
