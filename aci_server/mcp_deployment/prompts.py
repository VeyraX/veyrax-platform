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

Ple

"""


extract_env_variables_prompt = """
Based on provided context of repository, extract environment variables from a given context.

You MUST generate the code without any additional comments or characters. Just the code that I'll paste to the Dockerfile and it will work. 

It just BE JSON with key-value pairs of environment variables.
Example:
{
    "env_variables": {
        "ENV_VARIABLE_1": "value1",
        "ENV_VARIABLE_2": "value2"
    }
}

No other text or characters, NEVER. Just PURE JSON.
"""
