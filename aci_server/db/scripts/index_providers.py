import os
from upstash_vector import Index, Vector
from openai import OpenAI
from dotenv import load_dotenv
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from db.supabase import get_supabase
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

def create_provider_text(provider: dict) -> str:
    # Create a text representation of the provider for embedding
    text = f"{provider['name']}\n{provider['description']}\n"
    text += f"Tag: {provider['provider_tag']}\n"
    text += f"Auth method: {provider['auth_method']}\n"
    if provider.get('scopes'):
        text += "Scopes:\n"
        for scope in provider['scopes']:
            text += f"- {scope['scope_name']} ({scope['scope']})\n"
    return text

def get_embedding(client: OpenAI, text: str) -> list[float]:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

def purge_index(index: Index):
    batch_size = 1000
    offset = 0
    total_purged = 0
    
    while True:
        result = index.query(
            vector=[0] * 1536,
            top_k=batch_size, 
            include_metadata=False
        )
        
        if not result or not result.matches:
            break
            
        vector_ids = [match.id for match in result.matches]
        if vector_ids:
            index.delete(ids=vector_ids)
            total_purged += len(vector_ids)
            print(f"Purged batch of {len(vector_ids)} vectors")
        
        if len(vector_ids) < batch_size:
            break
            
    print(f"Index purge completed. Total vectors purged: {total_purged}")

def create_repository_text(repo: dict) -> str:
    # Create a text representation of the MCP repository for embedding
    text = f"{repo.get('name', '')}\n"
    if repo.get('description'):
        text += f"{repo.get('description')}\n"
    if repo.get('image_name'):
        text += f"{repo.get('image_name')}\n"
    return text

def main():
    supabase = get_supabase()
    vector_index = get_vector_index()
    openai_client = get_openai_client()
    
    print("Purging existing index...")
    purge_index(vector_index)
    
    print("Fetching providers from Supabase...")
    providers_data = supabase.table("providers").select(
        "id",
        "name",
        "description",
        "logo_url",
        "created_at",
        "provider_tag",
        "auth_method",
        "has_index_capability",
        "scopes",
        "is_enabled"
    ).execute()
    
    providers = providers_data.data
    
    print(f"Creating embeddings for {len(providers)} providers...")
    vectors = []
    for i, provider in enumerate(providers, 1):
        text = create_provider_text(provider)
        
        embedding = get_embedding(openai_client, text)
        
        vector = Vector(
            id=str(provider['id']),
            vector=embedding,
            metadata={
                "provider_id": str(provider['id']),
                "name": provider['name'],
                "description": provider['description'],
                "provider_tag": provider['provider_tag'],
                "auth_method": provider['auth_method'],
                "has_index_capability": provider.get('has_index_capability', False),
                "is_enabled": provider.get('is_enabled', True),
                "type": "provider"  # Adding type to distinguish between providers and repositories
            }
        )
        vectors.append(vector)
        print(f"Progress: {i}/{len(providers)} providers processed")
    
    repositories_data = supabase.table("mcp_repositories").select(
        "id",
        "name",
        "description",
        "created_at",
        "image_name",
        "repo_url",
        "is_approved"
    ).execute()
    
    repositories = repositories_data.data
    
    print(f"Creating embeddings for {len(repositories)} MCP repositories...")
    for i, repo in enumerate(repositories, 1):
        text = create_repository_text(repo)
        
        embedding = get_embedding(openai_client, text)
        
        vector = Vector(
            id=str(repo['id']), 
            vector=embedding,
            metadata={
                "repo_id": str(repo['id']),
                "name": repo.get('name', ''),
                "description": repo.get('description', ''),
                "created_at": repo.get('created_at', ''),
                "image_name": repo.get('image_name', ''),
                "repo_url": repo.get('repo_url', ''),
                "type": "mcp_repository"
            }
        )
        vectors.append(vector)
        print(f"Progress: {i}/{len(repositories)} repositories processed")
    
    print(f"Upserting {len(vectors)} vectors to index...")
    vector_index.upsert(vectors=vectors)
    print(f"Successfully indexed {len(vectors)} items ({len(providers)} providers and {len(repositories)} repositories)")

if __name__ == "__main__":
    main() 