import re
import requests
import os
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
    api_url = f"https://api.github.com/repos/{owner}/{repo_name}/contents/{path}"
    print(f"Fetching repository contents from: {api_url}")
    
    github_token = os.environ.get("GITHUB_TOKEN")
    headers = {}
    if github_token:
        headers["Authorization"] = f"Bearer {github_token}"
    
    response = requests.get(api_url, headers=headers)
    
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
        github_token = os.environ.get("GITHUB_TOKEN")
        headers = {}
        if github_token:
            headers["Authorization"] = f"Bearer {github_token}"
        
        response = requests.get(download_url, headers=headers)
        
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
        'node_modules/',
        '_next/',
        '.log',
        '.bak',
        '.tmp',
        '.sqlite',
        '.db',
        '.DS_Store',
        'node_modules/',
        'public/',
        '_next/',
        '.next/',
        '.output/',
        '.vercel/',
        'dist/',
        'build/',
        '.cache/',
        '.vite/',
        '.turbo/',
        'static/',
        'logs/',
        'coverage/',
        '.expo/',
        '.android/',
        '.ios/',
        'src/assets/'
    ]
    
    for skip in skip_files:
        if skip in file_path.lower():
            return True
    
    return False

def check_dockerfile_exists(repo_files):
    try:
        if not repo_files or not isinstance(repo_files, list):
            return False
            
        for file in repo_files:
            if not isinstance(file, dict) or "path" not in file:
                continue
                
            file_path = file.get("path", "").lower()
            if file_path == "dockerfile" or file_path.endswith("/dockerfile") or "/dockerfile" in file_path:
                return True
                
        return False
    except Exception as e:
        return False

def generate_file_structure_tree(contents: List[Dict[str, Any]], subdir_path: str = ""):
    file_tree = {}
    workdir_parts = subdir_path.split('/') if subdir_path else []
    
    workdir_files = []
    
    for item in contents:
        file_path = item['path']
        if should_skip_file(file_path) or not is_text_file(file_path):
            continue
        
        is_in_workdir = False
        if subdir_path and (file_path == subdir_path or file_path.startswith(subdir_path + '/')):
            is_in_workdir = True
            workdir_files.append(item)
        
        is_root_file = '/' not in file_path
            
        path_parts = file_path.split('/')
        current = file_tree
        for i, part in enumerate(path_parts):
            on_workdir_path = (i < len(workdir_parts) and part == workdir_parts[i])
            
            if i == len(path_parts) - 1:
                if on_workdir_path or is_in_workdir or is_root_file:
                    current.setdefault('__files__', []).append(part)
            else:
                if part not in current:
                    current[part] = {}
                current = current[part]
    
    tree_text = []
    
    def build_tree(node, path_so_far="", indent=""):
        if '__files__' in node:
            files = sorted(node['__files__'])
            for i, file_name in enumerate(files):
                is_last = (i == len(files) - 1) and not [k for k in node.keys() if k != '__files__']
                tree_text.append(f"{indent}{'└── ' if is_last else '├── '}{file_name}")
        
        dirs = sorted([(k, v) for k, v in node.items() if k != '__files__'])
        
        for i, (dir_name, contents) in enumerate(dirs):
            is_last_dir = (i == len(dirs) - 1)
            current_path = f"{path_so_far}/{dir_name}" if path_so_far else dir_name
            
            is_on_workdir_path = False
            for j, wp in enumerate(workdir_parts):
                if j < len(current_path.split('/')) and current_path.split('/')[j] == wp:
                    is_on_workdir_path = True
                else:
                    is_on_workdir_path = False
                    break
            
            is_workdir = (current_path == subdir_path)
            
            dir_indicator = f"{dir_name}/" + (" [*]" if is_workdir else "")
            tree_text.append(f"{indent}{'└── ' if is_last_dir else '├── '}{dir_indicator}")
            
            next_indent = indent + ('    ' if is_last_dir else '│   ')
            
            if is_on_workdir_path or is_workdir or current_path.startswith(subdir_path + '/'):
                build_tree(contents, path_so_far=current_path, indent=next_indent)
    
    tree_text.append("Repository structure (focused on working directory):")
    tree_text.append(".")
    build_tree(file_tree)
    
    if subdir_path:
        tree_text.append("")
        tree_text.append(f"Working path: {subdir_path}")
    
    return "\n".join(tree_text)

def parse_repository(repo_url: str):
    owner, repo_name, subdir_path = parse_github_url(repo_url)
    
    print(f"Starting to fetch repository contents for {owner}/{repo_name}")
    full_repo_contents = get_repository_contents(owner, repo_name, "")
    print(f"Fetched {len(full_repo_contents)} files from full repository")
    
    file_structure_tree = generate_file_structure_tree(full_repo_contents, subdir_path)
    
    contents = get_repository_contents(owner, repo_name, subdir_path)
    
    if not contents:
        print(f"Warning: No contents found in repository subdirectory: {subdir_path}")
    else:
        print(f"Fetched {len(contents)} files from subdirectory: {subdir_path}")
    
    contents.sort(key=lambda x: x['path'])
    
    result = {
        "repository": {
            "url": repo_url,
            "owner": owner,
            "name": repo_name,
            "subdirectory": subdir_path
        },
        "file_structure": file_structure_tree,
        "files": []
    }
    
    file_count = 0
    max_files = 40 
    skipped_count = 0
    
    print(f"Starting to process {len(contents)} repository files (max: {max_files})")
    
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
    
    # Check explicitly for Dockerfile before returning
    has_dockerfile = check_dockerfile_exists(result.get("files", []))
    print(f"Dockerfile check result: {has_dockerfile}")
    
    return result 