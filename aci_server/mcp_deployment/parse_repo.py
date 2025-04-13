import re
import requests
from urllib.parse import urlparse
from typing import Dict, Any, List, Optional

def parse_github_url(repo_url: str):
    repo_url = repo_url.rstrip('/')
    repo_url = re.sub(r'\.git$', '', repo_url)
    
    parsed_url = urlparse(repo_url)
    
    if 'github.com' not in parsed_url.netloc:
        raise ValueError("Not a valid GitHub URL")
    
    path_parts = [p for p in parsed_url.path.split('/') if p]
    
    if len(path_parts) < 2:
        raise ValueError("URL does not contain a valid repository path")
    
    owner = path_parts[0]
    repo_name = path_parts[1]
    
    return owner, repo_name

def get_repository_contents(owner: str, repo_name: str, path: str = "", recursive: bool = True):
    api_url = f"https://api.github.com/repos/{owner}/{repo_name}/contents/{path}"
    response = requests.get(api_url)
    
    if response.status_code != 200:
        return []
    
    contents = response.json()
    
    if not isinstance(contents, list):
        contents = [contents]
    
    all_contents = []
    
    for item in contents:
        if item['type'] == 'file':
            all_contents.append(item)
        elif item['type'] == 'dir' and recursive:
            dir_contents = get_repository_contents(owner, repo_name, item['path'], recursive)
            all_contents.extend(dir_contents)
    
    return all_contents

def get_file_content(download_url: str):
    response = requests.get(download_url)
    
    if response.status_code != 200:
        return None
    
    return response.text

def is_text_file(filename: str):
    text_extensions = {
        '.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.scss', '.json', '.xml',
        '.yml', '.yaml', '.md', '.txt', '.sh', '.bash', '.c', '.cpp', '.h', '.java', 
        '.rb', '.php', '.go', '.sql', 'json', 'Dockerfile'
    }
    
    ext = '.' + filename.split('.')[-1].lower() if '.' in filename else ''
    return ext in text_extensions

def should_skip_file(file_path: str):
    skip_files = [
        'package-lock.json',
        'yarn.lock',
        'pnpm-lock.yaml',
        '.lock',
        '.svg',
        '.png',
        '.jpg',
        '.jpeg',
        '.gif',
        '.ico',
        '.woff',
        '.woff2',
        '.ttf',
        '.eot',
        '.mp4',
        '.mp3',
        '.wav',
        '.pdf',
        '.gz',
        '.zip',
        '.tar',
        '.min.js',
        '.min.css',
        'node_modules/'
    ]
    
    for skip in skip_files:
        if skip in file_path.lower():
            return True
    
    return False

def parse_repository(repo_url: str):
    owner, repo_name = parse_github_url(repo_url)
    
    print(f"Parsing repository: {owner}/{repo_name}")
    contents = get_repository_contents(owner, repo_name)
    
    contents.sort(key=lambda x: x['path'])
    
    result = {
        "repository": {
            "url": repo_url,
            "owner": owner,
            "name": repo_name
        },
        "files": []
    }
    
    file_count = 0
    max_files = 50 
    skipped_count = 0
    
    for item in contents:
        if file_count >= max_files:
            result["truncated"] = True
            break
            
        file_path = item['path']
        download_url = item['download_url']
        
        if should_skip_file(file_path):
            skipped_count += 1
            continue
        
        if not is_text_file(file_path):
            skipped_count += 1
            continue
        
        content = get_file_content(download_url)
        
        if content is not None:
            truncated_content = content[:50000] if len(content) > 50000 else content
            is_truncated = len(content) > 50000
            
            result["files"].append({
                "path": file_path,
                "content": truncated_content,
                "truncated": is_truncated
            })
            
            file_count += 1
    
    result["file_count"] = file_count
    result["skipped_count"] = skipped_count
    
    print(f"Repository parsing completed. Added {file_count} files, skipped {skipped_count} files.")
    
    return result 