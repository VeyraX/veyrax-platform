from fastapi import APIRouter, Body, Depends, HTTPException
from starlette.requests import Request as FastAPIRequest
from typing import Dict, Any
from .schema import (
    CreateLinkParams,
    UpdateLinkParams,
    UpsertLinkParams,
    DeleteLinkParams,
    GetLinkParams,
    GetLinksParams,
    ApiResponse,
    BulkCreateLinksParams,
    BulkUpdateLinksParams,
    BulkDeleteLinksParams,
    GetQRCodeParams,
    GetAnalyticsParams,
    GetEventsParams,
    GetCustomerParams,
    GetCustomersParams,
    UpdateCustomerParams,
    DeleteCustomerParams,
    TrackLeadParams,
    TrackSaleParams,
    CreateTagParams,
    GetTagsParams,
    UpdateTagParams,
    CreateDomainParams,
    UpdateDomainParams,
    DeleteDomainParams,
    GetDomainsParams,
    GetWorkspaceParams,
    UpdateWorkspaceParams
)
from .service import DubService
from .client import DubClient
from ..common.auth import validate_provider_api_key
from ..common.input_schema_decorator import schema
from ..common.utils import apply_error_handler_to_service, apply_error_handler_to_router
from ..common.examples_handler import ExamplesLoader

router = APIRouter(prefix="/dub", tags=["dub"])
examples = ExamplesLoader()

async def get_dub_service(request: FastAPIRequest):
    try:
        api_key = await validate_provider_api_key(request, "dub")
        client = DubClient(api_key)
        service = DubService(client)
        
        apply_error_handler_to_service(service)
        
        return service
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Failed to initialize Dub service: {str(e)}"
        )

@router.post("/create_link", response_model=ApiResponse)
@schema(
    input_schema_class=CreateLinkParams,
    output_schema_class=ApiResponse,
    examples=examples["/dub/create_link"]
)
async def create_link(
    params: Dict[str, Any] = Body(...),
    service: DubService = Depends(get_dub_service)
):
    validated_params = CreateLinkParams(**params)
    return service.create_link(validated_params)

@router.post("/update_link", response_model=ApiResponse)
@schema(
    input_schema_class=UpdateLinkParams,
    output_schema_class=ApiResponse,
    examples=examples["/dub/update_link"]
)
async def update_link(
    params: Dict[str, Any] = Body(...),
    service: DubService = Depends(get_dub_service)
):
    validated_params = UpdateLinkParams(**params)
    return service.update_link(validated_params.link_id, validated_params)

@router.post("/upsert_link", response_model=ApiResponse)
@schema(
    input_schema_class=UpsertLinkParams,
    output_schema_class=ApiResponse,
    examples=examples["/dub/upsert_link"]
)
async def upsert_link(
    params: Dict[str, Any] = Body(...),
    service: DubService = Depends(get_dub_service)
):
    validated_params = UpsertLinkParams(**params)
    return service.upsert_link(validated_params)

@router.post("/delete_link", response_model=ApiResponse)
@schema(
    input_schema_class=DeleteLinkParams,
    output_schema_class=ApiResponse,
    examples=examples["/dub/delete_link"]
)
async def delete_link(
    params: Dict[str, Any] = Body(...),
    service: DubService = Depends(get_dub_service)
):
    validated_params = DeleteLinkParams(**params)
    return service.delete_link(validated_params.link_id)

@router.post("/get_link", response_model=ApiResponse)
@schema(
    input_schema_class=GetLinkParams,
    output_schema_class=ApiResponse,
    examples=examples["/dub/get_link"]
)
async def get_link(
    params: Dict[str, Any] = Body(...),
    service: DubService = Depends(get_dub_service)
):
    validated_params = GetLinkParams(**params)
    return service.get_link_info(validated_params.link_id)

@router.post("/get_links", response_model=ApiResponse)
@schema(
    input_schema_class=GetLinksParams,
    output_schema_class=ApiResponse,
    examples=examples["/dub/get_links"]
)
async def get_links(
    params: Dict[str, Any] = Body(...),
    service: DubService = Depends(get_dub_service)
):
    return service.get_links()

@router.post("/get_links_count", response_model=ApiResponse)
@schema(
    input_schema_class=GetLinksParams,
    output_schema_class=ApiResponse,
    examples=examples["/dub/get_links_count"]
)
async def get_links_count(
    params: Dict[str, Any] = Body(...),
    service: DubService = Depends(get_dub_service)
):
    return service.get_links_count()

