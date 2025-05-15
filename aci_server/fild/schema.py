from pydantic import BaseModel
from typing import Dict, Any, List, Optional, Union


class AgentRequest(BaseModel):
    query: str

class AgentResponse(BaseModel):
    query: str
    result: str
    success: bool
    payload: Optional[List[Dict[str, Any]]] = None
