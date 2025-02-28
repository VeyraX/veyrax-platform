from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union

class Message(BaseModel):
    role: str
    content: str

class CompletionRequest(BaseModel):
    messages: List[Message]
    model: str = "sonar"
    max_tokens: Optional[int] = 1024
    temperature: float = 0.4
    top_p: float = 0.9
    search_domain_filter: Optional[str] = None
    return_images: bool = False
    return_related_questions: bool = False
    search_recency_filter: Optional[str] = None
    top_k: int = 5
    stream: bool = False
    presence_penalty: Optional[float] = 0
    frequency_penalty: Optional[float] = 1
    response_format: Optional[str] = None

class CompletionResponse(BaseModel):
    id: str
    model: str
    object: str
    created: int
    citations: List[str]
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]
    component: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None

class ApiResponse(BaseModel):
    data: CompletionResponse
    component: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None

# Response schema class
class CompletionResponseSchema(BaseModel):
    data: CompletionResponse
    message: Optional[str] = None