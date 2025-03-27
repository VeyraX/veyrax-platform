from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

class CheckAuthorizationParams(BaseModel):
    pass

class CheckAuthorizationResponse(BaseModel):
    status_code: int
    message: str
    project: Optional[str] = None

class RetrieveAccountStatusParams(BaseModel):
    pass

class CurrentProject(BaseModel):
    name: Optional[str] = None
    templates: Optional[int] = None

class RetrieveAccountStatusResponse(BaseModel):
    status_code: int
    created_at: Optional[datetime] = None
    uid: Optional[str] = None
    paid_plan_name: Optional[str] = None
    api_usage: Optional[int] = None
    api_quota: Optional[int] = None
    current_project: Optional[CurrentProject] = None

class CreateImageParams(BaseModel):
    template: str
    modifications: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[str] = None

class CreateImageResponse(BaseModel):
    status_code: int
    uid: str
    status: str
    image_url: Optional[str] = None
    template: Optional[str] = None
    created_at: Optional[datetime] = None

class RetrieveImageParams(BaseModel):
    uid: str

class ImageObject(BaseModel):
    uid: str
    status: str
    image_url: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    template: Optional[str] = None
    created_at: Optional[datetime] = None

class RetrieveImageResponse(BaseModel):
    status_code: int
    image: ImageObject

class ListAllImagesParams(BaseModel):
    page: Optional[int] = Field(default=1, ge=1)
    limit: Optional[int] = Field(default=25, ge=1)

class ListAllImagesResponse(BaseModel):
    status_code: int
    images: List[ImageObject]

class CreateVideoParams(BaseModel):
    video_template: str
    input_media_url: str
    modifications: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[str] = None

class CreateVideoResponse(BaseModel):
    status_code: int
    uid: str
    status: str
    video_url: Optional[str] = None
    created_at: Optional[datetime] = None

class RetrieveVideoParams(BaseModel):
    uid: str

class VideoObject(BaseModel):
    uid: str
    status: str
    video_url: Optional[str] = None
    render_type: Optional[str] = None
    created_at: Optional[datetime] = None

class RetrieveVideoResponse(BaseModel):
    status_code: int
    video: VideoObject

class UpdateVideoParams(BaseModel):
    uid: str
    transcription: Optional[List[str]] = None
    approved: Optional[bool] = None

class UpdateVideoResponse(BaseModel):
    status_code: int
    video: VideoObject

class ListAllVideosParams(BaseModel):
    page: Optional[int] = Field(default=1, ge=1)

class ListAllVideosResponse(BaseModel):
    status_code: int
    videos: List[VideoObject]

class CreateCollectionParams(BaseModel):
    template_set: str
    modifications: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[str] = None

class CreateCollectionResponse(BaseModel):
    status_code: int
    uid: str
    status: str
    image_urls: Optional[Dict[str, str]] = None
    created_at: Optional[datetime] = None

class RetrieveCollectionParams(BaseModel):
    uid: str

class CollectionObject(BaseModel):
    uid: str
    status: str
    template_set: Optional[str] = None
    image_urls: Optional[Dict[str, str]] = None
    created_at: Optional[datetime] = None

class RetrieveCollectionResponse(BaseModel):
    status_code: int
    collection: CollectionObject

class ListAllCollectionsParams(BaseModel):
    page: Optional[int] = Field(default=1, ge=1)

class ListAllCollectionsResponse(BaseModel):
    status_code: int
    collections: List[CollectionObject]

class CreateAnimatedGifParams(BaseModel):
    template: str
    frames: List[List[Dict[str, Any]]]
    fps: Optional[int] = 1
    loop: Optional[bool] = True

class CreateAnimatedGifResponse(BaseModel):
    status_code: int
    uid: str
    status: str
    created_at: Optional[datetime] = None

class RetrieveAnimatedGifParams(BaseModel):
    uid: str

