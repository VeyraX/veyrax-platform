from db.supabase import get_supabase
from fastapi import HTTPException
from typing import List, Dict, Any, Optional

class VeyraxMemoryClient:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.supabase = get_supabase()
    
    def save_memory(self, memory: str, tool: str = None) -> dict:
        data = {
            "memory": memory,
            "user_id": self.user_id
        }
        
        if tool:
            data["tool"] = tool
            
        result = self.supabase.table('users_memory').insert(data).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to save memory")
            
        return {
            "success": True,
            "message": "Memory saved successfully",
            "id": result.data[0].get('id')
        }
    
    def get_memories(self, tool: Optional[str] = None, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        query = self.supabase.table('users_memory').select('*').eq('user_id', self.user_id)
        
        if tool:
            query = query.eq('tool', tool)
            
        count_query = query
        count_result = count_query.execute()
        total_count = len(count_result.data)
        
        query = query.order('created_at', desc=True).limit(limit).offset(offset)
        result = query.execute()
        
        if result.data is None:
            return {"items": [], "count": 0}
            
        return {
            "items": result.data,
            "count": total_count
        }
    
    def update_memory(self, id: str, memory: Optional[str] = None, tool: Optional[str] = None) -> Dict[str, Any]:
        check_query = self.supabase.table('users_memory').select('id').eq('id', id).eq('user_id', self.user_id)
        check_result = check_query.execute()
        
        if not check_result.data:
            raise HTTPException(status_code=404, detail=f"Memory with ID {id} not found or access denied")
        
        update_data = {}
        if memory is not None:
            update_data["memory"] = memory
        if tool is not None:
            update_data["tool"] = tool
            
        if not update_data:
            return {
                "success": True,
                "message": "No changes to update",
                "id": id
            }
            
        result = self.supabase.table('users_memory').update(update_data).eq('id', id).eq('user_id', self.user_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to update memory")
            
        return {
            "success": True,
            "message": "Memory updated successfully",
            "id": id
        }
    
    def delete_memory(self, id: str) -> Dict[str, Any]:
        check_query = self.supabase.table('users_memory').select('id').eq('id', id).eq('user_id', self.user_id)
        check_result = check_query.execute()
        
        if not check_result.data:
            raise HTTPException(status_code=404, detail=f"Memory with ID {id} not found or access denied")
        
        result = self.supabase.table('users_memory').delete().eq('id', id).eq('user_id', self.user_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to delete memory")
            
        return {
            "success": True,
            "message": "Memory deleted successfully",
            "id": id
        }
