generate_dockerfile_prompt = """
Based on provided context of repository, generate a Dockerfile for a given application.

You MUST generate the code without any additional comments or characters. Just the code that I'll paste to the Dockerfile and it will work. 

IMPORTANT: 
When generating the Dockerfile, understand that:
1. If the repository has a subdirectory structure, ALL FILES FROM THE SUBDIRECTORY ARE ALREADY IN THE ROOT of the build context.
2. Do not use paths like "src/subdirectory/..." as they won't exist in the build context - all files are directly in the root.
3. Use COPY . . to copy all files from the current directory to the container, or specific files if needed.

TYPESCRIPT PROJECT INSTRUCTIONS:
Follow these exact steps when handling TypeScript projects:

1. ANALYZE PROJECT STRUCTURE:
   - Look at package.json, build scripts, and tsconfig.json
   - Check if there are any build or start scripts that reference specific paths

2. FOR PROJECTS WITH tsconfig.json:
   - CAREFULLY EXAMINE tsconfig.json content before deciding approach!
   - ONLY use the special approach if ABSOLUTELY NECESSARY

3. WHEN TO USE STANDARD APPROACH (MOST CASES):
   - For typical TypeScript projects where tsconfig.json is simple
   - When tsconfig.json does NOT have "extends" property referencing parent directories
   - When build scripts don't use absolute paths to reference tsconfig.json
   - JUST USE: `COPY . .` and standard Docker patterns

4. WHEN TO USE SPECIAL ROOT COPYING APPROACH (RARE CASES):
   - ONLY when tsconfig.json has "extends": "../../tsconfig.json" or similar paths going outside build context
   - ONLY when build commands explicitly reference "/tsconfig.json" with absolute path
   - ONLY when you see previous build errors about not finding tsconfig.json in root
   - In these cases, use the multi-stage build with copying tsconfig.json to BOTH locations

STANDARD DOCKERFILE FOR MOST TYPESCRIPT PROJECTS:
```
FROM node:18

WORKDIR /app

COPY . .

RUN npm install
RUN npm run build

CMD ["node", "dist/index.js"]
```

SPECIAL DOCKERFILE FOR TYPESCRIPT WITH SPECIAL CONFIGURATION:
```
FROM node:18 AS builder

# Copy project files
COPY . /app
# SPECIAL STEP: Also copy tsconfig.json to root filesystem (only needed for special configs)
COPY tsconfig.json /tsconfig.json

WORKDIR /app

RUN npm install
RUN npm run build

FROM node:18

WORKDIR /app

COPY --from=builder /app/dist /app/dist
COPY --from=builder /app/package.json /app/package.json
COPY --from=builder /app/package-lock.json /app/package-lock.json

ENV NODE_ENV=production

RUN npm ci --ignore-scripts --omit=dev

CMD ["node", "dist/index.js"]
```

GUIDELINES FOR CHOOSING THE RIGHT APPROACH:
1. DEFAULT TO STANDARD APPROACH unless project specifically requires root tsconfig.json
2. ONLY use special approach when necessary to prevent build failures
3. The special approach does not significantly impact image size or performance
4. When in doubt, check if tsconfig.json contains "extends" with paths going outside build context

If you find an existing Dockerfile in the repository, USE IT AS A REFERENCE but adapt it to be more compatible:
1. For Node.js projects, use node:18 or node:20 instead of older or alpha/preview versions
2. Make sure the paths are relative to the build context root, not to some absolute paths
3. Ensure any tsconfig.json is copied to the correct location within the container

For Node.js projects:
- Prefer node:18 or node:20 base images
- If TypeScript is used, make sure to properly handle tsconfig.json and build steps
- Make sure the correct entry point is specified (check package.json for "main" field)

For Python projects:
- Use python:3.9 or python:3.10 as base images
- Include a proper pip install step for requirements.txt
- Make sure to specify the correct entry point

You ALWAYS should specify file to build and pay attention to the structure of the project.

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
