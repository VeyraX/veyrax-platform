from typing import Dict, Any
from .client import PerplexityClient
from .schema import CompletionRequest, CompletionResponse

class PerplexityService:
    def __init__(self, client: PerplexityClient):
        self.client = client
        
    def create_completion(self, request: CompletionRequest) -> CompletionResponse:
        response = self.client.create_completion(**request.model_dump())
        return CompletionResponse(**response)