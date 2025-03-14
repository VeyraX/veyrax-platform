from fastapi import APIRouter, Depends, HTTPException, Body, Request as FastAPIRequest
from typing import Dict, Any, Optional
from .services import FirecrawlService
from .client import FirecrawlClient
from .schema import (
    ScrapeParams,
    BatchScrapeParams,
    GetBatchScrapeParams,
    GetBatchScrapeErrorsParams,
    CrawlParams,
    GetCrawlParams,
    CancelCrawlParams,
    GetCrawlErrorsParams,
    MapParams,
    ExtractParams,
    GetExtractParams,
    SearchParams,
    ScrapeResponse,
    BatchScrapeResponse,
    BatchScrapeStatusResponse,
    BatchScrapeErrorsResponse,
    CrawlResponse,
    CrawlStatusResponse,
    CancelCrawlResponse,
    CrawlErrorsResponse,
    MapResponse,
    ExtractResponse,
    ExtractStatusResponse,
    SearchResponse,
    CreditUsageResponse,
    ApiResponse
)
from ..common.auth import validate_provider_api_key
from ..common.input_schema_decorator import schema
from pydantic import ValidationError
from ..common.utils import format_validation_error
from ..common.examples_handler import ExamplesLoader

router = APIRouter(prefix="/firecrawl", tags=["firecrawl"])

examples = ExamplesLoader()

async def get_firecrawl_service(request: FastAPIRequest):
    try:
        api_key = await validate_provider_api_key(request, "firecrawl")
        client = FirecrawlClient(api_key)
        return FirecrawlService(client)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize service: {str(e)}")

@router.post("/scrape", response_model=ApiResponse)
@schema(input_schema_class=ScrapeParams, output_schema_class=ScrapeResponse, examples=examples["/firecrawl/scrape"])
async def scrape(
    params: Dict[str, Any] = Body(...),
    service: FirecrawlService = Depends(get_firecrawl_service)
):
    try:
        validated_params = ScrapeParams(**params)
        return service.scrape(validated_params)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'ScrapeParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch_scrape", response_model=ApiResponse)
@schema(input_schema_class=BatchScrapeParams, output_schema_class=BatchScrapeResponse, examples=examples["/firecrawl/batch_scrape"])
async def batch_scrape(
    params: Dict[str, Any] = Body(...),
    service: FirecrawlService = Depends(get_firecrawl_service)
):
    try:
        validated_params = BatchScrapeParams(**params)
        return service.batch_scrape(validated_params)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'BatchScrapeParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_batch_status", response_model=ApiResponse)
