from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Union


class AgentRequest(BaseModel):
    query: str

class ExtractedValue(BaseModel):
    value: str
    reasoning: str

class AgentResponse(BaseModel):
    query: str
    result: str
    success: bool
    payload: Optional[List[Dict[str, Any]]] = None

class WaterfallRequest(BaseModel):
    sheet_id: str
    query: str
    row_indexes: Optional[List[int]] = None
    row_range: Optional[Dict[str, int]] = None
    column_ids: List[int]

class WaterfallResponse(BaseModel):
    success: bool
    message: str
    process_details: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
