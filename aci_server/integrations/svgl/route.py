from fastapi import APIRouter, Depends, Body, HTTPException, Request
from typing import Dict, Any, List, Optional
from .schema import (
    GetAllSvgsParams,
    GetSvgByCategoryParams,
    SearchSvgsParams,
    ApiResponse
)
from .service import SvglService
from .client import SvglClient
from ..common.input_schema_decorator import schema
from ..common.utils import apply_error_handler_to_service, apply_error_handler_to_router, apply_error_handler_to_client
from ..common.examples_handler import ExamplesLoader

router = APIRouter(prefix="/svgl", tags=["svgl"])
examples = ExamplesLoader()

async def get_svgl_service(request: Request):
    try:
        client = SvglClient()
        apply_error_handler_to_client(client)
        service = SvglService(client)
        apply_error_handler_to_service(service)
        return service
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SVGL service initialization failed: {str(e)}")

@router.post("/get_svgs", response_model=ApiResponse)
@schema(
    input_schema_class=GetAllSvgsParams,
    output_schema_class=ApiResponse,
    examples=examples["/svgl/get_svgs"]
)
async def get_svgs(
    params: Dict[str, Any] = Body(...),
    service: SvglService = Depends(get_svgl_service)
):
    validated_params = GetAllSvgsParams(**params)
    return service.get_all_svgs(validated_params.limit)

@router.post("/get_svg_by_category", response_model=ApiResponse)
@schema(
    input_schema_class=GetSvgByCategoryParams,
    output_schema_class=ApiResponse,
    examples=examples["/svgl/get_svg_by_category"]
)
async def get_svg_by_category(
    params: Dict[str, Any] = Body(...),
    service: SvglService = Depends(get_svgl_service)
):
    validated_params = GetSvgByCategoryParams(**params)
    return service.get_svg_by_category(validated_params.category)

@router.post("/get_categories", response_model=ApiResponse)
@schema(
    input_schema_class=None,
    output_schema_class=ApiResponse,
    examples=examples["/svgl/get_categories"]
)
async def get_categories(
    service: SvglService = Depends(get_svgl_service)
):
    return service.get_categories()

@router.post("/search_svgs", response_model=ApiResponse)
@schema(
    input_schema_class=SearchSvgsParams,
    output_schema_class=ApiResponse,
    examples=examples["/svgl/search_svgs"]
)
async def search_svgs(
    params: Dict[str, Any] = Body(...),
    service: SvglService = Depends(get_svgl_service)
):
    validated_params = SearchSvgsParams(**params)
    return service.search_svgs(validated_params.query)

apply_error_handler_to_router(router)
