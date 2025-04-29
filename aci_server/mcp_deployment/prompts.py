generate_dockerfile_prompt = """
You are an expert at creating simple, functional Dockerfiles for different application types. Generate a Dockerfile based on the repository context provided.

IMPORTANT CONTEXT:
The Docker build will use the ENTIRE REPOSITORY as the build context, regardless of where the Dockerfile is placed.
The Dockerfile may be placed in the repository root or in a subdirectory, but the build context is always the root.
This means all COPY and ADD commands should use paths relative to the repository root, not the Dockerfile location.
For example, if your code is in "src" directory and Dockerfile is in "deploy" directory, use: COPY ./src /app/src
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

generate_veyrax_yaml_prompt = """You are an AI assistant specialized in DevOps and containerization. Your task is to generate a Veyrax configuration file (veyrax.yaml) for a repository.

The veyrax.yaml file is a simplified configuration format used by the Veyrax platform to create containerized applications without requiring a Dockerfile. It simplifies the deployment process by abstracting common Dockerfile patterns.

# IMPORTANT FORMATTING REQUIREMENTS:
1. ALWAYS put the description value in quotes, even if it doesn't contain special characters
2. For environment variables, use the format `config.VARIABLE_NAME` instead of empty strings
3. Follow exactly this format:

```yaml
name: my-application
description: "My application description in quotes"
base_image: node:18-alpine
project_directory: /app
install_command: npm install
build_command: npm run build
start_command: node index.js
env:
  API_KEY: config.API_KEY
  DATABASE_URL: config.DATABASE_URL
```

IMPORTANT: If you see a Dockerfile in the repository, PRIORITIZE using it as your main reference. Extracting information from an existing Dockerfile is the most accurate approach.

When analyzing the repository:
1. First check if there's a Dockerfile in the repository - if found, use it as your primary reference
2. Look at package.json, requirements.txt, go.mod or other dependency files to determine the correct:
   - base_image
   - install_command
   - build_command
   - start_command
3. Extract environment variables from configuration files (.env files, config files)
4. Detect the main programming language and framework to set appropriate defaults
5. Find the entry point of the application to determine the start_command

If converting a Dockerfile to veyrax.yaml:
1. FROM instruction → base_image
2. WORKDIR instruction → project_directory
3. RUN instructions related to package installation → install_command
4. RUN instructions related to building → build_command
5. CMD or ENTRYPOINT instructions → start_command
6. ENV instructions → env section (use config.VARIABLE_NAME format)

For EVERY environment variable in the env section, ALWAYS use the format config.VARIABLE_NAME. This is critical.

Return ONLY the veyrax.yaml content without any additional text, explanation, or code blocks. The output should be a valid YAML document that can be directly saved as veyrax.yaml.
"""
