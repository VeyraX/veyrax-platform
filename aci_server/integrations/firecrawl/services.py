from typing import Optional, Dict, Any, List, Union
from .client import FirecrawlClient
from .schema import (
    ScrapeParams,
    BatchScrapeParams,
    CrawlParams,
    MapParams,
    ExtractParams,
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
import os
from ..common.component_handler import load_components, prepare_components_auto

class FirecrawlService:
    def __init__(self, client: FirecrawlClient):
        self.client = client
        self.components_data = self._load_components()
    
    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
    
    def prepare_response(self, data: Any, component_name: str = None) -> ApiResponse:
        tool_name = "firecrawl"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data)
    
    def _convert_schema_to_json_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        if not schema or not isinstance(schema, dict):
            return schema
            
        schema_properties = {}
        for key, value in schema.items():
            if value == 'string' or value == '':
                schema_properties[key] = {"type": "string"}
            elif value == 'number' or value == 'integer':
                schema_properties[key] = {"type": value}
            elif value == 'boolean':
                schema_properties[key] = {"type": "boolean"}
            elif value == 'array':
                schema_properties[key] = {"type": "array", "items": {"type": "string"}}
            elif value == 'object':
                schema_properties[key] = {"type": "object"}
            else:
                schema_properties[key] = value
        
        return {
            "type": "object",
            "properties": schema_properties,
            "required": list(schema_properties.keys())
        }
    
    def scrape(self, params: ScrapeParams) -> ApiResponse:
        response = self.client.scrape(**params.dict(exclude_none=True))
        return ApiResponse(data=response)
    
    def batch_scrape(self, params: BatchScrapeParams) -> ApiResponse:
        response = self.client.batch_scrape(**params.dict(exclude_none=True))
        return ApiResponse(data=response)
    
    def get_batch_status(self, batch_id: str) -> ApiResponse:
        response = self.client.get_batch_status(batch_id)
        return ApiResponse(data=response)
    
    def get_batch_errors(self, batch_id: str) -> ApiResponse:
        response = self.client.get_batch_errors(batch_id)
        return ApiResponse(data=response)

    def crawl(self, params: CrawlParams) -> ApiResponse:
        response = self.client.crawl(**params.dict(exclude_none=True))
        return ApiResponse(data=response)

    def get_crawl_status(self, crawl_id: str) -> ApiResponse:
        response = self.client.get_crawl_status(crawl_id)
        return ApiResponse(data=response)

    def cancel_crawl(self, crawl_id: str) -> ApiResponse:
        response = self.client.cancel_crawl(crawl_id)
        return ApiResponse(data=response)

    def get_crawl_errors(self, crawl_id: str) -> ApiResponse:
        response = self.client.get_crawl_errors(crawl_id)
        return ApiResponse(data=response)

    def map_site(self, params: MapParams) -> ApiResponse:
        response = self.client.map_site(**params.dict(exclude_none=True))
        return ApiResponse(data=response)

    def extract(self, params: ExtractParams) -> ApiResponse:
        params_dict = params.dict(exclude_none=True)
        
        if 'schema' in params_dict:
            params_dict['schema'] = self._convert_schema_to_json_schema(params_dict['schema'])
        
        print(params_dict)
        response = self.client.extract(**params_dict)
        return ApiResponse(data=response)

    def get_extract_status(self, extract_id: str) -> ApiResponse:
        response = self.client.get_extract_status(extract_id)
        return ApiResponse(data=response)

    def search(self, params: SearchParams) -> ApiResponse:
        response = self.client.search(**params.dict(exclude_none=True))
        return ApiResponse(data=response)

    def get_credit_usage(self) -> ApiResponse:
        response = self.client.get_credit_usage()
        return ApiResponse(data=response)
