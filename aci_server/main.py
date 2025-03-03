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
from integrations.common.utils import get_router_tools
from integrations.common.route_identifier import route_method
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
    "github": github_router
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
    """
    Helper function to find a route by tool name and method.
    
    Args:
        tool: The name of the tool/integration
        method: The method name to find
        
    Returns:
        The matching route or None if not found
    
    Raises:
        HTTPException: If the tool doesn't exist
    """
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
            
            # First handle any dependencies
            for name, param in signature.parameters.items():
                if param.default != inspect.Parameter.empty and hasattr(param.default, "__class__") and param.default.__class__.__name__ == "Depends":
                    dep_func = param.default.dependency
                    try:
                        # Get the actual service/dependency instance
                        dependency_result = await dep_func(request)
                        
                        # Make sure it's not a Depends object itself
                        if hasattr(dependency_result, "__class__") and dependency_result.__class__.__name__ == "Depends":
                            raise ValueError(f"Dependency resolution error: got Depends object instead of service instance")
                            
                        endpoint_args[name] = dependency_result
                    except Exception as e:
                        error_msg = f"Error resolving dependency {name}: {str(e)}"
                        print(error_msg)
                        # Always fail on dependency resolution errors
                        raise HTTPException(status_code=500, detail=error_msg)
            
            # Now handle regular parameters
            for name, param in signature.parameters.items():
                # Skip parameters that are already handled by dependencies
                if name in endpoint_args:
                    continue
                    
                # Check if parameter is a Body parameter
                is_body_param = (
                    param.default != inspect.Parameter.empty 
                    and hasattr(param.default, "__class__") 
                    and param.default.__class__.__name__ == "Body"
                )
                
                if name in params:
                    # Add the parameter directly if it's in our params
                    endpoint_args[name] = params[name]
                elif name == "params" and is_body_param:
                    # For Body parameters named "params", pass the entire params dict
                    endpoint_args[name] = params
                elif name == "request" and name not in endpoint_args:
                    # If the endpoint expects the request object
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
        for provider in providers.data:
            if provider.get('input_schema'):
                tool_name = provider['provider_tag']
                for method in provider['input_schema']:

                    route = find_route_by_tool_and_method(tool_name, method)
                    examples = route.endpoint.examples()

                    provider['input_schema'][method]['examples'] = examples
        
                user_tools[provider['provider_tag']] = provider['input_schema']

        return {"tools": user_tools}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user tools: {str(e)}")