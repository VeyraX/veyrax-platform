from fastapi import HTTPException
from openai import OpenAI
from openai import AsyncOpenAI
import os
from .prompts import generate_dockerfile_prompt, extract_env_variables_prompt, extract_repo_metadata_prompt, generate_veyrax_yaml_prompt
from dotenv import load_dotenv
import base64
import httpx
import json
from typing import Dict, Any, Optional
from .parse_repo import check_dockerfile_exists, check_veyrax_yaml_exists, extract_veyrax_yaml_file
from .queries import add_repository_to_providers_index

load_dotenv()

def setup_openrouter_client():
    openrouter_api_key = os.environ.get("OPENROUTER_API_KEY")
    if not openrouter_api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable is not set or empty")
    
    site_url = os.environ.get("SITE_URL", "https://veyraxapp.com")
    site_name = os.environ.get("SITE_NAME", "Veyrax")
    
    client = OpenAI(
        api_key=openrouter_api_key,
        base_url="https://openrouter.ai/api/v1",
        default_headers={
            "HTTP-Referer": site_url,
            "X-Title": site_name
        }
    )
    
    return client

def openai_call(system_message, human_message):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": human_message}
        ],
        temperature=0
    )
    
    return response.choices[0].message.content

def openrouter_claude_call(system_message, human_message):
    client = setup_openrouter_client()
    
    response = client.chat.completions.create(
        model="anthropic/claude-3-7-sonnet",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": human_message}
        ],
        temperature=0
    )
    
    return response.choices[0].message.content

def generate_dockerfile(context):
    system_message = generate_dockerfile_prompt
    human_message = context
    # return openai_call(system_message, human_message)
    return openrouter_claude_call(system_message, human_message)

def extract_env_variables(context, is_local: bool = False):
    system_message = extract_env_variables_prompt
    context_with_flag = json.loads(context)
    context_with_flag["is_local"] = is_local
    human_message = json.dumps(context_with_flag)
    
    try:
        # env_variables_json = openai_call(system_message, human_message)
        env_variables_json = openrouter_claude_call(system_message, human_message)
        return json.loads(env_variables_json)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Failed to parse environment variables JSON")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract environment variables: {str(e)}")

def extract_repo_metadata(context):
    system_message = extract_repo_metadata_prompt
    human_message = context
    try:
        # metadata_json = openai_call(system_message, human_message)
        metadata_json = openrouter_claude_call(system_message, human_message)
        return json.loads(metadata_json)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Failed to parse metadata JSON")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract repository metadata: {str(e)}")

def generate_dockerfile_from_veyrax_yaml(veyrax_config):
    try:
        base_image = veyrax_config.get('base_image', 'node:18-alpine')
        project_dir = veyrax_config.get('project_directory', '/app')
        install_cmd = veyrax_config.get('install_command', 'npm install')
        build_cmd = veyrax_config.get('build_command', '')
        start_cmd = veyrax_config.get('start_command', 'npm start')
        
        dockerfile = f"""
        FROM {base_image}

        WORKDIR {project_dir}

        COPY . .

        RUN {install_cmd}
        """
        
        if build_cmd:
            dockerfile += f"\nRUN {build_cmd}\n"
            
        env_vars = veyrax_config.get('env', {})
        if env_vars:
            for key, value in env_vars.items():
                clean_value = value
                if isinstance(value, str) and value.startswith("config."):
                    clean_value = value[7:]
                dockerfile += f"\nENV {key}={clean_value}"
        
        dockerfile += f"\nCMD {start_cmd}\n"
        
        return dockerfile
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate Dockerfile from veyrax.yaml: {str(e)}")

