from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException, Depends, Response
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
from integrations.clickhouse.route import router as clickhouse_router
from integrations.snowflake.route import router as snowflake_router
from integrations.postgresql.route import router as postgresql_router
from integrations.veyrax.route import router as veyrax_router
from integrations.firecrawl.route import router as firecrawl_router
from integrations.ticktick.route import router as ticktick_router
from integrations.brave.route import router as brave_router
from integrations.tavily.route import router as tavily_router
from integrations.exa.route import router as exa_router
from integrations.asana.route import router as asana_router
from integrations.trello.route import router as trello_router
from integrations.figma.route import router as figma_router
from integrations.sentry.route import router as sentry_router
from integrations.http_request.route import router as http_request_router
from integrations.vercel.route import router as vercel_router
from integrations.hacker_news.route import router as hacker_news_router
from integrations.readwise.route import router as readwise_router
from integrations.postman.route import router as postman_router
from integrations.common.utils import get_router_tools, log_api_call
from integrations.common.route_identifier import route_method
from integrations.common.prompt_example import get_tools_example_prompt, get_tools_example_prompt_empty

from celery_app import celery_app
from integrations.common.get_memory import get_user_memories
import os
import json
import inspect
import sentry_sdk


load_dotenv()

sentry_url = os.getenv("SENTRY_URL")
NEXT_PUBLIC_SENTRY_ENVIRONMENT = os.getenv('NEXT_PUBLIC_SENTRY_ENVIRONMENT', 'production')

sentry_sdk.init(
    dsn=sentry_url,
    send_default_pii=True,
    traces_sample_rate=1.0,
    environment=NEXT_PUBLIC_SENTRY_ENVIRONMENT,
    _experiments={
        "continuous_profiling_auto_start": True,
    },
)

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
    "youtube": youtube_router,
    "clickhouse": clickhouse_router,
    "snowflake": snowflake_router,
    "postgresql": postgresql_router,
    "veyrax": veyrax_router,
    "firecrawl": firecrawl_router,
    "ticktick": ticktick_router,
    "brave": brave_router,
    "exa": exa_router,
    "tavily": tavily_router,
    "asana": asana_router,
    "trello": trello_router,
    "figma": figma_router,
    "sentry": sentry_router,
    "http-request": http_request_router,
    "vercel": vercel_router,
    "hacker-news": hacker_news_router,
    "postman": postman_router,
    "readwise": readwise_router
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


## healthcheck route
@app.head("/")
async def root_head():
    try:
        tools = await get_tools()
        if not tools.get("tools"):
            return Response(status_code=503, content="No tools configured")
            
        return Response(status_code=200)
    except Exception as e:
        return Response(
            status_code=500,
            content=f"Tools check failed: {str(e)}"
        )

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
async def handle_tool_call(tool: str, method: str, request: Request, include_component: bool = True):
    success = 0
    response = None
    error_message = None
    try:
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
                        except Exception as dep_error:
                            error_msg = f"Error resolving dependency {name}: {str(dep_error)}"
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
                        endpoint_args[name] = params
                    elif name == "params" and is_body_param:
                        endpoint_args[name] = params
                    elif name == "request" and name not in endpoint_args:
                        endpoint_args[name] = request
                
                try:
                    response = await route.endpoint(**endpoint_args)
                    success = 1
                except Exception as exc:
                    success = 0 
                    error_message = str(exc)
                    raise exc
                
                if not include_component:
                    if isinstance(response, dict) and "component" in response:
                        response.pop("component")
                    elif hasattr(response, "component") and hasattr(response, "dict"):
                        response_dict = response.dict()
                        if "component" in response_dict:
                            response_dict.pop("component")
                        return response_dict
                
                return response
        
        raise HTTPException(status_code=404, detail=f"Method '{method}' not found in tool '{tool}'")
    
    except Exception as exc:
        error_message = str(exc)
        raise
    
    finally:
        try:
            user_id = await get_user_from_request(request)
            log_api_call(
                user_id=user_id,
                endpoint=f"/tool-call/{tool}/{method}",
                success=success,
                error_message=error_message
            )
        except Exception as log_error:
            print(f"Error logging API call for Supabase: {str(log_error)}")

@app.get("/tools/{tool_name}")
async def get_tool_spec(tool_name: str):
    if tool_name not in INTEGRATION_ROUTERS:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
    
    router = INTEGRATION_ROUTERS[tool_name]
    return {"tools": get_router_tools(router)}

@app.get("/get-tools")
async def get_user_tools(request: Request):
    if NEXT_PUBLIC_SENTRY_ENVIRONMENT.lower() == 'development':
        return await get_dev_user_tools(request)
    
    try:
        user_id = await get_user_from_request(request)
    except Exception as e:  
        raise HTTPException(status_code=401, detail=f"Invalid authentication: {str(e)}")
    
    try:
        supabase = get_supabase()
    
        user_providers = supabase.table('users_providers') \
            .select('provider_id') \
            .eq('user_id', user_id) \
            .execute()
            
        if not user_providers.data:
            tools_response = {"tools": {}}
            tools_response["tools"]["examples"] = json.loads(get_tools_example_prompt_empty)
            
            tools_response["tools"]["memories"] = {}
            
            return tools_response
            
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
        
        user_memories = await get_user_memories(user_id)
        user_tools['memories'] = user_memories
        
        log_api_call(
            user_id=user_id,
            endpoint="/get-tools",
            success=1
        )
        
        return {"tools": user_tools}
    except Exception as e:
        log_api_call(
            user_id=user_id,
            endpoint="/get-tools",
            success=0,
            error_message=str(e)
        )
        raise HTTPException(status_code=500, detail=f"Failed to get user tools: {str(e)}")

async def get_dev_user_tools(request: Request):
    try:
        user_id = await get_user_from_request(request)
    except Exception as e:  
        raise HTTPException(status_code=401, detail=f"Invalid authentication: {str(e)}")
    
    try:
        supabase = get_supabase()
    
        user_providers = supabase.table('users_providers') \
            .select('provider_id') \
            .eq('user_id', user_id) \
            .execute()
            
        if not user_providers.data:
            tools_response = {"tools": {}}
            tools_response["tools"]["examples"] = json.loads(get_tools_example_prompt_empty)
            tools_response["tools"]["memories"] = {}
            
            return tools_response
            
        provider_ids = [item['provider_id'] for item in user_providers.data]
        
        providers = supabase.table('providers') \
            .select('provider_tag') \
            .in_('id', provider_ids) \
            .execute()
            
        provider_tags = [provider['provider_tag'] for provider in providers.data]
        
        user_tools = {}
        user_tools['examples'] = json.loads(get_tools_example_prompt)
        
        for name, router in INTEGRATION_ROUTERS.items():
            if name in provider_tags:
                tool_schemas = get_router_tools(router)

                provider_tools = {}
                for tool_schema in tool_schemas:
                    method_name = tool_schema["function"]["name"]
                    provider_tools[method_name] = tool_schema
                
                # Add to user_tools
                user_tools[name] = provider_tools
        
        # Add memories
        user_memories = await get_user_memories(user_id)
        user_tools['memories'] = user_memories
        
        
        return {"tools": user_tools}
    except Exception as e:
        log_api_call(
            user_id=user_id,
            endpoint="/dev/get-user-tools",
            success=0,
            error_message=str(e)
        )
        raise HTTPException(status_code=500, detail=f"Failed to get dev user tools: {str(e)}")