generate_dockerfile_prompt = """
Based on provided context of repository, generate a Dockerfile for a given application.

You MUST generate the code without any additional comments or characters. Just the code that I'll paste to the Dockerfile and it will work. 

Project might be on the node or python. Consider requirements, current Dockerfile or package.json to properly generate the Dockerfile.

You ALWAYS should specify file to build. 

Example:
```
FROM node:18

WORKDIR /app

COPY . .

RUN npm install

RUN npm run build

CMD ["node", "build/index.js"] 
```

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