def extract_metadata_from_veyrax_yaml(veyrax_config):
    try:
        return {
            "name": veyrax_config.get('name', ''),
            "description": veyrax_config.get('description', '')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract metadata from veyrax.yaml: {str(e)}")

def extract_env_variables_from_veyrax_yaml(veyrax_config, is_local=False):
    try:
        env_vars = veyrax_config.get('env', {})
        processed_vars = {}
        for key, value in env_vars.items():
            if isinstance(value, str) and value.startswith("config."):
                processed_vars[key] = value[7:]
            else:
                processed_vars[key] = value
        return processed_vars
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract env variables from veyrax.yaml: {str(e)}")

def generate_dockerfile_with_base64_from_repo(repo_data):
    veyrax_config = extract_veyrax_yaml_file(repo_data.get("files", []))
    if veyrax_config:
        print("Generating Dockerfile from veyrax.yaml")
        dockerfile = generate_dockerfile_from_veyrax_yaml(veyrax_config)
    else:
        print("Generating Dockerfile from Dockerfile")
        dockerfile_content = None
        for file in repo_data.get("files", []):
            if file.get("path", "").lower() == "dockerfile" or file.get("path", "").endswith("/dockerfile"):
                dockerfile_content = file.get("content")
                break
        
        if dockerfile_content:
            dockerfile = dockerfile_content
        else:
            context = json.dumps(repo_data)
            dockerfile = generate_dockerfile(context)
    print("Dockerfile generated")
    print(dockerfile)
    dockerfile_base64 = base64.b64encode(dockerfile.encode()).decode()
    print("Dockerfile base64 encoded")
    return dockerfile_base64

async def push_mcp_to_dockerhub(
    repo_url: str, 
    image_name: str, 
    auth_token: str, 
    repository_id: Optional[str] = None, 
    deployment_id: Optional[str] = None,
    commit_hash: Optional[str] = None
) -> Dict[str, Any]:
    try:
        from .parse_repo import parse_repository
        from .queries import get_cached_dockerfile, save_dockerfile
        
        cached = await get_cached_dockerfile(repository_id, commit_hash)
        if cached and cached.get('docker_file_b64'):
            dockerfile_base64 = cached.get('docker_file_b64')
        else:
            repo_data = parse_repository(repo_url=repo_url)
            dockerfile_base64 = generate_dockerfile_with_base64_from_repo(repo_data)
            
            save_result = await save_dockerfile(repository_id, commit_hash, dockerfile_base64)
            
        
        workflow_id = os.environ.get("GITHUB_WORKFLOW_ID")
        github_repo = os.environ.get("GITHUB_REPO")
        github_token = os.environ.get("GITHUB_TOKEN")
        
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {github_token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json"
        }
        
        workflow_data = {
            "ref": "main",
            "inputs": {
                "repo_url": repo_url,
                "dockerfile_base64": dockerfile_base64,
                "image_name": image_name,
                "auth_token": auth_token,
                "repository_id": repository_id,
                "deployment_id": deployment_id
            }
        }
        
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://api.github.com/repos/{github_repo}/actions/workflows/{workflow_id}/dispatches", 
                headers=headers,
                json=workflow_data,
                timeout=30.0
            )
        
        if response.status_code != 204:
            try:
                response_body = response.json()
                print(f"GitHub API response body: {response_body}")
            except:
                print(f"GitHub API response text: {response.text}")
        
        if response.status_code == 204:
            if repository_id:
                index_result = await add_repository_to_providers_index(repository_id)

                
            return {
                "status": "success",
                "dockerfile_b64": dockerfile_base64,
                "github_workflow_url": f"https://github.com/{github_repo}/actions",
                "message": "Docker image build process started successfully",
                "deployment_id": deployment_id
            }
        else:
            return {
                "status": "partial_success",
                "dockerfile_b64": dockerfile_base64,
                "message": f"Dockerfile generated successfully, but GitHub workflow failed to start. Status code: {response.status_code}",
                "deployment_id": deployment_id
            }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error: {str(e)}",
            "deployment_id": deployment_id
        }

async def generate_veyrax_yaml(data):
    try:
        system_message = generate_veyrax_yaml_prompt
        
        if "dockerfile" in data:
            human_message = json.dumps({
                "dockerfile": data["dockerfile"],
                "source_type": "dockerfile"
            })
        else:
            repo_context = {
                "files": data.get("files", []),
                "file_tree": data.get("file_tree", ""),
                "source_type": "repository"
            }
            
            human_message = json.dumps(repo_context)
        
        yaml_content = openrouter_claude_call(system_message, human_message)
        return yaml_content.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate veyrax.yaml: {str(e)}")
    