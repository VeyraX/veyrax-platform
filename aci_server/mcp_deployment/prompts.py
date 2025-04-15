generate_dockerfile_prompt = """
Based on provided context of repository, generate a Dockerfile for a given application.

You MUST generate the code without any additional comments or characters. Just the code that I'll paste to the Dockerfile and it will work. 

IMPORTANT: 
When generating the Dockerfile, understand that:
1. If the repository has a subdirectory structure, ALL FILES FROM THE SUBDIRECTORY ARE ALREADY IN THE ROOT of the build context.
2. Do not use paths like "src/subdirectory/..." as they won't exist in the build context - all files are directly in the root.
3. Use COPY . . to copy all files from the current directory to the container, or specific files if needed.

PYTHON PROJECT INSTRUCTIONS:
Follow these exact steps when handling Python projects:

1. FIRST, ANALYZE DEPENDENCY MANAGEMENT APPROACH:
   - Check which dependency files exist in the repository
   - DO NOT assume that requirements.txt exists - it may not!
   - Look for one of these patterns:
     a) requirements.txt - pip's standard requirements file
     b) pyproject.toml and poetry.lock - indicates Poetry usage
     c) Pipfile and Pipfile.lock - indicates Pipenv usage
     d) setup.py or setup.cfg - setuptools project
     e) environment.yml - conda environment

2. THEN CHOOSE THE CORRECT INSTALLATION METHOD:
   - For requirements.txt: `pip install -r requirements.txt`
   - For Poetry: `pip install poetry && poetry install`
   - For Pipenv: `pip install pipenv && pipenv install --system --deploy`
   - For setup.py: `pip install .`
   - For conda: `conda env create -f environment.yml`

3. CRITICAL: ONLY COPY DEPENDENCY FILES THAT ACTUALLY EXIST!
   - DO NOT include statements like `COPY requirements.txt .` unless confirmed that file exists
   - INSTEAD use patterns like:
     ```
     # Copy only dependency files first for better caching
     COPY pyproject.toml poetry.lock* ./
     ```
   - Include the wildcard * for optional files

4. STANDARD PYTHON DOCKERFILE PATTERNS:
   a) For pip with requirements.txt (ONLY if it exists):
   ```
   FROM python:3.11-slim
   
   WORKDIR /app
   
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   COPY . .
   
   CMD ["python", "app.py"]
   ```
   
   b) For Poetry project:
   ```
   FROM python:3.11-slim
   
   WORKDIR /app
   
   RUN pip install poetry
   
   COPY pyproject.toml poetry.lock* ./
   RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi
   
   COPY . .
   
   CMD ["python", "app.py"]
   ```
   
   c) For Pipenv project:
   ```
   FROM python:3.11-slim
   
   WORKDIR /app
   
   RUN pip install pipenv
   
   COPY Pipfile Pipfile.lock .
   RUN pipenv install --system --deploy
   
   COPY . .
   
   CMD ["python", "app.py"]
   ```

TYPESCRIPT & NODE.JS PROJECT INSTRUCTIONS:
Follow these guidelines for TypeScript and Node.js projects:

1. ALWAYS USE THE SIMPLEST APPROACH POSSIBLE
   - Avoid complex multi-stage builds
   - Don't over-optimize or add unnecessary steps
   - Trust the package manager to handle dependencies correctly

2. FOR ALL NODE.JS PROJECTS (INCLUDING MONOREPOS):
   - Use a single, simple Dockerfile
   - Copy all files at once to avoid path issues
   - Use standard npm/yarn commands without extra flags unless needed

3. STANDARD NODE.JS DOCKERFILE (USE THIS BY DEFAULT):
```
FROM node:18-alpine

WORKDIR /app

# Copy everything
COPY . .

# Install dependencies and build
RUN npm install
RUN npm run build

# Set the entry point (adjust based on project)
CMD ["node", "dist/index.js"]
```

4. FOR MONOREPO PROJECTS:
   - Keep the same simple approach
   - Let npm/yarn workspace commands handle dependencies
   - Adjust the CMD path based on the target package

If you find an existing Dockerfile in the repository, USE IT AS A REFERENCE but adapt it to be more compatible:
1. For Node.js projects, use node:18 or node:20 instead of older versions
2. Make sure paths are relative to the build context

NEVER add ```dockerfile``` or `````` to the code. Just the code that I'll paste to the Dockerfile and it will work. JUST CODE.

IT IS VERY CRUCIAL, BECAUSE I'LL PASTE IT DIRECTLY TO THE DOCKERFILE, AND IF YOU ADD ANYTHING ELSE, IT WILL BREAK THE DOCKERFILE.
"""


extract_env_variables_prompt = """
Based on provided context of repository, extract environment variables from a given context.

You MUST generate the code without any additional comments or characters. Just the code that I'll paste to the Dockerfile and it will work. 

It just BE JSON with key-value pairs of environment variables.
Example:
{
    "ENV_VARIABLE_1": "value1",
    "ENV_VARIABLE_2": "value2"
}

No other text or characters, NEVER. Just PURE JSON.

Pay attention on the confings and proccess.env files, or os.env files, or .env files. Very important.

NEVER take env from test.py or test.yml or any other config files. You MUST take ONLY env that required to run the project.

NEVER add ```json``` or `````` to the code. Just the code that I'll paste to the Dockerfile and it will work. JUST CODE.

Think about tool and repository and include only environment variables that crucial to run the project.
"""

extract_repo_metadata_prompt = """
Based on provided context of repository, generate a name and description for this MCP (Multi-Cloud Plugin).

You MUST return a JSON object with 'name' and 'description' fields. The name should be concise, descriptive, and highlight the main functionality. The description should be 1-2 sentences explaining what the MCP does.

Example:
{
    "name": "GitHub Terminal",
    "description": "Execute terminal commands and manage files in GitHub repositories. Provides code access, shell operations, and automation capabilities."
}

Keep it concise and focused on the functionality. Return only pure JSON with no markdown formatting or additional text.

In MOST of the cases you MUST take name from README.md and description. NEVER hallucinate about the name and description.

NEVER add ```json``` or `````` to the code. Just the code that I'll paste to the Dockerfile and it will work. JUST CODE.
"""
