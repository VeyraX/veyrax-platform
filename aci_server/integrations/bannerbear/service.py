from typing import Any, Dict
from .client import BannerbearClient
from .schema import ApiResponse, CreateImageParams
from ..common.component_handler import load_components, prepare_components_auto
from .schema import *

class BannerbearService:
    def __init__(self, client: BannerbearClient):
        self.client = client


    def prepare_response(self, data: Any, component_name: str = None) -> ApiResponse:
        """Prepare standardized API response with optional UI components"""
        tool_name = "bannerbear"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name) if component_name else None
        return ApiResponse(data=data, component=components)
    

    def create_image(self, params: CreateImageParams) -> ApiResponse:
        """Create an image and format response"""
        processed_params = params.dict(exclude_unset=True)
        response = self.client.create_image(processed_params)
        
        # Return response directly without additional mapping
        return self.prepare_response(response, None)

    def retrieve_image(self, params: RetrieveImageParams) -> ApiResponse:
        """Retrieve an image and format response"""
        response = self.client.retrieve_image(params.uid)
        
        # Return response directly without additional mapping
        return self.prepare_response(response, None)

    def check_authorization(self, params: CheckAuthorizationParams) -> ApiResponse:
        """Check authorization (no real params needed, but we keep typed signature)."""
        # If needed: processed_params = params.dict(exclude_unset=True)
        response = self.client.check_authorization()
        return self.prepare_response(response)

    def retrieve_account_status(self, params: RetrieveAccountStatusParams) -> ApiResponse:
        """Retrieve account status."""
        # processed_params = params.dict(exclude_unset=True)
        response = self.client.retrieve_account_status()
        return self.prepare_response(response)


    def list_all_images(self, params: ListAllImagesParams) -> ApiResponse:
        """List all images."""
        processed_params = params.dict(exclude_unset=True)
        response = self.client.list_all_images(processed_params)
        return self.prepare_response(response)

    def create_video(self, params: CreateVideoParams) -> ApiResponse:
        """Create a video."""
        processed_params = params.dict(exclude_unset=True)
        response = self.client.create_video(processed_params)
        return self.prepare_response(response)

    def retrieve_video(self, params: RetrieveVideoParams) -> ApiResponse:
        """Retrieve a video."""
        processed_params = params.dict(exclude_unset=True)
        response = self.client.retrieve_video(processed_params["uid"])
        return self.prepare_response(response)

    def update_video(self, params: UpdateVideoParams) -> ApiResponse:
        """Update a video."""
        processed_params = params.dict(exclude_unset=True)
        response = self.client.update_video(processed_params)
        return self.prepare_response(response)

    def list_all_videos(self, params: ListAllVideosParams) -> ApiResponse:
        """List all videos."""
        processed_params = params.dict(exclude_unset=True)
        response = self.client.list_all_videos(processed_params)
        return self.prepare_response(response)

    def create_collection(self, params: CreateCollectionParams) -> ApiResponse:
        """Create a collection."""
        processed_params = params.dict(exclude_unset=True)
        response = self.client.create_collection(processed_params)
        return self.prepare_response(response)

    def retrieve_collection(self, params: RetrieveCollectionParams) -> ApiResponse:
        """Retrieve a collection."""
        processed_params = params.dict(exclude_unset=True)
        response = self.client.retrieve_collection(processed_params["uid"])
        return self.prepare_response(response)

    def list_all_collections(self, params: ListAllCollectionsParams) -> ApiResponse:
        """List all collections."""
        processed_params = params.dict(exclude_unset=True)
        response = self.client.list_all_collections(processed_params)
        return self.prepare_response(response)

    def create_animated_gif(self, params: CreateAnimatedGifParams) -> ApiResponse:
        """Create an animated GIF."""
        processed_params = params.dict(exclude_unset=True)
        response = self.client.create_animated_gif(processed_params)
        return self.prepare_response(response)

    def retrieve_animated_gif(self, params: RetrieveAnimatedGifParams) -> ApiResponse:
        """Retrieve an animated GIF."""
        processed_params = params.dict(exclude_unset=True)
        response = self.client.retrieve_animated_gif(processed_params["uid"])
        return self.prepare_response(response)

    def list_all_animated_gifs(self, params: ListAllAnimatedGifsParams) -> ApiResponse:
        """List all animated GIFs."""
        processed_params = params.dict(exclude_unset=True)
        response = self.client.list_all_animated_gifs(processed_params)
        return self.prepare_response(response)

    def create_screenshot(self, params: CreateScreenshotParams) -> ApiResponse:
        """Create a screenshot."""
        processed_params = params.dict(exclude_unset=True)
        response = self.client.create_screenshot(processed_params)
        return self.prepare_response(response)

    def retrieve_screenshot(self, params: RetrieveScreenshotParams) -> ApiResponse:
        """Retrieve a screenshot."""
        processed_params = params.dict(exclude_unset=True)
        response = self.client.retrieve_screenshot(processed_params["uid"])
        return self.prepare_response(response)

    def list_all_screenshots(self, params: ListAllScreenshotsParams) -> ApiResponse:
        """List all screenshots."""
        processed_params = params.dict(exclude_unset=True)
        response = self.client.list_all_screenshots(processed_params)
        return self.prepare_response(response)

    def create_template(self, params: CreateTemplateParams) -> ApiResponse:
        """Create a template."""
        processed_params = params.dict(exclude_unset=True)
        response = self.client.create_template(processed_params)
        return self.prepare_response(response)

    def duplicate_template(self, params: DuplicateTemplateParams) -> ApiResponse:
        """Duplicate a template."""
        processed_params = params.dict(exclude_unset=True)
        source_uid = processed_params["source_uid"]
        response = self.client.duplicate_template(source_uid)
        return self.prepare_response(response)

    def retrieve_template(self, params: RetrieveTemplateParams) -> ApiResponse:
        """Retrieve a template."""
        processed_params = params.dict(exclude_unset=True)
        response = self.client.retrieve_template(processed_params["uid"])
        return self.prepare_response(response)

    def update_template(self, params: UpdateTemplateParams) -> ApiResponse:
        """Update a template."""
        processed_params = params.dict(exclude_unset=True)
        uid = processed_params.pop("uid", None)  # remove uid from dict
        response = self.client.update_template(uid, processed_params)
        return self.prepare_response(response)

    def list_all_templates(self, params: ListAllTemplatesParams) -> ApiResponse:
        """List all templates."""
        processed_params = params.dict(exclude_unset=True)
        response = self.client.list_all_templates(processed_params)
        return self.prepare_response(response)

    def import_templates(self, params: ImportTemplatesParams) -> ApiResponse:
        """Import templates."""
        processed_params = params.dict(exclude_unset=True)
        response = self.client.import_templates(processed_params)
        return self.prepare_response(response)

    def create_template_set(self, params: CreateTemplateSetParams) -> ApiResponse:
        """Create a template set."""
        processed_params = params.dict(exclude_unset=True)
        response = self.client.create_template_set(processed_params)
        return self.prepare_response(response)

    def update_template_set(self, params: UpdateTemplateSetParams) -> ApiResponse:
        """Update a template set."""
        processed_params = params.dict(exclude_unset=True)
        uid = processed_params.pop("uid", None)
        response = self.client.update_template_set(uid, processed_params)
        return self.prepare_response(response)

    def retrieve_template_set(self, params: RetrieveTemplateSetParams) -> ApiResponse:
        """Retrieve a template set."""
        processed_params = params.dict(exclude_unset=True)
        response = self.client.retrieve_template_set(processed_params["uid"])
        return self.prepare_response(response)

    def list_all_template_sets(self, params: ListAllTemplateSetsParams) -> ApiResponse:
        """List all template sets."""
        processed_params = params.dict(exclude_unset=True)
        response = self.client.list_all_template_sets(processed_params)
        return self.prepare_response(response)

    def create_video_template(self, params: CreateVideoTemplateParams) -> ApiResponse:
        """Create a video template."""
        processed_params = params.dict(exclude_unset=True)
        response = self.client.create_video_template(processed_params)
        return self.prepare_response(response)

    def retrieve_video_template(self, params: RetrieveVideoTemplateParams) -> ApiResponse:
        """Retrieve a video template."""
        processed_params = params.dict(exclude_unset=True)
        response = self.client.retrieve_video_template(processed_params["uid"])
        return self.prepare_response(response)

    def list_all_video_templates(self, params: ListAllVideoTemplatesParams) -> ApiResponse:
        """List all video templates."""
        processed_params = params.dict(exclude_unset=True)
        response = self.client.list_all_video_templates(processed_params)
        return self.prepare_response(response)

    def create_session(self, params: CreateSessionParams) -> ApiResponse:
        """Create a session."""
        processed_params = params.dict(exclude_unset=True)
        response = self.client.create_session(processed_params)
        return self.prepare_response(response)

    def retrieve_session(self, params: RetrieveSessionParams) -> ApiResponse:
        """Retrieve a session."""
        processed_params = params.dict(exclude_unset=True)
        response = self.client.retrieve_session(processed_params["uid"])
        return self.prepare_response(response)

    def list_all_sessions(self, params: ListAllSessionsParams) -> ApiResponse:
        """List all sessions."""
        processed_params = params.dict(exclude_unset=True)
        response = self.client.list_all_sessions(processed_params)
        return self.prepare_response(response)

    def create_webhook(self, params: CreateWebhookParams) -> ApiResponse:
        """Create a webhook."""
        processed_params = params.dict(exclude_unset=True)
        response = self.client.create_webhook(processed_params)
        return self.prepare_response(response)

    def retrieve_webhook(self, params: RetrieveWebhookParams) -> ApiResponse:
        """Retrieve a webhook."""
        processed_params = params.dict(exclude_unset=True)
        response = self.client.retrieve_webhook(processed_params["uid"])
        return self.prepare_response(response)

    def delete_webhook(self, params: DeleteWebhookParams) -> ApiResponse:
        """Delete a webhook."""
        processed_params = params.dict(exclude_unset=True)
        response = self.client.delete_webhook(processed_params["uid"])
        return self.prepare_response(response)

    def create_movie(self, params: CreateMovieParams) -> ApiResponse:
        """Create a movie."""
        processed_params = params.dict(exclude_unset=True)
        response = self.client.create_movie(processed_params)
        return self.prepare_response(response)

    def retrieve_movie(self, params: RetrieveMovieParams) -> ApiResponse:
        """Retrieve a movie."""
        processed_params = params.dict(exclude_unset=True)
        response = self.client.retrieve_movie(processed_params["uid"])
        return self.prepare_response(response)

    def list_all_movies(self, params: ListAllMoviesParams) -> ApiResponse:
        """List all movies."""
        processed_params = params.dict(exclude_unset=True)
        response = self.client.list_all_movies(processed_params)
        return self.prepare_response(response)

    def create_diagnosis(self, params: CreateDiagnosisParams) -> ApiResponse:
        """Create a diagnosis."""
        processed_params = params.dict(exclude_unset=True)
        response = self.client.create_diagnosis(processed_params)
        return self.prepare_response(response)

    def retrieve_diagnosis(self, params: RetrieveDiagnosisParams) -> ApiResponse:
        """Retrieve a diagnosis."""
        processed_params = params.dict(exclude_unset=True)
        response = self.client.retrieve_diagnosis(processed_params["uid"])
        return self.prepare_response(response)

    def create_signed_base(self, params: CreateSignedBaseParams) -> ApiResponse:
        """Create a signed base."""
        processed_params = params.dict(exclude_unset=True)
        response = self.client.create_signed_base(processed_params["uid"])
        return self.prepare_response(response)

    def list_signed_bases(self, params: ListSignedBasesParams) -> ApiResponse:
        """List signed bases."""
        processed_params = params.dict(exclude_unset=True)
        uid = processed_params.pop("uid", None)
        response = self.client.list_signed_bases(uid, processed_params)
        return self.prepare_response(response)

    def create_project(self, params: CreateProjectParams) -> ApiResponse:
        """Create a project."""
        processed_params = params.dict(exclude_unset=True)
        response = self.client.create_project(processed_params)
        return self.prepare_response(response)

    def retrieve_project(self, params: RetrieveProjectParams) -> ApiResponse:
        """Retrieve a project."""
        processed_params = params.dict(exclude_unset=True)
        response = self.client.retrieve_project(processed_params["uid"])
        return self.prepare_response(response)

    def hydrate_project(self, params: HydrateProjectParams) -> ApiResponse:
        """Hydrate a project."""
        processed_params = params.dict(exclude_unset=True)
        uid = processed_params.pop("uid", None)
        response = self.client.hydrate_project(uid, processed_params)
        return self.prepare_response(response)

    def list_all_projects(self, params: ListAllProjectsParams) -> ApiResponse:
        """List all projects."""
        processed_params = params.dict(exclude_unset=True)
        response = self.client.list_all_projects(processed_params)
        return self.prepare_response(response)

    def list_fonts(self, params: ListFontsParams) -> ApiResponse:
        """List fonts."""
        # If your client call doesn't need the actual params, that's fine.
        # processed_params = params.dict(exclude_unset=True)
        response = self.client.list_fonts()
        return self.prepare_response(response)

    def list_effects(self, params: ListEffectsParams) -> ApiResponse:
        """List effects."""
        # processed_params = params.dict(exclude_unset=True)
        response = self.client.list_effects()
        return self.prepare_response(response)

    def join_pdf(self, params: JoinPdfParams) -> ApiResponse:
        """Join multiple PDFs into one."""
        processed_params = params.dict(exclude_unset=True)
        response = self.client.join_pdf(processed_params)
        return self.prepare_response(response)

    def retrieve_joined_pdf(self, params: RetrieveJoinedPdfParams) -> ApiResponse:
        """Retrieve a joined PDF."""
        processed_params = params.dict(exclude_unset=True)
        response = self.client.retrieve_joined_pdf(processed_params["uid"])
        return self.prepare_response(response)

    def rasterize_pdf(self, params: RasterizePdfParams) -> ApiResponse:
        """Convert a PDF to images."""
        processed_params = params.dict(exclude_unset=True)
        response = self.client.rasterize_pdf(processed_params)
        return self.prepare_response(response)

    def retrieve_rasterized_pdf(self, params: RetrieveRasterizedPdfParams) -> ApiResponse:
        """Retrieve a rasterized PDF."""
        processed_params = params.dict(exclude_unset=True)
        response = self.client.retrieve_rasterized_pdf(processed_params["uid"])
        return self.prepare_response(response)