class AnimatedGifObject(BaseModel):
    uid: str
    status: str
    image_url: Optional[str] = None
    fps: Optional[int] = 1
    loop: Optional[bool] = True
    created_at: Optional[datetime] = None

class RetrieveAnimatedGifResponse(BaseModel):
    status_code: int
    animated_gif: AnimatedGifObject

class ListAllAnimatedGifsParams(BaseModel):
    page: Optional[int] = Field(default=1, ge=1)

class ListAllAnimatedGifsResponse(BaseModel):
    status_code: int
    animated_gifs: List[AnimatedGifObject]

class CreateScreenshotParams(BaseModel):
    url: str
    width: Optional[int] = 1200
    height: Optional[int] = None
    mobile: Optional[bool] = False

class CreateScreenshotResponse(BaseModel):
    status_code: int
    uid: str
    status: str
    screenshot_image_url: Optional[str] = None
    created_at: Optional[datetime] = None

class RetrieveScreenshotParams(BaseModel):
    uid: str

class ScreenshotObject(BaseModel):
    uid: str
    status: str
    screenshot_image_url: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    created_at: Optional[datetime] = None

class RetrieveScreenshotResponse(BaseModel):
    status_code: int
    screenshot: ScreenshotObject

class ListAllScreenshotsParams(BaseModel):
    page: Optional[int] = Field(default=1, ge=1)

class ListAllScreenshotsResponse(BaseModel):
    status_code: int
    screenshots: List[ScreenshotObject]

class CreateTemplateParams(BaseModel):
    name: str
    width: int
    height: int
    tags: Optional[List[str]] = None

class CreateTemplateResponse(BaseModel):
    status_code: int
    uid: str
    name: str
    width: int
    height: int
    tags: Optional[List[str]] = None
    created_at: Optional[datetime] = None

class DuplicateTemplateParams(BaseModel):
    source_uid: str

class DuplicateTemplateResponse(BaseModel):
    status_code: int
    uid: str
    name: str
    width: int
    height: int
    created_at: Optional[datetime] = None

class RetrieveTemplateParams(BaseModel):
    uid: str

class TemplateObject(BaseModel):
    uid: str
    name: str
    width: int
    height: int
    tags: Optional[List[str]] = None
    preview_url: Optional[str] = None
    created_at: Optional[datetime] = None

class RetrieveTemplateResponse(BaseModel):
    status_code: int
    template: TemplateObject

class UpdateTemplateParams(BaseModel):
    uid: str
    name: Optional[str] = None
    tags: Optional[List[str]] = None
    width: Optional[int] = None
    height: Optional[int] = None

class UpdateTemplateResponse(BaseModel):
    status_code: int
    template: TemplateObject

class ListAllTemplatesParams(BaseModel):
    page: Optional[int] = Field(default=1, ge=1)
    limit: Optional[int] = Field(default=25, ge=1)

class ListAllTemplatesResponse(BaseModel):
    status_code: int
    templates: List[TemplateObject]

class ImportTemplatesParams(BaseModel):
    publications: List[str]

class ImportedTemplate(BaseModel):
    uid: str
    name: str

class ImportTemplatesResponse(BaseModel):
    status_code: int
    imported: List[ImportedTemplate]

class CreateTemplateSetParams(BaseModel):
    name: Optional[str] = None
    templates: List[str]

class CreateTemplateSetResponse(BaseModel):
    status_code: int
    uid: str
    name: Optional[str] = None
    templates: List[str]
    created_at: Optional[datetime] = None

class UpdateTemplateSetParams(BaseModel):
    uid: str
    name: Optional[str] = None
    templates: List[str]

class TemplateSetObject(BaseModel):
    uid: str
    name: Optional[str] = None
    templates: List[str]
    created_at: Optional[datetime] = None

class UpdateTemplateSetResponse(BaseModel):
    status_code: int
    template_set: TemplateSetObject

class RetrieveTemplateSetParams(BaseModel):
    uid: str

