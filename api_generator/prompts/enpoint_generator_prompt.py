endpoint_generator_prompt_few_shot_1 = '''
Tool: Gmail 
Endpoint: /api/v1/gmail/messages    

Expected files: [
    {
        "client.py": """
from typing import Dict, Any
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

class GmailClient:
    def __init__(self, credentials: Credentials):
        self.service = build('gmail', 'v1', credentials=credentials)
    
    def list_messages(self) -> Dict[str, Any]:
        return self.service.users().messages().list(userId='me').execute()
""",
        "schema.py": """
from typing import List
from pydantic import BaseModel

class Message(BaseModel):
    id: str
    thread_id: str
    snippet: str

class MessageList(BaseModel):
    messages: List[Message]
""",
        "service.py": """
from .client import GmailClient
from .schema import MessageList, Message

class GmailService:
    def __init__(self, client: GmailClient):
        self.client = client

    def get_messages(self) -> MessageList:
        response = self.client.list_messages()
        messages = [Message(**msg) for msg in response.get('messages', [])]
        return MessageList(messages=messages)
""",
        "route.py": """
from fastapi import APIRouter, Depends
from .schema import MessageList
from .service import GmailService

router = APIRouter(prefix="/api/v1/gmail")

@router.get("/messages", response_model=MessageList)
async def list_messages(
    service: GmailService = Depends()
) -> MessageList:
    return service.get_messages()
"""
    }
]
'''

endpoint_generator_prompt = """
You are an expert API developer. For given endpoint you MUST generate list of files that are needed to be created to implement the endpoint.

File structure and description that you MUST to generate: 

- client.py: Raw APIs to tool functions, NEVER add business logic here, ONLY call external APIs
- schema.py: Define data schema for the endpoints and futher APIs calls for requests and responses
- service.py: Business logic to handle the endpoint
- route.py: Endpoint route from services with business logic and applied schema. 
    
Code should be written in Python and should be compatible with FastAPI.
"""

endpoint_generator_prompt = """
You are an expert API developer. For given endpoint you MUST generate list of files that are needed to be created to implement the endpoint.

File structure and description that you MUST to generate: 

- client.py: Raw APIs to tool functions, NEVER add business logic here, ONLY call external APIs
- schema.py: Define data schema for the endpoints and futher APIs calls for requests and responses
- service.py: Business logic to handle the endpoint
- route.py: Endpoint route from services with business logic and applied schema. 
    
Code should be written in Python and should be compatible with FastAPI.
"""