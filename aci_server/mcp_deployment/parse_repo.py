import re
import requests
from urllib.parse import urlparse
from typing import Dict, Any, List, Optional

def parse_github_url(repo_url: str):
    """Extract owner and repo name from GitHub URL"""
    # Remove trailing slashes and .git extension if present
    repo_url = repo_url.rstrip('/')
    repo_url = re.sub(r'\.git$', '', repo_url)
    
    # Parse URL
    parsed_url = urlparse(repo_url)
    
    # Verify it's a GitHub URL
    if 'github.com' not in parsed_url.netloc:
        raise ValueError("Not a valid GitHub URL")
    
    # Extract path components
    path_parts = [p for p in parsed_url.path.split('/') if p]
    
    if len(path_parts) < 2:
        raise ValueError("URL does not contain a valid repository path")
    
    owner = path_parts[0]
    repo_name = path_parts[1]
    
    return owner, repo_name

def get_repository_contents(owner: str, repo_name: str, path: str = "", recursive: bool = True):
    """Get contents of a repository at a specific path"""
    api_url = f"https://api.github.com/repos/{owner}/{repo_name}/contents/{path}"
    response = requests.get(api_url)
    
    if response.status_code != 200:
        return []
    
    contents = response.json()
    
    # If single file is returned (not a list), wrap it in a list
    if not isinstance(contents, list):
        contents = [contents]
    
    all_contents = []
    
    for item in contents:
        if item['type'] == 'file':
            all_contents.append(item)
        elif item['type'] == 'dir' and recursive:
            # Recursively get directory contents
            dir_contents = get_repository_contents(owner, repo_name, item['path'], recursive)
            all_contents.extend(dir_contents)
    
    return all_contents

def get_file_content(download_url: str):
    """Get content of a specific file"""
    response = requests.get(download_url)
    
    if response.status_code != 200:
        return None
    
    return response.text

def is_text_file(filename: str):
    """Check if a file is likely to be a text file based on extension"""
    text_extensions = {
        '.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.scss', '.json', '.xml',
        '.yml', '.yaml', '.md', '.txt', '.sh', '.bash', '.c', '.cpp', '.h', '.java', 
        '.rb', '.php', '.go', '.sql', 'json'
    }
    
    ext = '.' + filename.split('.')[-1].lower() if '.' in filename else ''
    return ext in text_extensions

def parse_repository(repo_url: str, max_files: int = 50):
    """
    Parse a GitHub repository and return its contents
    
    Args:
        repo_url: GitHub repository URL
        max_files: Maximum number of files to process
        
    Returns:
        Dictionary with repository information and file contents
    """
    # Parse URL to get owner and repo name
    owner, repo_name = parse_github_url(repo_url)
    
    # Get repository contents
    contents = get_repository_contents(owner, repo_name)
    
    # Sort by path
    contents.sort(key=lambda x: x['path'])
    
    # Prepare result
    result = {
        "repository": {
            "url": repo_url,
            "owner": owner,
            "name": repo_name
        },
        "files": []
    }
    
    # Process each file (up to max_files)
    file_count = 0
    for item in contents:
        # Check file count limit
        if file_count >= max_files:
            result["truncated"] = True
            break
            
        file_path = item['path']
        download_url = item['download_url']
        
        # Skip non-text files
        if not is_text_file(file_path):
            continue
        
        # Get file content
        content = get_file_content(download_url)
        
        if content is not None:
            result["files"].append({
                "path": file_path,
                "content": content[:50000] if len(content) > 50000 else content,  # Limit content size
                "truncated": len(content) > 50000
            })
            
            # Update counter
            file_count += 1
    
    result["file_count"] = file_count
    
    return result 