class RetrieveTemplateSetResponse(BaseModel):
    status_code: int
    template_set: TemplateSetObject

class ListAllTemplateSetsParams(BaseModel):
    page: Optional[int] = Field(default=1, ge=1)

class ListAllTemplateSetsResponse(BaseModel):
    status_code: int
    template_sets: List[TemplateSetObject]

class CreateVideoTemplateParams(BaseModel):
    template: str
    render_type: str
    approval_required: Optional[bool] = None

class CreateVideoTemplateResponse(BaseModel):
    status_code: int
    uid: str
    name: Optional[str] = None
    render_type: str
    approval_required: Optional[bool] = None
    created_at: Optional[datetime] = None

class RetrieveVideoTemplateParams(BaseModel):
    uid: str

class VideoTemplateObject(BaseModel):
    uid: str
    name: Optional[str] = None
    render_type: Optional[str] = None
    approval_required: Optional[bool] = None
    width: Optional[int] = None
    height: Optional[int] = None
    created_at: Optional[datetime] = None

class RetrieveVideoTemplateResponse(BaseModel):
    status_code: int
    video_template: VideoTemplateObject

class ListAllVideoTemplatesParams(BaseModel):
    page: Optional[int] = Field(default=1, ge=1)

class ListAllVideoTemplatesResponse(BaseModel):
    status_code: int
    video_templates: List[VideoTemplateObject]

class CreateSessionParams(BaseModel):
    template: str
    mode: Optional[str] = None

class SessionObject(BaseModel):
    uid: str
    session_editor_url: str
    expired: bool
    template: Optional[str] = None
    created_at: Optional[datetime] = None

class CreateSessionResponse(BaseModel):
    status_code: int
    session: SessionObject

class RetrieveSessionParams(BaseModel):
    uid: str

class RetrieveSessionResponse(BaseModel):
    status_code: int
    session: SessionObject

class ListAllSessionsParams(BaseModel):
    page: Optional[int] = Field(default=1, ge=1)

class ListAllSessionsResponse(BaseModel):
    status_code: int
    sessions: List[SessionObject]

class CreateWebhookParams(BaseModel):
    url: str
    event: str

class WebhookObject(BaseModel):
    uid: str
    url: str
    event: str
    created_at: Optional[datetime] = None

class CreateWebhookResponse(BaseModel):
    status_code: int
    webhook: WebhookObject

class RetrieveWebhookParams(BaseModel):
    uid: str

class RetrieveWebhookResponse(BaseModel):
    status_code: int
    webhook: WebhookObject

class DeleteWebhookParams(BaseModel):
    uid: str

class DeleteWebhookResponse(BaseModel):
    status_code: int
    message: str

class CreateMovieParams(BaseModel):
    width: int
    height: int
    transition: Optional[str] = None
    soundtrack_url: Optional[str] = None
    inputs: List[Dict[str, Any]]

class CreateMovieResponse(BaseModel):
    status_code: int
    uid: str
    status: str
    movie_url: Optional[str] = None
    created_at: Optional[datetime] = None

class RetrieveMovieParams(BaseModel):
    uid: str

class MovieObject(BaseModel):
    uid: str
    status: str
    percent_rendered: Optional[int] = None
    movie_url: Optional[str] = None
    created_at: Optional[datetime] = None

class RetrieveMovieResponse(BaseModel):
    status_code: int
    movie: MovieObject

class ListAllMoviesParams(BaseModel):
    page: Optional[int] = Field(default=1, ge=1)

class ListAllMoviesResponse(BaseModel):
    status_code: int
    movies: List[MovieObject]

class CreateDiagnosisParams(BaseModel):
    image_uid: str

class CreateDiagnosisResponse(BaseModel):
    status_code: int
    uid: str
    type: str
    parent_uid: str
    status: str

class RetrieveDiagnosisParams(BaseModel):
    uid: str

class ExternalImageIssue(BaseModel):
    image_url: str
    result: str
    comment: Optional[str] = None

