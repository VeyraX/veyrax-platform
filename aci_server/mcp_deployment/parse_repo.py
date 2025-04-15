import re
import requests
from urllib.parse import urlparse
from typing import Dict, Any, List, Optional, Tuple

def parse_github_url(repo_url: str) -> Tuple[str, str, str]:
    repo_url = repo_url.rstrip('/')
    repo_url = re.sub(r'\.git$', '', repo_url)
    
    print(f"Parsing GitHub URL: {repo_url}")
    
    pattern = r'https?://github\.com/([^/]+)/([^/]+)(?:/(.*))?'
    match = re.match(pattern, repo_url)
    
    if not match:
        raise ValueError("Not a valid GitHub URL")
    
    owner, repo_name, remaining_path = match.groups()
    remaining_path = remaining_path or ""
  
    subdir_path = ""
    if remaining_path:
        tree_pattern = r'^(tree|blob)/([^/]+)/(.*)$'
        tree_match = re.match(tree_pattern, remaining_path)
        
        if tree_match:
            _, branch, subdir_path = tree_match.groups()
            print(f"Detected {tree_match.group(1)}/{branch} format with subdirectory: '{subdir_path}'")
        else:
            subdir_path = remaining_path
            print(f"Direct subdirectory path: '{subdir_path}'")
    
    print(f"Final parse result: owner='{owner}', repo='{repo_name}', subdir='{subdir_path}'")
    return owner, repo_name, subdir_path

def get_repository_contents(owner: str, repo_name: str, path: str = "", recursive: bool = True):
    """Получает содержимое репозитория через GitHub API с учетом поддиректории"""
    api_url = f"https://api.github.com/repos/{owner}/{repo_name}/contents/{path}"
    print(f"Fetching repository contents from: {api_url}")
    
    response = requests.get(api_url)
    
    if response.status_code != 200:
        print(f"Error fetching contents: {response.status_code} - {response.text}")
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
    try:
        response = requests.get(download_url)
        
        if response.status_code != 200:
            print(f"Error fetching file content: {response.status_code}")
            return None
        
        return response.text
    except Exception as e:
        print(f"Exception fetching file content: {str(e)}")
        return None

def is_text_file(filename: str):
    text_extensions = {
        '.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.scss', '.json', '.xml',
        '.yml', '.yaml', '.md', '.txt', '.sh', '.bash', '.c', '.cpp', '.h', '.java', 
        '.rb', '.php', '.go', '.sql', '.json'
    }
    
    special_files = {
        'dockerfile', 'makefile', 'jenkinsfile', 'procfile', 'gemfile', 'rakefile',
        'vagrantfile', 'bashrc', 'gitignore', 'dockerignore', 'editorconfig'
    }
    
    basename = filename.split('/')[-1].lower()
    
    if '.' not in basename:
        return basename in special_files
    
    ext = '.' + basename.split('.')[-1]
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
    owner, repo_name, subdir_path = parse_github_url(repo_url)
    
    print(f"Parsing repository: {owner}/{repo_name}, subdirectory: {subdir_path or 'root'}")
    
    contents = get_repository_contents(owner, repo_name, subdir_path)
    
    if not contents:
        print(f"Warning: No contents found in repository subdirectory: {subdir_path}")
    
    contents.sort(key=lambda x: x['path'])
    
    result = {
        "repository": {
            "url": repo_url,
            "owner": owner,
            "name": repo_name,
            "subdirectory": subdir_path
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
            
            display_path = file_path
            if subdir_path and file_path.startswith(subdir_path + '/'):
                display_path = file_path[len(subdir_path) + 1:]
            
            result["files"].append({
                "path": display_path,
                "content": truncated_content,
                "truncated": is_truncated
            })
            
            file_count += 1
    
    result["file_count"] = file_count
    result["skipped_count"] = skipped_count
    
    print(f"Repository parsing completed. Added {file_count} files, skipped {skipped_count} files.")
    
    return result 