@schema(input_schema_class=GetBatchScrapeParams, output_schema_class=BatchScrapeStatusResponse, examples=examples["/firecrawl/get_batch_status"])
async def get_batch_status(
    params: Dict[str, Any] = Body(...),
    service: FirecrawlService = Depends(get_firecrawl_service)
):
    try:
        validated_params = GetBatchScrapeParams(**params)
        return service.get_batch_status(validated_params.id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetBatchScrapeParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_batch_errors", response_model=ApiResponse)
@schema(input_schema_class=GetBatchScrapeErrorsParams, output_schema_class=BatchScrapeErrorsResponse, examples=examples["/firecrawl/get_batch_errors"])
async def get_batch_errors(
    params: Dict[str, Any] = Body(...),
    service: FirecrawlService = Depends(get_firecrawl_service)
):
    try:
        validated_params = GetBatchScrapeErrorsParams(**params)
        return service.get_batch_errors(validated_params.id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetBatchScrapeErrorsParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/crawl", response_model=ApiResponse)
@schema(input_schema_class=CrawlParams, output_schema_class=CrawlResponse, examples=examples["/firecrawl/crawl"])
async def crawl(
    params: Dict[str, Any] = Body(...),
    service: FirecrawlService = Depends(get_firecrawl_service)
):
    try:
        validated_params = CrawlParams(**params)
        return service.crawl(validated_params)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'CrawlParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_crawl_status", response_model=ApiResponse)
@schema(input_schema_class=GetCrawlParams, output_schema_class=CrawlStatusResponse, examples=examples["/firecrawl/get_crawl_status"])
async def get_crawl_status(
    params: Dict[str, Any] = Body(...),
    service: FirecrawlService = Depends(get_firecrawl_service)
):
    try:
        validated_params = GetCrawlParams(**params)
        return service.get_crawl_status(validated_params.id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetCrawlParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cancel_crawl", response_model=ApiResponse)
@schema(input_schema_class=CancelCrawlParams, output_schema_class=CancelCrawlResponse, examples=examples["/firecrawl/cancel_crawl"])
async def cancel_crawl(
    params: Dict[str, Any] = Body(...),
    service: FirecrawlService = Depends(get_firecrawl_service)
):
    try:
        validated_params = CancelCrawlParams(**params)
        return service.cancel_crawl(validated_params.id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'CancelCrawlParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_crawl_errors", response_model=ApiResponse)
@schema(input_schema_class=GetCrawlErrorsParams, output_schema_class=CrawlErrorsResponse, examples=examples["/firecrawl/get_crawl_errors"])
async def get_crawl_errors(
    params: Dict[str, Any] = Body(...),
    service: FirecrawlService = Depends(get_firecrawl_service)
):
    try:
        validated_params = GetCrawlErrorsParams(**params)
        return service.get_crawl_errors(validated_params.id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetCrawlErrorsParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/map_site", response_model=ApiResponse)
@schema(input_schema_class=MapParams, output_schema_class=MapResponse, examples=examples["/firecrawl/map_site"])
async def map_site(
    params: Dict[str, Any] = Body(...),
    service: FirecrawlService = Depends(get_firecrawl_service)
):
    try:
        validated_params = MapParams(**params)
        return service.map_site(validated_params)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'MapParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/extract", response_model=ApiResponse)
@schema(input_schema_class=ExtractParams, output_schema_class=ExtractResponse, examples=examples["/firecrawl/extract"])
async def extract(
    params: Dict[str, Any] = Body(...),
    service: FirecrawlService = Depends(get_firecrawl_service)
):
    try:
        validated_params = ExtractParams(**params)
        return service.extract(validated_params)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'ExtractParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_extract_status", response_model=ApiResponse)
@schema(input_schema_class=GetExtractParams, output_schema_class=ExtractStatusResponse, examples=examples["/firecrawl/get_extract_status"])
async def get_extract_status(
    params: Dict[str, Any] = Body(...),
    service: FirecrawlService = Depends(get_firecrawl_service)
):
    try:
        validated_params = GetExtractParams(**params)
        return service.get_extract_status(validated_params.id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetExtractParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search", response_model=ApiResponse)
@schema(input_schema_class=SearchParams, output_schema_class=SearchResponse, examples=examples["/firecrawl/search"])
async def search(
    params: Dict[str, Any] = Body(...),
    service: FirecrawlService = Depends(get_firecrawl_service)
):
    try:
        validated_params = SearchParams(**params)
        return service.search(validated_params)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'SearchParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_credit_usage", response_model=ApiResponse)
@schema(output_schema_class=CreditUsageResponse, examples=examples["/firecrawl/get_credit_usage"])
async def get_credit_usage(
    service: FirecrawlService = Depends(get_firecrawl_service)
):
    try:
        return service.get_credit_usage()
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/validate_key")
async def validate_key(
    params: Dict[str, Any] = Body(...),
):
    try:
        api_key = params.get("api_key")
        if not api_key:
            return {"valid": False, "message": "API key is required"}
        
        client = FirecrawlClient(api_key=api_key)
        test_response = client.get_credit_usage()
        return {"valid": True, "message": "API key is valid"}
    except Exception as e:
        return {"valid": False, "message": f"Invalid API key"}