class DiagnosisReport(BaseModel):
    external_images: Optional[List[ExternalImageIssue]] = None

class DiagnosisObject(BaseModel):
    uid: str
    status: str
    type: str
    parent_uid: str
    report: Optional[DiagnosisReport] = None
    created_at: Optional[datetime] = None

class RetrieveDiagnosisResponse(BaseModel):
    status_code: int
    diagnosis: DiagnosisObject

class CreateSignedBaseParams(BaseModel):
    uid: str

class SignedBaseObject(BaseModel):
    uid: str
    base_url: str
    example_url: Optional[str] = None

class CreateSignedBaseResponse(BaseModel):
    status_code: int
    signed_base: SignedBaseObject

class ListSignedBasesParams(BaseModel):
    uid: str
    page: Optional[int] = Field(default=1, ge=1)

class ListSignedBasesResponse(BaseModel):
    status_code: int
    signed_bases: List[SignedBaseObject]

class CreateProjectParams(BaseModel):
    name: str
    image_proxy: Optional[bool] = None
    web_sessions: Optional[bool] = None

class ProjectObject(BaseModel):
    uid: str
    name: str
    templates: Optional[int] = None
    image_proxy: Optional[bool] = None
    web_sessions: Optional[bool] = None
    created_at: Optional[datetime] = None

class CreateProjectResponse(BaseModel):
    status_code: int
    project: ProjectObject

class RetrieveProjectParams(BaseModel):
    uid: str

class RetrieveProjectResponse(BaseModel):
    status_code: int
    project: ProjectObject

class HydrateProjectParams(BaseModel):
    uid: str
    source: Optional[str] = None
    templates: Optional[List[str]] = None

class HydrateProjectResponse(BaseModel):
    status_code: int
    uid: str
    hydrated_from: Optional[str] = None
    imported_templates: Optional[List[Dict[str, str]]] = None

class ListAllProjectsParams(BaseModel):
    page: Optional[int] = Field(default=1, ge=1)

class ListAllProjectsResponse(BaseModel):
    status_code: int
    projects: List[ProjectObject]

class ListFontsParams(BaseModel):
    pass

class FontsResponse(BaseModel):
    status_code: int
    fonts: Dict[str, List[str]]

class ListEffectsParams(BaseModel):
    pass

class EffectsResponse(BaseModel):
    status_code: int
    effects: List[str]

class JoinPdfParams(BaseModel):
    pdf_inputs: List[str]

class JoinPdfResponse(BaseModel):
    status_code: int
    uid: str
    status: str
    joined_pdf_url: Optional[str] = None
    pdf_inputs: Optional[List[str]] = None

class RetrieveJoinedPdfParams(BaseModel):
    uid: str

class RetrieveJoinedPdfObject(BaseModel):
    uid: str
    status: str
    joined_pdf_url: Optional[str] = None
    pdf_inputs: Optional[List[str]] = None

class RetrieveJoinedPdfResponse(BaseModel):
    status_code: int
    joined_pdf: RetrieveJoinedPdfObject

class RasterizePdfParams(BaseModel):
    url: str
    dpi: Optional[int] = 300

class RasterizePdfResponse(BaseModel):
    status_code: int
    uid: str
    status: str
    image_url_png: Optional[str] = None
    image_url_jpg: Optional[str] = None

class RetrieveRasterizedPdfParams(BaseModel):
    uid: str

class RasterizedPdfObject(BaseModel):
    uid: str
    status: str
    image_url_png: Optional[str] = None
    image_url_jpg: Optional[str] = None
    dpi: Optional[int] = None
    created_at: Optional[datetime] = None

class RetrieveRasterizedPdfResponse(BaseModel):
    status_code: int
    rasterization: RasterizedPdfObject

class ApiResponse(BaseModel):
    data: Any
    component: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = Field(
        None,
        description="UI components configuration for rendering results"
    )
