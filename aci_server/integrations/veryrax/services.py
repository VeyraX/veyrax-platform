from typing import Optional, Dict, Any
from .client import VeryraxMemoryClient
from .schema import (
    SaveMemoryResponse, GetMemoriesResponse, UpdateMemoryResponse, 
    DeleteMemoryResponse, ApiResponse, MemoryList, MemoryItem, SaveMemoryParams
)

class VeryraxMemoryService:
    def __init__(self, client: VeryraxMemoryClient):
        self.client = client
        
    def save_memory(self, memory: str, tool: Optional[str] = None) -> ApiResponse:
        print("SERVICE SAVE_MEMORY CALLED WITH:", memory, tool)
        result = self.client.save_memory(memory, tool)
        print("CLIENT RETURNED:", result)
        response_data = SaveMemoryResponse(**result)
        print("RESPONSE DATA:", response_data)
        
        return ApiResponse(data=response_data)
    
    def get_memories(self, tool: Optional[str] = None, limit: int = 50, offset: int = 0) -> ApiResponse:
        result = self.client.get_memories(tool, limit, offset)
        
        memory_items = [MemoryItem(**item) for item in result["items"]]
        memory_list = MemoryList(items=memory_items, count=result["count"])
        
        return ApiResponse(data=memory_list)
    
    def update_memory(self, id: str, memory: Optional[str] = None, tool: Optional[str] = None) -> ApiResponse:
        result = self.client.update_memory(id, memory, tool)
        response_data = UpdateMemoryResponse(**result)
        
        return ApiResponse(data=response_data)
    
    def delete_memory(self, id: str) -> ApiResponse:
        result = self.client.delete_memory(id)
        response_data = DeleteMemoryResponse(**result)
        
        return ApiResponse(data=response_data)
