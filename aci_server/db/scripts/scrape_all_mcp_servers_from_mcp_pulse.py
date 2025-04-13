import httpx
import asyncio
import sys
import os
from pydantic import BaseModel
from typing import List, Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from db.supabase import get_supabase
from aci_server.mcp_deployment.schema import ExternalMCPResponse

class AppendAllServersResponse(BaseModel):
    total_added: int
    skipped: int
    message: str

async def append_all_servers():
    try:
        api_url = "https://api.pulsemcp.com/v0beta/servers"
        added_count = 0
        skipped_count = 0
        no_source_code_count = 0
        supabase = get_supabase()
        
        print("Starting to fetch and process MCP servers...")
        
        async with httpx.AsyncClient(
            headers={"User-Agent": "VeyraX/1.0 (https://veyrax.com)"}
        ) as client:
            next_url = api_url
            while next_url:
                print(f"Fetching data from: {next_url}")
                response = await client.get(next_url, timeout=30.0)
                
                if response.status_code != 200:
                    error_detail = f"External API error: {response.status_code} - {response.text}"
                    print(f"Error: {error_detail}")
                    return
                
                data = ExternalMCPResponse.parse_obj(response.json())
                print(f"Fetched {len(data.servers)} servers")
                
                for server in data.servers:
                    if not server.source_code_url:
                        no_source_code_count += 1
                        continue
                    
                    result = supabase.table('mcp_repositories').select('*').execute()
                    
                    existing_entry = False
                    for entry in result.data:
                        if entry.get('metadata') and entry['metadata'].get('source_code_url') == server.source_code_url:
                            existing_entry = True
                            break
                    
                    if existing_entry:
                        skipped_count += 1
                        print(f"Skipping existing repository: {server.name}")
                    else:
                        print(f"Adding new repository: {server.name}")
                        supabase.table('external_mcp_repositories').insert({
                            'name': server.name,
                            'metadata': {
                                'source_code_url': server.source_code_url,
                                'url': server.url,
                                'external_url': server.external_url,
                                'short_description': server.short_description,
                                'github_stars': server.github_stars,
                                'package_registry': server.package_registry,
                                'package_name': server.package_name,
                                'package_download_count': server.package_download_count,
                                'ai_generated_description': server.EXPERIMENTAL_ai_generated_description
                            }
                        }).execute()
                        added_count += 1
                
                next_url = data.next
        
        result = AppendAllServersResponse(
            total_added=added_count,
            skipped=skipped_count,
            message=f"Successfully processed servers: {added_count} added, {skipped_count} skipped (already exist), {no_source_code_count} skipped (no source_code_url)"
        )
        
        print(f"\nSummary: {result.message}")
        return result
        
    except Exception as e:
        error_message = f"Failed to fetch and store external MCP servers: {str(e)}"
        print(f"Error: {error_message}")
        return None

if __name__ == "__main__":
    asyncio.run(append_all_servers()) 