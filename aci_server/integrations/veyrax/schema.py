from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field

class SaveMemoryParams(BaseModel):
    memory: str = Field(..., description="Text to save in memory")
    tool: Optional[str] = Field(None, description="Tool name (optional)")

    class Config:
        extra = "ignore"

class GetMemoriesParams(BaseModel):
    tool: Optional[str] = Field(None, description="Filter by tool name")
    limit: Optional[int] = Field(50, description="Maximum number of memories to return")
    offset: Optional[int] = Field(0, description="Number of memories to skip")

class UpdateMemoryParams(BaseModel):
    id: Union[str, int] = Field(..., description="Memory ID to update")
    memory: Optional[str] = Field(None, description="New text for the memory")
    tool: Optional[str] = Field(None, description="New tool name")

class DeleteMemoryParams(BaseModel):
    id: Union[str, int] = Field(..., description="Memory ID to delete")

class MemoryItem(BaseModel):
    id: Union[str, int]
    memory: str
    tool: Optional[str] = None
    user_id: str
    created_at: Optional[str] = None

class MemoryList(BaseModel):
    items: List[MemoryItem]
    count: int

class SaveMemoryResponse(BaseModel):
    success: bool
    message: str
    id: Optional[Union[str, int]] = None

class GetMemoriesResponse(BaseModel):
    data: MemoryList
    message: Optional[str] = None

class UpdateMemoryResponse(BaseModel):
    success: bool
    message: str
    id: Union[str, int]

class DeleteMemoryResponse(BaseModel):
    success: bool
    message: str
    id: Union[str, int]

class ApiResponse(BaseModel):
    data: Any
    component: Optional[Dict[str, Any]] = None
