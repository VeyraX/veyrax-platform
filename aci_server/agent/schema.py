from typing import Optional
from pydantic import BaseModel


class AgentQueryRequest(BaseModel):
    query: str
    custom_instructions: Optional[str] = None

class AgentResponse(BaseModel):
    status: str
    response: Optional[str] = None
    error: Optional[str] = None
    details: Optional[str] = None