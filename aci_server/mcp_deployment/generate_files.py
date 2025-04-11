from openai import OpenAI
import os
from .prompts import generate_dockerfile_prompt, extract_env_variables_prompt
from dotenv import load_dotenv

load_dotenv()

def openai_call(system_message, human_message):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": human_message}
        ],
        temperature=0
    )
    
    return response.choices[0].message.content
    

def generate_dockerfile(context):
    system_message = generate_dockerfile_prompt
    human_message = context
    return openai_call(system_message, human_message)

def extract_env_variables(context):
    system_message = extract_env_variables_prompt
    human_message = context
    return openai_call(system_message, human_message)