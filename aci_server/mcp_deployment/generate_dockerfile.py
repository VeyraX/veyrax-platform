#!/usr/bin/env python3
import json
import argparse
import sys

from .parse_repo import parse_repository
from .generate_files import generate_dockerfile

def main():
    parser = argparse.ArgumentParser(description="Generate a Dockerfile from a GitHub repository")
    parser.add_argument("repo_url", help="GitHub repository URL to parse")
    parser.add_argument("--max-files", type=int, default=50, help="Maximum number of files to include (1-100)")
    parser.add_argument("-o", "--output", help="Output file path (default: Dockerfile)")
    
    args = parser.parse_args()
    
    if not args.repo_url or 'github.com' not in args.repo_url:
        print("Error: Only GitHub repositories are supported")
        sys.exit(1)
    
    if args.max_files <= 0 or args.max_files > 100:
        print("Error: Max files must be between 1 and 100")
        sys.exit(1)
    
    output_file = args.output or "Dockerfile"
    
    try:
        print(f"Parsing repository: {args.repo_url}...")
        repo_data = parse_repository(
            repo_url=args.repo_url,
            max_files=args.max_files
        )
        print(f"Successfully parsed repository with {repo_data['file_count']} files")
        
        context = json.dumps(repo_data)
        
        print("Generating Dockerfile...")
        dockerfile = generate_dockerfile(context)
        
        with open(output_file, "w") as f:
            f.write(dockerfile)
        
        print(f"Dockerfile successfully generated and saved to: {output_file}")
        
    except ValueError as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
    
    except Exception as e:
        print(f"Error: Failed to generate Dockerfile: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 