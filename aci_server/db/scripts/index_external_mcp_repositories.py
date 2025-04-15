import os
from upstash_vector import Index, Vector
from openai import OpenAI
from dotenv import load_dotenv
import sys
from pathlib import Path

# Add parent directory to Python path to allow imports
sys.path.append(str(Path(__file__).parent.parent.parent))
from db.supabase import get_supabase
# Load environment variables at the start
load_dotenv()

# Debug print
print("Environment variables:")
print(f"SUPABASE_URL: {os.getenv('SUPABASE_URL')}")
print(f"SUPABASE_SERVICE_KEY: {os.getenv('SUPABASE_SERVICE_KEY')}")
print(f"UPSTASH_EXTERNAL_MCP_URL: {os.getenv('UPSTASH_EXTERNAL_MCP_URL')}")
print(f"UPSTASH_EXTERNAL_MCP_TOKEN: {os.getenv('UPSTASH_EXTERNAL_MCP_TOKEN')}")

def get_vector_index():
    url = os.getenv("UPSTASH_EXTERNAL_MCP_URL")
    token = os.getenv("UPSTASH_EXTERNAL_MCP_TOKEN")
    if not url or not token:
        raise ValueError("Missing Upstash Vector credentials for external MCP")
    return Index(url=url, token=token)

def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Missing OpenAI API key")
    return OpenAI(api_key=api_key)

def create_repository_text(repo: dict) -> str:
    # Create a text representation of the repository for embedding
    metadata = repo['metadata']
    text = f"{repo['name']}\n"
    
    if metadata.get('short_description'):
        text += f"{metadata['short_description']}\n"
    
    if metadata.get('ai_generated_description'):
        text += f"{metadata['ai_generated_description']}\n"
    
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

def main():
    supabase = get_supabase()
    vector_index = get_vector_index()
    openai_client = get_openai_client()
    
    print("Purging existing index...")
    purge_index(vector_index)
    
    print("Fetching external MCP repositories from Supabase...")
    repos_data = supabase.table("external_mcp_repositories").select(
        "id",
        "name",
        "metadata",
        "created_at"
    ).execute()
    
    repositories = repos_data.data
    
    print(f"Creating embeddings for {len(repositories)} repositories...")
    vectors = []
    batch_size = 100
    total_indexed = 0
    
    for i, repo in enumerate(repositories, 1):
        text = create_repository_text(repo)
        
        embedding = get_embedding(openai_client, text)
        
        vector = Vector(
            id=str(repo['id']),
            vector=embedding,
            metadata={
                "id": str(repo['id']),
                "name": repo['name'],
                "created_at": repo['created_at'],
                **repo['metadata']  # Include all metadata fields
            }
        )
        vectors.append(vector)
        
        # Print progress every 10 items
        if i % 10 == 0:
            print(f"Progress: {i}/{len(repositories)} repositories processed")
        
        # Upsert in batches of 100 to avoid memory issues and get progress faster
        if len(vectors) >= batch_size or i == len(repositories):
            print(f"Upserting batch {total_indexed//batch_size + 1} to index ({len(vectors)} vectors)...")
            vector_index.upsert(vectors=vectors)
            total_indexed += len(vectors)
            vectors = []  # Clear the vectors list after upserting
    
    print(f"Successfully indexed {total_indexed} repositories")

if __name__ == "__main__":
    main() 