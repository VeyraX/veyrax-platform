from fastapi import APIRouter, Depends, HTTPException, Request, Body
from typing import Dict, Any
from .schema import (
    DomainSearchParams, EmailFinderParams, EmailVerifierParams, EmailCountParams,
    EmailEnrichmentParams, CompanyEnrichmentParams, CombinedEnrichmentParams,
    DomainSearchResponseSchema, EmailFinderResponseSchema, EmailVerifierResponseSchema,
    EmailCountResponseSchema, EmailEnrichmentResponseSchema, CompanyEnrichmentResponseSchema,
    CombinedEnrichmentResponseSchema, AccountInformationResponseSchema, ApiResponse
)
from .service import HunterIOService
from .client import HunterIOClient
from ..common.auth import validate_provider_api_key
from ..common.input_schema_decorator import schema
from pydantic import ValidationError
from ..common.utils import apply_error_handler_to_service, apply_error_handler_to_router, apply_error_handler_to_client
from ..common.examples_handler import ExamplesLoader
import os

router = APIRouter(prefix="/hunterio", tags=["hunterio"])

examples = ExamplesLoader()

async def get_hunterio_service(request: Request):
    try:
        api_key = await validate_provider_api_key(request, "hunterio")
        client = HunterIOClient(api_key)
        apply_error_handler_to_client(client)
        service = HunterIOService(client)
        apply_error_handler_to_service(service)
        return service
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize Hunter.io service: {str(e)}")

@router.post("/domain_search", response_model=ApiResponse)
@schema(input_schema_class=DomainSearchParams, output_schema_class=DomainSearchResponseSchema, examples=examples["/hunterio/domain_search"])
async def domain_search(
    params: Dict[str, Any] = Body(...),
    service: HunterIOService = Depends(get_hunterio_service)
):
    validated_params = DomainSearchParams(**params)
    return service.domain_search(validated_params)

@router.post("/email_finder", response_model=ApiResponse)
@schema(input_schema_class=EmailFinderParams, output_schema_class=EmailFinderResponseSchema, examples=examples["/hunterio/email_finder"])
async def email_finder(
    params: Dict[str, Any] = Body(...),
    service: HunterIOService = Depends(get_hunterio_service)
):
    validated_params = EmailFinderParams(**params)
    return service.email_finder(validated_params)

@router.post("/email_verifier", response_model=ApiResponse)
@schema(input_schema_class=EmailVerifierParams, output_schema_class=EmailVerifierResponseSchema, examples=examples["/hunterio/email_verifier"])
async def email_verifier(
    params: Dict[str, Any] = Body(...),
    service: HunterIOService = Depends(get_hunterio_service)
):
    validated_params = EmailVerifierParams(**params)
    return service.email_verifier(validated_params)

@router.post("/email_count", response_model=ApiResponse)
@schema(input_schema_class=EmailCountParams, output_schema_class=EmailCountResponseSchema, examples=examples["/hunterio/email_count"])
async def email_count(
    params: Dict[str, Any] = Body(...),
    service: HunterIOService = Depends(get_hunterio_service)
):
    validated_params = EmailCountParams(**params)
    return service.email_count(validated_params)

@router.post("/email_enrichment", response_model=ApiResponse)
@schema(input_schema_class=EmailEnrichmentParams, output_schema_class=EmailEnrichmentResponseSchema, examples=examples["/hunterio/email_enrichment"])
async def email_enrichment(
    params: Dict[str, Any] = Body(...),
    service: HunterIOService = Depends(get_hunterio_service)
):
    validated_params = EmailEnrichmentParams(**params)
    return service.email_enrichment(validated_params)

@router.post("/company_enrichment", response_model=ApiResponse)
@schema(input_schema_class=CompanyEnrichmentParams, output_schema_class=CompanyEnrichmentResponseSchema, examples=examples["/hunterio/company_enrichment"])
async def company_enrichment(
    params: Dict[str, Any] = Body(...),
    service: HunterIOService = Depends(get_hunterio_service)
):
    validated_params = CompanyEnrichmentParams(**params)
    return service.company_enrichment(validated_params)

@router.post("/combined_enrichment", response_model=ApiResponse)
@schema(input_schema_class=CombinedEnrichmentParams, output_schema_class=CombinedEnrichmentResponseSchema, examples=examples["/hunterio/combined_enrichment"])
async def combined_enrichment(
    params: Dict[str, Any] = Body(...),
    service: HunterIOService = Depends(get_hunterio_service)
):
    validated_params = CombinedEnrichmentParams(**params)
    return service.combined_enrichment(validated_params)

@router.post("/account_information", response_model=ApiResponse)
@schema(output_schema_class=AccountInformationResponseSchema, examples=examples["/hunterio/account_information"])
async def account_information(
    service: HunterIOService = Depends(get_hunterio_service)
):
    return service.account_information()

@router.post("/validate_key")
async def validate_key(
    params: Dict[str, Any] = Body(...),
):
    try:
        api_key = params.get("api_key")
        if not api_key:
            return {"valid": False, "message": "API key is required"}
        
        client = HunterIOClient(api_key=api_key)
        test_response = client.account_information()
        return {"valid": True, "message": "API key is valid"}
    except Exception as e:
        return {"valid": False, "message": f"Invalid API key: {str(e)}"}

apply_error_handler_to_router(router) 