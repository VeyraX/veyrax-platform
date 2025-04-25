import os
from upstash_vector import Index, Vector
from openai import OpenAI
from db.supabase import get_supabase
import sentry_sdk
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

def get_vector_index():
    url = os.getenv("UPSTASH_PROVIDERS_URL")
    token = os.getenv("UPSTASH_PROVIDERS_TOKEN")
    if not url or not token:
        raise ValueError("Missing Upstash Vector credentials")
    return Index(url=url, token=token)

def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Missing OpenAI API key")
    return OpenAI(api_key=api_key)

async def get_user_tools_with_vector_search(user_id: str, query: str, top_k: int = 4) -> Dict[str, Any]:
    try:
        supabase = get_supabase()
        vector_index = get_vector_index()
        openai_client = get_openai_client()
        
        response = openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=query
        )
        query_embedding = response.data[0].embedding
        
        user_providers = supabase.table('users_providers') \
            .select('provider_id') \
            .eq('user_id', user_id) \
            .execute()
            
        if not user_providers.data:
            return {}
            
        provider_ids = [f"'{str(item['provider_id'])}'" for item in user_providers.data]
        filter_condition = f"provider_id IN ({','.join(provider_ids)})"
        
        vector_results = vector_index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            include_vectors=False,
            filter=filter_condition
        )
        
        if not vector_results:
            return {}
        
        matched_provider_ids = []
        provider_scores = {}
        
        for result in vector_results:
            if hasattr(result, 'metadata') and result.metadata and 'provider_id' in result.metadata:
                provider_id = str(result.metadata['provider_id'])
                matched_provider_ids.append(provider_id)
                provider_scores[provider_id] = result.score
        
        if not matched_provider_ids:
            return {}
        
        actions = supabase.from_('user_actions_view') \
            .select('*') \
            .eq('user_id', user_id) \
            .in_('provider_id', matched_provider_ids) \
            .execute()
            
        if not actions.data:
            return {}
        
        user_tools = {}
        
        for row in actions.data:
            provider_name = row.get('provider_tag')
            action_name = row.get('action_slug')
            input_schema = row.get('input_schema')
            provider_id = str(row.get('provider_id'))
            
            if not provider_name or not action_name or not input_schema:
                continue
            
            if provider_name not in user_tools:
                user_tools[provider_name] = {"__score": provider_scores.get(provider_id, 0), "actions": {}}
            
            action_schema = {
                "type": "function",
                "function": {
                    "name": action_name,
                    **input_schema
                }
            }
            
            user_tools[provider_name]["actions"][action_name] = action_schema
        
        result = {}
        for provider_name, provider_data in user_tools.items():
            score = provider_data["__score"]
            actions = provider_data["actions"]
            
            result[provider_name] = {
                "__score": score,
                **actions
            }
        
        return result
        
    except Exception as e:
        print(f"Error in get_user_tools_with_vector_search: {str(e)}")
        sentry_sdk.capture_exception(e)
        return {"error": str(e)}

async def get_user_mcp_repositories_with_vector_search(user_id: str, query: str, top_k: int = 4) -> Dict[str, Any]:
    try:
        supabase = get_supabase()
        vector_index = get_vector_index()
        openai_client = get_openai_client()
        
        response = openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=query
        )
        query_embedding = response.data[0].embedding
        
        user_repos = supabase.table('users_mcp') \
            .select('repo_id') \
            .eq('user_id', user_id) \
            .eq('status', 'connected') \
            .execute()
            
        if not user_repos.data:
            return {}
            
        repo_ids = [f"'{str(item['repo_id'])}'" for item in user_repos.data]
        filter_condition = f"type = 'mcp_repository' AND repo_id IN ({','.join(repo_ids)})"
        
        vector_results = vector_index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            include_vectors=False,
            filter=filter_condition
        )
        
        if not vector_results:
            return {}
        
        matched_repo_ids = []
        repo_scores = {}
        
        for result in vector_results:
            if hasattr(result, 'metadata') and result.metadata and 'repo_id' in result.metadata:
                repo_id = str(result.metadata['repo_id'])
                matched_repo_ids.append(repo_id)
                repo_scores[repo_id] = result.score
        
        if not matched_repo_ids:
            return {}
            
        repo_data = supabase.table('mcp_repositories') \
            .select('id, image_name, input_schema') \
            .in_('id', matched_repo_ids) \
            .execute()
            
        if not repo_data.data:
            return {}
            
        repo_lookup = {str(repo['id']): repo for repo in repo_data.data}
        
        user_mcp_tools = {}
        
        for repo in repo_data.data:
            repo_id = str(repo.get('id'))
            image_name = repo.get('image_name')
            input_schema = repo.get('input_schema')
            
            if not repo_id or not image_name or not input_schema or repo_id not in repo_scores:
                continue
                
            user_mcp_tools[image_name] = {
                "__score": repo_scores[repo_id],
                "input_schema": input_schema
            }
        
        return user_mcp_tools
        
    except Exception as e:
        print(f"Error in get_user_mcp_repositories_with_vector_search: {str(e)}")
        sentry_sdk.capture_exception(e)
        return {"error": str(e)}

async def get_user_combined_tools_with_vector_search(user_id: str, query: str, top_k: int = 4) -> Dict[str, Any]:
    try:
        provider_tools = await get_user_tools_with_vector_search(user_id, query, top_k * 2)
        mcp_tools = await get_user_mcp_repositories_with_vector_search(user_id, query, top_k * 2)
        
        all_items = []
        
        for provider, provider_data in provider_tools.items():
            if "__score" not in provider_data:
                continue
                
            provider_score = provider_data["__score"]
            all_items.append(("provider:" + provider, provider_score, provider_data))
        
        for image_name, repo_data in mcp_tools.items():
            if "__score" not in repo_data:
                continue
                
            repo_score = repo_data["__score"]
            all_items.append(("mcp:" + image_name, repo_score, repo_data))
        
        all_items.sort(key=lambda x: x[1], reverse=True)
        
        top_items = all_items[:top_k]
        
        result = {}
        
        for key, score, data in top_items:
            key_type, name = key.split(":", 1)
            
            if key_type == "provider":
                provider_result = {k: v for k, v in data.items() if k != "__score"}
                result[name] = provider_result
            else:
                repo_result = {k: v for k, v in data.items() if k != "__score"}
                result[name] = repo_result
        
        return result
        
    except Exception as e:
        print(f"Error in get_user_combined_tools_with_vector_search: {str(e)}")
        sentry_sdk.capture_exception(e)
        return {"error": str(e)}
