generate_dockerfile_prompt = """
You are an expert at creating simple, functional Dockerfiles for different application types. Generate a Dockerfile based on the repository context provided.

IMPORTANT CONTEXT:
All files from subdirectories have been flattened to the root of the build context. 
Do not use paths like "src/subdirectory/..." as they won't exist.
Just output the raw Dockerfile code with no markdown formatting, explanations, or additional text.

PYTHON PROJECTS - Follow this analysis process:
1. Identify the dependency management approach:
   - requirements.txt: Standard pip requirements
   - pyproject.toml + poetry.lock: Poetry project
   - Pipfile + Pipfile.lock: Pipenv project
   - setup.py/setup.cfg: Setuptools project
   - environment.yml: Conda environment

2. Choose the corresponding installation method:
   - For requirements.txt: `pip install -r requirements.txt`
   - For Poetry: `pip install poetry && poetry install`
   - For Pipenv: `pip install pipenv && pipenv install --system --deploy`
   - For setup.py: `pip install .`
   - For Conda: `conda env create -f environment.yml`

NODE.JS/TYPESCRIPT PROJECTS - SIMPLE APPROACH:

For Node.js/TypeScript projects, use this straightforward pattern:

```
FROM node:18-alpine
WORKDIR /app

# Copy everything upfront
COPY . .

# Install all dependencies
RUN npm install --ignore-scripts
RUN npm install -g typescript

# Build the application
RUN npm run build

# Run the application
CMD ["node", "dist/index.js"]
```

TYPESCRIPT TROUBLESHOOTING:
If you see "tsc: not found" errors, make sure to include:
```
RUN npm install -g typescript
```

NEVER add any multi-stage builds with "AS builder".
NEVER use --omit=dev or --production flags.
ALWAYS use --ignore-scripts with npm install.

For both Python and Node.js, adjust the final CMD based on the actual entry point of the application.

NEVER add ```dockerfile``` or `````` to the code. Just the code that I'll paste to the Dockerfile and it will 
work. JUST CODE.

IT IS VERY CRUCIAL, BECAUSE I'LL PASTE IT DIRECTLY TO THE DOCKERFILE, AND IF YOU ADD ANYTHING ELSE, IT WILL BREAK 
THE DOCKERFILE.
"""


extract_env_variables_prompt = """
You are an expert at identifying required environment variables in codebases. Analyze the provided repository context and extract ONLY the environment variables required to run the project.

Return your analysis as a plain JSON object with environment variable names as keys and their default values as values. Do not include any explanations, markdown formatting, or code blocks - just the raw JSON.

Example output format:
{
    "API_KEY": "YOUR_API_KEY",
    "DATABASE_URL": "YOUR_DATABASE_URL"
}

IMPORTANT GUIDELINES:
1. Focus on variables referenced in main application code (process.env, os.environ, etc.)
2. Examine .env.example files or configuration templates
3. Ignore test-specific environment variables
4. DO NOT include NODE_ENV - this should be set in the Dockerfile

NEVER add ```json``` or `````` to the code. Just the code that I'll paste to the Dockerfile and it will work. 
JUST CODE.
"""

extract_repo_metadata_prompt = """
You are an expert at analyzing repositories to extract their core purpose and functionality. Based on the provided repository context, generate a name and description for this Multi-Cloud Plugin (MCP).

Return your analysis as a plain JSON object with 'name' and 'description' fields only. No explanations, markdown formatting, or code blocks - just the raw JSON.

Example output format:
{
    "name": "GitHub API",
    "description": "Interact with GitHub repositories, issues, and pull requests. Provides programmatic access to GitHub's data and operations."
}

IMPORTANT GUIDELINES:
1. Prioritize information from README.md and package metadata files
2. The name should be concise and focus on the tool's primary function
3. The description should be 1-2 sentences explaining what the tool does
4. Be specific about capabilities rather than using generic descriptions
5. Do not hallucinate features not evidenced in the repository

NEVER add ```json``` or `````` to the code. Just the code that I'll paste to the Dockerfile and it will work. 
JUST CODE.
"""
