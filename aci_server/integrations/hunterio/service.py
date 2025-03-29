from typing import Dict, Any, Union, List, Optional
from .client import HunterIOClient
from .schema import (
    DomainSearchParams, EmailFinderParams, EmailVerifierParams, EmailCountParams,
    EmailEnrichmentParams, CompanyEnrichmentParams, CombinedEnrichmentParams,
    DomainSearchResult, EmailFinderResult, EmailVerifierResult, EmailCountResult,
    EmailEnrichmentResult, CompanyEnrichmentResult, CombinedEnrichmentResult,
    AccountInformationResult, ApiResponse
)
import os
from ..common.component_handler import load_components, prepare_components_auto
import json
from requests.exceptions import HTTPError

class HunterIOService:
    def __init__(self, client: HunterIOClient):
        self.client = client
        self.components_data = self._load_components()
        
    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
        
    def prepare_response(self, data: Any, component_name: str = None) -> ApiResponse:
        tool_name = "hunterio"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)
        
    def domain_search(self, params: DomainSearchParams) -> ApiResponse:
        response = self.client.domain_search(
            domain=params.domain,
            company=params.company,
            limit=params.limit,
            offset=params.offset,
            type_filter=params.type,
            seniority=params.seniority,
            department=params.department,
            required_field=params.required_field
        )
        
        if not response:
            raise ValueError("Empty response received from Hunter.io API")
            
        domain_search_result = DomainSearchResult(**response.get("data", {}))
        return self.prepare_response(domain_search_result, "DomainSearchResultView")
    
    def email_finder(self, params: EmailFinderParams) -> ApiResponse:
        response = self.client.email_finder(
            domain=params.domain,
            company=params.company,
            first_name=params.first_name,
            last_name=params.last_name,
            full_name=params.full_name,
            max_duration=params.max_duration
        )
        
        if not response:
            raise ValueError("Empty response received from Hunter.io API")
            
        email_finder_result = EmailFinderResult(**response.get("data", {}))
        return self.prepare_response(email_finder_result, "EmailFinderResultView")
    
    def email_verifier(self, params: EmailVerifierParams) -> ApiResponse:
        response = self.client.email_verifier(email=params.email)
        
        if not response:
            raise ValueError("Empty response received from Hunter.io API")
            
        email_verifier_result = EmailVerifierResult(**response.get("data", {}))
        return self.prepare_response(email_verifier_result, "EmailVerifierResultView")
    
    def email_count(self, params: EmailCountParams) -> ApiResponse:
        response = self.client.email_count(
            domain=params.domain,
            company=params.company,
            type_filter=params.type
        )
        
        if not response:
            raise ValueError("Empty response received from Hunter.io API")
            
        email_count_result = EmailCountResult(**response.get("data", {}))
        return self.prepare_response(email_count_result, "EmailCountResultView")
    
    def email_enrichment(self, params: EmailEnrichmentParams) -> ApiResponse:
        response = self.client.email_enrichment(
            email=params.email,
            clearbit_format=params.clearbit_format
        )
        
        if not response:
            raise ValueError("Empty response received from Hunter.io API")
            
        email_enrichment_result = EmailEnrichmentResult(**response.get("data", {}))
        return self.prepare_response(email_enrichment_result, "EmailEnrichmentResultView")
    
    def company_enrichment(self, params: CompanyEnrichmentParams) -> ApiResponse:
        response = self.client.company_enrichment(
            domain=params.domain,
            clearbit_format=params.clearbit_format
        )
        
        if not response:
            raise ValueError("Empty response received from Hunter.io API")
            
        company_enrichment_result = CompanyEnrichmentResult(**response.get("data", {}))
        return self.prepare_response(company_enrichment_result, "CompanyEnrichmentResultView")
    
    def combined_enrichment(self, params: CombinedEnrichmentParams) -> ApiResponse:
        response = self.client.combined_enrichment(
            email=params.email,
            clearbit_format=params.clearbit_format
        )
        
        if not response:
            raise ValueError("Empty response received from Hunter.io API")
            
        combined_enrichment_result = CombinedEnrichmentResult(**response.get("data", {}))
        return self.prepare_response(combined_enrichment_result, "CombinedEnrichmentResultView")
    
    def account_information(self) -> ApiResponse:
        response = self.client.account_information()
        
        if not response:
            raise ValueError("Empty response received from Hunter.io API")
            
        account_information_result = AccountInformationResult(**response.get("data", {}))
        return self.prepare_response(account_information_result, "AccountInformationResultView") 