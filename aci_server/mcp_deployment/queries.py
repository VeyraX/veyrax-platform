from db.supabase import get_supabase
from typing import Dict, Any, Optional, List
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

async def get_cached_dockerfile(
    repository_id: str,
    commit_hash: str
) -> Dict[str, Any]:
    try:
        supabase = get_supabase()
        
        result = supabase.table('mcp_repositories') \
            .select('id, docker_file_b64') \
            .eq('id', repository_id) \
            .eq('last_commit_hash', commit_hash) \
            .limit(1) \
            .execute()
            
        if result.data and len(result.data) > 0:
            return {
                'docker_file_b64': result.data[0].get('docker_file_b64')
            }
            
        return {}
        
    except Exception as e:
        print(f"Error getting cached dockerfile: {str(e)}")
        return {}

async def save_dockerfile(
    repository_id: str,
    commit_hash: str,
    docker_file_b64: str
) -> bool:
    try:
        supabase = get_supabase()
        
        result = supabase.table('mcp_repositories') \
            .update({
                'docker_file_b64': docker_file_b64,
                'last_commit_hash': commit_hash
            }) \
            .eq('id', repository_id) \
            .execute()
        
        return True
        
    except Exception as e:
        print(f"Error saving dockerfile: {str(e)}")
        return False

async def get_mcp_repositories(repo_ids: List[str] = None) -> List[Dict[str, Any]]:
    try:
        supabase = get_supabase()
        
        query = supabase.table('mcp_repositories').select('id, image_name, input_schema')
        
        if repo_ids:
            query = query.in_('id', repo_ids)
        
        result = query.execute()
        
        if not result.data:
            return []
            
        return result.data
        
    except Exception as e:
        print(f"Error getting MCP repositories: {str(e)}")
        return []

async def get_user_connected_repo_ids(user_id: str) -> List[str]:
    try:
        supabase = get_supabase()
        
        result = supabase.table('users_mcp') \
            .select('repo_id') \
            .eq('user_id', user_id) \
            .execute()
        
        if not result.data:
            return []
        
        return [item["repo_id"] for item in result.data]
        
    except Exception as e:
        print(f"Error getting user connected repo IDs: {str(e)}")
        return []

async def get_user_mcp_image_names(user_id: str) -> List[str]:
    try:
        repo_ids = await get_user_connected_repo_ids(user_id)
        
        if not repo_ids:
            return []
        
        repos = await get_mcp_repositories(repo_ids)
        
        if not repos:
            return []
        
        return [repo["image_name"] for repo in repos]
        
    except Exception as e:
        print(f"Error getting user MCP image names: {str(e)}")
        return []

async def get_user_connected_mcp_actions(user_id: str) -> Dict[str, Any]:
    try:
        repo_ids = await get_user_connected_repo_ids(user_id)
        
        if not repo_ids:
            return {}
        
        repos = await get_mcp_repositories(repo_ids)
        
        if not repos:
            return {}
        
        connected_repos = {}
        for repo in repos:
            image_name = repo["image_name"]
            input_schema = repo["input_schema"]
            connected_repos[image_name] = input_schema
        
        return connected_repos
        
    except Exception as e:
        print(f"Error getting user connected MCP actions: {str(e)}")
        return {}