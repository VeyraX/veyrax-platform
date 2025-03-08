from db.supabase import get_supabase
from typing import Dict, List, Optional

async def get_user_memories(user_id: str, limit: Optional[int] = None) -> Dict[str, List[str]]:
    try:
        supabase = get_supabase()
        
        query = supabase.table('users_memory') \
            .select('memory,tool') \
            .eq('user_id', user_id)
            
        if limit is not None:
            query = query.limit(limit)
            
        result = query.execute()
        
        memories_by_tool = {}
        
        for item in result.data:
            tool = item.get('tool') or 'general'
            memory = item.get('memory')
            
            if memory:
                if tool not in memories_by_tool:
                    memories_by_tool[tool] = []
                memories_by_tool[tool].append(memory)
        
        return memories_by_tool
        
    except Exception as e:
        print(f"Error retrieving user memories: {str(e)}")
        return {}
