from db.supabase import get_supabase
from typing import Dict, Any, Optional, List
import uuid
from datetime import datetime
import os
from upstash_vector import Index, Vector
from openai import OpenAI

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
    build_logs: str = None
) -> Dict[str, Any]:
    try:
        supabase = get_supabase()
        
        update_data = {
            "status": status,
            "build_logs": build_logs,
        }
            
        result = supabase.table('mcp_repository_deployments') \
            .update(update_data) \
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
        return False

async def get_mcp_repositories(repo_ids: List[str] = None) -> List[Dict[str, Any]]:
    try:
        supabase = get_supabase()
        
        query = supabase.table('mcp_repositories').select('id, image_name, input_schema').eq('is_approved', True)
        
        if repo_ids:
            query = query.in_('id', repo_ids)
        
        result = query.execute()
        
        if not result.data:
            return []
            
        return result.data
        
    except Exception as e:
        return []

async def get_user_connected_repo_ids(user_id: str) -> List[str]:
    try:
        supabase = get_supabase()
        
        result = supabase.table('users_mcp') \
            .select('repo_id') \
            .eq('user_id', user_id) \
            .eq('status', 'connected') \
            .execute()
        
        if not result.data:
            return []
        
        return [item["repo_id"] for item in result.data]
        
    except Exception as e:
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
        return {}

async def update_users_mcp_status_by_deployment_id(deployment_id: str, status: str) -> bool:
    try:
        supabase = get_supabase()
        
        deploy_result = supabase.table('mcp_repository_deployments') \
            .select('repo_id') \
            .eq("deployment_id", deployment_id) \
            .execute()
        
        if not deploy_result.data or len(deploy_result.data) == 0:
            return False
            
        repo_id = deploy_result.data[0].get("repo_id")
        if not repo_id:
            return False
            
        users_result = supabase.table('users_mcp') \
            .select('user_id') \
            .eq("repo_id", repo_id) \
            .execute()
        
        if not users_result.data or len(users_result.data) == 0:
            return False
            
        for user_data in users_result.data:
            user_id = user_data.get("user_id")
            if user_id:
                supabase.table('users_mcp') \
                    .update({"status": status}) \
                    .eq("user_id", user_id) \
                    .eq("repo_id", repo_id) \
                    .execute()
        
        return True
        
    except Exception as e:
        return False

async def add_repository_to_providers_index(repo_id: str) -> Dict[str, Any]:
    try:
        supabase = get_supabase()
        
        result = supabase.table('mcp_repositories') \
            .select('id, name, description, created_at, image_name, repo_url, input_schema') \
            .eq('id', repo_id) \
            .limit(1) \
            .execute()
            
        if not result.data or len(result.data) == 0:
            return {"error": "Repository not found"}
            
        repo = result.data[0]
        
        text = f"{repo.get('name', '')}\n"
        if repo.get('description'):
            text += f"{repo.get('description')}\n"
        if repo.get('image_name'):
            text += f"{repo.get('image_name')}\n"
            
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return {"error": "Missing OpenAI API key"}
        openai_client = OpenAI(api_key=api_key)
        
        embedding_response = openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        embedding = embedding_response.data[0].embedding
        
        url = os.getenv("UPSTASH_PROVIDERS_URL")
        token = os.getenv("UPSTASH_PROVIDERS_TOKEN")
        if not url or not token:
            return {"error": "Missing Upstash Vector credentials for Providers index"}
        vector_index = Index(url=url, token=token)
        
        check_result = vector_index.query(
            vector=embedding,
            top_k=1,
            include_metadata=True,
            filter=f"repo_id = '{str(repo_id)}' AND type = 'mcp_repository'"
        )
        
        if check_result and check_result.matches and len(check_result.matches) > 0:
            return {"success": True, "message": f"Repository {repo_id} already exists in Providers index"}
        
        vector = Vector(
            id=str(repo['id']),
            vector=embedding,
            metadata={
                "repo_id": str(repo['id']),
                "name": repo.get('name', ''),
                "description": repo.get('description', ''),
                "created_at": str(repo.get('created_at', '')),
                "image_name": repo.get('image_name', ''),
                "repo_url": repo.get('repo_url', ''),
                "type": "mcp_repository"
            }
        )
        
        vector_index.upsert(vectors=[vector])
        
        return {"success": True, "message": f"Repository {repo_id} added to Providers index"}
        
    except Exception as e:
        return {"error": str(e)}

async def get_repo_id_from_deployment(deployment_id: str) -> Optional[str]:
    try:
        supabase = get_supabase()
        deployment_result = supabase.table('mcp_repository_deployments') \
            .select('repo_id') \
            .eq("deployment_id", deployment_id) \
            .limit(1) \
            .execute()
            
        if deployment_result.data and len(deployment_result.data) > 0:
            return deployment_result.data[0].get("repo_id")
            
        return None
        
    except Exception as e:
        return f'Error getting repo_id from deployment: {str(e)}'