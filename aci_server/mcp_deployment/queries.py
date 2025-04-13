from db.supabase import get_supabase
from typing import Dict, Any, Optional
import uuid

async def create_mcp_deployment_record(
    repository_id: str,
    commit_hash: Optional[str] = None,
    status: str = "started"
) -> Dict[str, Any]:
    try:
        supabase = get_supabase()
        
        deployment_id = str(uuid.uuid4())
        
        data = {
            "repo_id": repository_id,
            "status": status,
            "deployment_id": deployment_id
        }
        
        if commit_hash:
            data["commit_hash"] = commit_hash
        
        result = supabase.table('mcp_repository_deployments').insert(data).execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]
        
        return {"error": "Failed to create deployment record"}
        
    except Exception as e:
        return {"error": str(e)}

async def update_mcp_deployment_status(
    deployment_id: str,
    status: str,
    error: Optional[str] = None,
    build_logs: Optional[str] = None
) -> Dict[str, Any]:
    try:
        supabase = get_supabase()
        
        data = {"status": status}
        
        if error:
            data["error"] = error
            
        if build_logs:
            data["build_logs"] = build_logs
        
        result = supabase.table('mcp_repository_deployments') \
            .update(data) \
            .eq("deployment_id", deployment_id) \
            .execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]
        
        return {"error": "Failed to update deployment status"}
        
    except Exception as e:
        return {"error": str(e)}