@router.post("/bulk_create_links", response_model=ApiResponse)
@schema(
    input_schema_class=BulkCreateLinksParams,
    output_schema_class=ApiResponse,
    examples=examples["/dub/bulk_create_links"]
)
async def bulk_create_links(
    params: Dict[str, Any] = Body(...),
    service: DubService = Depends(get_dub_service)
):
    validated_params = BulkCreateLinksParams(**params)
    return service.bulk_create_links(validated_params.links)

@router.post("/bulk_update_links", response_model=ApiResponse)
@schema(
    input_schema_class=BulkUpdateLinksParams,
    output_schema_class=ApiResponse,
    examples=examples["/dub/bulk_update_links"]
)
async def bulk_update_links(
    params: Dict[str, Any] = Body(...),
    service: DubService = Depends(get_dub_service)
):
    validated_params = BulkUpdateLinksParams(**params)
    return service.bulk_update_links(validated_params)

@router.post("/bulk_delete_links", response_model=ApiResponse)
@schema(
    input_schema_class=BulkDeleteLinksParams,
    output_schema_class=ApiResponse,
    examples=examples["/dub/bulk_delete_links"]
)
async def bulk_delete_links(
    params: Dict[str, Any] = Body(...),
    service: DubService = Depends(get_dub_service)
):
    validated_params = BulkDeleteLinksParams(**params)
    return service.bulk_delete_links(validated_params.link_ids)

@router.post("/get_qr_code", response_model=ApiResponse)
@schema(
    input_schema_class=GetQRCodeParams,
    output_schema_class=ApiResponse,
    examples=examples["/dub/get_qr_code"]
)
async def get_qr_code(
    params: Dict[str, Any] = Body(...),
    service: DubService = Depends(get_dub_service)
):
    validated_params = GetQRCodeParams(**params)
    return service.get_qr_code(validated_params.link_id)

@router.post("/get_analytics", response_model=ApiResponse)
@schema(
    input_schema_class=GetAnalyticsParams,
    output_schema_class=ApiResponse,
    examples=examples["/dub/get_analytics"]
)
async def get_analytics(
    params: Dict[str, Any] = Body(...),
    service: DubService = Depends(get_dub_service)
):
    return service.get_analytics()

@router.post("/get_events", response_model=ApiResponse)
@schema(
    input_schema_class=GetEventsParams,
    output_schema_class=ApiResponse,
    examples=examples["/dub/get_events"]
)
async def get_events(
    params: Dict[str, Any] = Body(...),
    service: DubService = Depends(get_dub_service)
):
    return service.get_events()

# Customer management endpoints
@router.post("/get_customer", response_model=ApiResponse)
@schema(
    input_schema_class=GetCustomerParams,
    output_schema_class=ApiResponse,
    examples=examples["/dub/get_customer"]
)
async def get_customer(
    params: Dict[str, Any] = Body(...),
    service: DubService = Depends(get_dub_service)
):
    validated_params = GetCustomerParams(**params)
    return service.get_customer(validated_params.customer_id)

@router.post("/get_customers", response_model=ApiResponse)
@schema(
    input_schema_class=GetCustomersParams,
    output_schema_class=ApiResponse,
    examples=examples["/dub/get_customers"]
)
async def get_customers(
    params: Dict[str, Any] = Body(...),
    service: DubService = Depends(get_dub_service)
):
    return service.get_customers()

@router.post("/update_customer", response_model=ApiResponse)
@schema(
    input_schema_class=UpdateCustomerParams,
    output_schema_class=ApiResponse,
    examples=examples["/dub/update_customer"]
)
async def update_customer(
    params: Dict[str, Any] = Body(...),
    service: DubService = Depends(get_dub_service)
):
    validated_params = UpdateCustomerParams(**params)
    return service.update_customer(validated_params.customer_id, validated_params)

@router.post("/delete_customer", response_model=ApiResponse)
@schema(
    input_schema_class=DeleteCustomerParams,
    output_schema_class=ApiResponse,
    examples=examples["/dub/delete_customer"]
)
async def delete_customer(
    params: Dict[str, Any] = Body(...),
    service: DubService = Depends(get_dub_service)
):
    validated_params = DeleteCustomerParams(**params)
    return service.delete_customer(validated_params.customer_id)

# Tracking endpoints
@router.post("/track_lead", response_model=ApiResponse)
@schema(
    input_schema_class=TrackLeadParams,
    output_schema_class=ApiResponse,
    examples=examples["/dub/track_lead"]
)
async def track_lead(
    params: Dict[str, Any] = Body(...),
    service: DubService = Depends(get_dub_service)
):
    validated_params = TrackLeadParams(**params)
    return service.track_lead(validated_params)

