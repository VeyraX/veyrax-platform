from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from db.supabase import get_supabase
from integrations.common.auth import get_user_from_request
from integrations.google_calendar.schema import EventFilters
from integrations.google_calendar.route import get_calendar_service
from integrations.gmail.route import router as gmail_router
from integrations.google_calendar.route import router as google_calendar_router
from integrations.notion.route import router as notion_router
from integrations.slack.route import router as slack_router
from integrations.linear.route import router as linear_router
from integrations.openweather.route import router as openweather_router
from integrations.perplexity.route import router as perplexity_router
from integrations.google_drive.route import router as google_drive_router
from integrations.jira.route import router as jira_router
from integrations.confluence.route import router as confluence_router
from integrations.outlook.route import router as outlook_router
from integrations.dropbox.route import router as dropbox_router
from integrations.resend.route import router as resend_router
from integrations.browser_use.route import router as browser_use_router
from integrations.github.route import router as github_router
from integrations.youtube.route import router as youtube_router
from integrations.common.utils import get_router_tools
from integrations.common.route_identifier import route_method
from integrations.common.prompt_example import get_tools_example_prompt
from celery_app import celery_app

import os
import importlib
import json
import inspect

load_dotenv()

INTEGRATION_ROUTERS = {
    "gmail": gmail_router,
    "google-calendar": google_calendar_router,
    "notion": notion_router,
    "slack": slack_router,
    "linear": linear_router,
    "openweather": openweather_router,
    "perplexity": perplexity_router,
    "google-drive": google_drive_router,
    "jira": jira_router,
    "confluence": confluence_router,
    "outlook": outlook_router,
    "dropbox": dropbox_router,
    "resend": resend_router,
    "browser-use": browser_use_router,
    "github": github_router,
    "youtube": youtube_router
}

app = FastAPI()

app.state.celery = celery_app

app.add_middleware(
    CORSMiddleware,
    allow_origins='*',
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in INTEGRATION_ROUTERS.values():
    app.include_router(router)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/tools")
async def get_tools():
    tools = {}
    for name, router in INTEGRATION_ROUTERS.items():
        tools[name] = get_router_tools(router)
    
    return {"tools": tools}

def find_route_by_tool_and_method(tool: str, method: str):
    if tool not in INTEGRATION_ROUTERS:
        raise HTTPException(status_code=404, detail=f"Tool '{tool}' not found")
    
    router = INTEGRATION_ROUTERS[tool]
    
    for route in router.routes:
        if route_method(route) == method:
            return route
    
    return None

@app.post("/tool-call/{tool}/{method}")
async def handle_tool_call(tool: str, method: str, request: Request):
    
    try:
        params = await request.json()
    except:
        params = {}
    
    if tool not in INTEGRATION_ROUTERS:
        raise HTTPException(status_code=404, detail=f"Tool '{tool}' not found")
    
    router = INTEGRATION_ROUTERS[tool]
    
    for route in router.routes:
        if route_method(route) == method:
            signature = inspect.signature(route.endpoint)
            
            endpoint_args = {}
            
            for name, param in signature.parameters.items():
                if param.default != inspect.Parameter.empty and hasattr(param.default, "__class__") and param.default.__class__.__name__ == "Depends":
                    dep_func = param.default.dependency
                    try:
                        dependency_result = await dep_func(request)
                        
                        if hasattr(dependency_result, "__class__") and dependency_result.__class__.__name__ == "Depends":
                            raise ValueError(f"Dependency resolution error: got Depends object instead of service instance")
                            
                        endpoint_args[name] = dependency_result
                    except Exception as e:
                        error_msg = f"Error resolving dependency {name}: {str(e)}"
                        print(error_msg)
                        raise HTTPException(status_code=500, detail=error_msg)
            
            for name, param in signature.parameters.items():
                if name in endpoint_args:
                    continue
                    
                is_body_param = (
                    param.default != inspect.Parameter.empty 
                    and hasattr(param.default, "__class__") 
                    and param.default.__class__.__name__ == "Body"
                )
                
                if name in params:
                    endpoint_args[name] = params[name]
                elif name == "params" and is_body_param:
                    endpoint_args[name] = params
                elif name == "request" and name not in endpoint_args:
                    endpoint_args[name] = request
            
            print(f"Calling {method} with {endpoint_args}")
            
            return await route.endpoint(**endpoint_args)
    
    raise HTTPException(status_code=404, detail=f"Method '{method}' not found in tool '{tool}'")

@app.get("/tools/{tool_name}")
async def get_tool_spec(tool_name: str):
    if tool_name not in INTEGRATION_ROUTERS:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
    
    router = INTEGRATION_ROUTERS[tool_name]
    return {"tools": get_router_tools(router)}

@app.get("/get-tools")
async def get_user_tools(request: Request):
    try:
        user_id = await get_user_from_request(request)
        
        supabase = get_supabase()
        
        user_providers = supabase.table('users_providers') \
            .select('provider_id') \
            .eq('user_id', user_id) \
            .execute()
            
        if not user_providers.data:
            return {"tools": {}}
            
        provider_ids = [item['provider_id'] for item in user_providers.data]
        
        providers = supabase.table('providers') \
            .select('provider_tag, input_schema') \
            .in_('id', provider_ids) \
            .execute()
            
        user_tools = {}
        user_tools['examples'] = json.loads(get_tools_example_prompt)

        for provider in providers.data:
            if provider.get('input_schema'):
                user_tools[provider['provider_tag']] = provider['input_schema']
        
        return {"tools": user_tools}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user tools: {str(e)}")