@router.post("/track_sale", response_model=ApiResponse)
@schema(
    input_schema_class=TrackSaleParams,
    output_schema_class=ApiResponse,
    examples=examples["/dub/track_sale"]
)
async def track_sale(
    params: Dict[str, Any] = Body(...),
    service: DubService = Depends(get_dub_service)
):
    validated_params = TrackSaleParams(**params)
    return service.track_sale(validated_params)

# Tag management endpoints
@router.post("/create_tag", response_model=ApiResponse)
@schema(
    input_schema_class=CreateTagParams,
    output_schema_class=ApiResponse,
    examples=examples["/dub/create_tag"]
)
async def create_tag(
    params: Dict[str, Any] = Body(...),
    service: DubService = Depends(get_dub_service)
):
    validated_params = CreateTagParams(**params)
    return service.create_tag(validated_params)

@router.post("/get_tags", response_model=ApiResponse)
@schema(
    input_schema_class=GetTagsParams,
    output_schema_class=ApiResponse,
    examples=examples["/dub/get_tags"]
)
async def get_tags(
    params: Dict[str, Any] = Body(...),
    service: DubService = Depends(get_dub_service)
):
    return service.get_tags()

@router.post("/update_tag", response_model=ApiResponse)
@schema(
    input_schema_class=UpdateTagParams,
    output_schema_class=ApiResponse,
    examples=examples["/dub/update_tag"]
)
async def update_tag(
    params: Dict[str, Any] = Body(...),
    service: DubService = Depends(get_dub_service)
):
    validated_params = UpdateTagParams(**params)
    return service.update_tag(validated_params.tag_id, validated_params)

# Domain management endpoints
@router.post("/create_domain", response_model=ApiResponse)
@schema(
    input_schema_class=CreateDomainParams,
    output_schema_class=ApiResponse,
    examples=examples["/dub/create_domain"]
)
async def create_domain(
    params: Dict[str, Any] = Body(...),
    service: DubService = Depends(get_dub_service)
):
    validated_params = CreateDomainParams(**params)
    return service.create_domain(validated_params)

@router.post("/update_domain", response_model=ApiResponse)
@schema(
    input_schema_class=UpdateDomainParams,
    output_schema_class=ApiResponse,
    examples=examples["/dub/update_domain"]
)
async def update_domain(
    params: Dict[str, Any] = Body(...),
    service: DubService = Depends(get_dub_service)
):
    validated_params = UpdateDomainParams(**params)
    return service.update_domain(validated_params.domain_slug, validated_params)

@router.post("/delete_domain", response_model=ApiResponse)
@schema(
    input_schema_class=DeleteDomainParams,
    output_schema_class=ApiResponse,
    examples=examples["/dub/delete_domain"]
)
async def delete_domain(
    params: Dict[str, Any] = Body(...),
    service: DubService = Depends(get_dub_service)
):
    validated_params = DeleteDomainParams(**params)
    return service.delete_domain(validated_params.domain_slug)

@router.post("/get_domains", response_model=ApiResponse)
@schema(
    input_schema_class=GetDomainsParams,
    output_schema_class=ApiResponse,
    examples=examples["/dub/get_domains"]
)
async def get_domains(
    params: Dict[str, Any] = Body(...),
    service: DubService = Depends(get_dub_service)
):
    return service.get_domains()

# Workspace management endpoints
@router.post("/get_workspace", response_model=ApiResponse)
@schema(
    input_schema_class=GetWorkspaceParams,
    output_schema_class=ApiResponse,
    examples=examples["/dub/get_workspace"]
)
async def get_workspace(
    params: Dict[str, Any] = Body(...),
    service: DubService = Depends(get_dub_service)
):
    validated_params = GetWorkspaceParams(**params)
    return service.get_workspace(validated_params.id_or_slug)

@router.post("/update_workspace", response_model=ApiResponse)
@schema(
    input_schema_class=UpdateWorkspaceParams,
    output_schema_class=ApiResponse,
    examples=examples["/dub/update_workspace"]
)
async def update_workspace(
    params: Dict[str, Any] = Body(...),
    service: DubService = Depends(get_dub_service)
):
    validated_params = UpdateWorkspaceParams(**params)
    return service.update_workspace(validated_params.id_or_slug, validated_params)

@router.post("/validate_key")
async def validate_key(
    params: Dict[str, Any] = Body(...),
):
    try:
        api_key = params.get("api_key", "")
        if not api_key:
            return {"valid": False, "message": "API key is required"}
        
        client = DubClient(api_key=api_key)
        try:
            client.get_links()
            return {"valid": True, "message": "API key is valid"}
        except Exception as e:
            return {"valid": False, "message": f"Invalid API key"}
    except Exception as e:
        return {"valid": False, "message": f"Invalid request: {str(e)}"}


apply_error_handler_to_router(router)
