from dotenv import load_dotenv

from fastapi import FastAPI, Request, HTTPException, Depends, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pympler import muppy, summary
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
from integrations.svgl.route import router as svgl_router
from integrations.dub.route import router as dub_router
from integrations.e2b.route import router as e2b_router
from integrations.motion.route import router as motion_router
from integrations.coda.route import router as coda_router
from integrations.n8n.route import router as n8n_router
from integrations.browserbase.route import router as browser_base_router
from integrations.typeform.route import router as typeform_router
from integrations.reddit.route import router as reddit_router
from integrations.common.utils import get_router_tools, log_api_call, get_user_flows_actions, get_user_tools_from_actions
from integrations.common.route_identifier import route_method
from integrations.common.prompt_example import get_tools_example_prompt, get_tools_example_prompt_empty
from integrations.linkedin.route import router as linkedin_router
from integrations.replicate.route import router as replicate_router
from integrations.posthog.route import router as posthog_router
from integrations.amazon.route import router as amazon_affiliates_router
from integrations.revid.route import router as revid_ai_router
from integrations.cloudinary.route import router as cloudinary_router
from integrations.airtable.route import router as airtable_router
from integrations.todoist.route import router as todoist_router
from integrations.google_sheets.route import router as google_sheets_router
from integrations.google_docs.route import router as google_docs_router
from integrations.x.route import router as x_router
from integrations.heygen.route import router as heygen_router
from integrations.bannerbear.route import router as bannerbear_router
from integrations.uploadthing.route import router as uploadthing_router
from integrations.mail.route import router as mail_smtp_router
from integrations.neondb.route import router as neondb_router
from integrations.supabase.route import router as supabase_router
from integrations.duckduckgo.route import router as duckduckgo_router
from integrations.ipinfo.route import router as ipinfo_router
from integrations.hunterio.route import router as hunterio_router
from integrations.zip_code.route import router as zip_code_router
from flow.route import router as flow_router
from debug_routes import router as debug_router
from celery_app import celery_app
from integrations.common.get_memory import get_user_memories
import os
import json
import inspect
import sentry_sdk
import random
import time
from starlette.middleware.base import BaseHTTPMiddleware
import httpx

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
    #"gmail": gmail_router,
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
    "readwise": readwise_router,
    "svgl": svgl_router,
    "dub": dub_router,
    "e2b": e2b_router,
    "motion": motion_router,
    "coda": coda_router,
    "n8n": n8n_router,
    "linkedin": linkedin_router,
    "browserbase": browser_base_router,
    "typeform": typeform_router,
    "replicate": replicate_router,
    "reddit": reddit_router,
    "posthog": posthog_router,
    "amazon": amazon_affiliates_router,
    "revid": revid_ai_router,
    "cloudinary": cloudinary_router,
    "airtable": airtable_router,
    "todoist": todoist_router,
    "google-sheets": google_sheets_router,
    "google-docs": google_docs_router,
    "x": x_router,
    "heygen": heygen_router,
    "bannerbear": bannerbear_router,
    "uploadthing": uploadthing_router,
    "mail": mail_smtp_router,
    "neondb": neondb_router,
    "supabase": supabase_router,
    "duckduckgo": duckduckgo_router,
    "ipinfo": ipinfo_router,
    "hunterio": hunterio_router,
    "zip_code": zip_code_router
}



async def check_user_permission(request: Request, tool: str, method: str):
    try:
        
        if method in ['validate_key', 'test_connection']:  # skip this paths, reserved for validation checks
            return

        
        user_id = await get_user_from_request(request)
        user_tools = get_user_tools_from_actions(user_id)

        if not user_tools:
            raise HTTPException(status_code=401, detail="User not found")
        
        if tool not in user_tools:
            raise HTTPException(status_code=403, detail=f"Tool {tool} is not availiable for this user")
        if method not in user_tools[tool]:
            raise HTTPException(status_code=403, detail=f"Action {method} is not availiable for {tool} for this user")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking permissions: {str(e)}")


class PermissionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path.strip("/")
        segments = path.split("/")
        
        # Skip non-tool routes like root, healthcheck, etc.
        if segments and (segments[0] in INTEGRATION_ROUTERS or segments[0] == "tool-call"):
            if segments[0] == "tool-call" and len(segments) >= 3:
                tool, method = segments[1], segments[2]
            else:
                tool, method = segments[0], segments[1] if len(segments) > 1 else None

            if tool and method:
                try:
                    # pass
                    await check_user_permission(request, tool, method)
                except HTTPException as e:
                    if e.status_code in [401, 403]:
                        return JSONResponse(
                            status_code=e.status_code,
                            content={"detail": f"Method not available: {e.detail}"}
                        )
                    raise e

        # Proceed if allowed
        return await call_next(request)


app = FastAPI()

app.state.celery = celery_app

app.add_middleware(
    CORSMiddleware,
    allow_origins='*',
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(debug_router)
app.include_router(flow_router)

app.add_middleware(PermissionMiddleware)

for router in INTEGRATION_ROUTERS.values():
    app.include_router(router)

@app.get("/")
async def root():
    return {"message": "Hello World"}

## healthcheck route
@app.head("/")
async def root_head():
    try:
        start_time = time.time()
        
        # Take 3 random tools to check
        sample_tools = list(INTEGRATION_ROUTERS.keys())
        sample_tools = random.sample(sample_tools, 3)
        
        timings = {}
        for name in sample_tools:
            tool_start = time.time()
            router = INTEGRATION_ROUTERS[name]
            _ = get_router_tools(router)
            tool_end = time.time()
            timings[name] = round(tool_end - tool_start, 3)
            
        total_time = round(time.time() - start_time, 3)
        
        return Response(
            status_code=200,
            headers={
                "X-Healthcheck-Time": str(total_time),
                "X-Healthcheck-Tools": str(timings)
            }
        )
    except Exception as e:
        return Response(
            status_code=500,
            content=f"Tools check failed: {str(e)}"
        )

@app.get("/tools")
async def get_tools(simple_schema: bool = False, format: str = "default"):
    tools = {}
    for name, router in INTEGRATION_ROUTERS.items():
        tools[name] = get_router_tools(router)
      
    if simple_schema:
        return {"tools": convert_to_brief_format(tools)}
    
    return {"tools": tools}

def convert_to_brief_format(tools_dict):
    """
    Convert tools to a very brief format with structure:
    {
      "tools": {
        "tool_name": {
          "method_name": "description"
        }
      }
    }
    """
    brief_tools = {}
    
    for tool_name, tool_functions in tools_dict.items():
        brief_tools[tool_name] = {}
        
        for func in tool_functions:
            if func.get("type") == "function" and "function" in func:
                method_name = func["function"].get("name", "")
                description = func["function"].get("description", "")
                
                # Try to get a better description from examples if available
                if "examples" in func and func["examples"] and "description" in func["examples"][0]:
                    description = func["examples"][0]["description"]
                
                if method_name == 'validate_key':
                    continue
                
                brief_tools[tool_name][method_name] = description
    
    return brief_tools

def remove_components_recursively(obj):
    if isinstance(obj, dict):
        result = {k: remove_components_recursively(v) for k, v in obj.items() if (k not in ["component", "components", 'parameters', 'strict', 'properties', 'output_schema', 'input_schema', 'input_json', 'output_json', ''])}
        return result
    elif isinstance(obj, list):
        return [remove_components_recursively(item) for item in obj]
    else:
        return obj

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
    user_id = None
    
    user_id = await get_user_from_request(request)
        
    try:
        try:
            params = await request.json()
        except:
            params = {}
        
        if tool not in INTEGRATION_ROUTERS:
            error_message = f"Tool '{tool}' not found"
            raise HTTPException(status_code=404, detail=error_message)
        
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
                                error_message = f"Dependency resolution error: got Depends object instead of service instance"
                                raise ValueError(error_message)
                                
                            endpoint_args[name] = dependency_result
                        except Exception as dep_error:
                            error_message = f"Error resolving dependency {name}: {str(dep_error)}"
                            raise HTTPException(status_code=500, detail=error_message)
                
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
                    raise
                
                if not include_component:
                    if isinstance(response, dict) and "component" in response:
                        response.pop("component")
                    elif hasattr(response, "component") and hasattr(response, "dict"):
                        response_dict = response.dict()
                        if "component" in response_dict:
                            response_dict.pop("component")
                        return response_dict
                
                return response
        
        error_message = f"Method '{method}' not found in tool '{tool}'"
        raise HTTPException(status_code=404, detail=error_message)
    
    except HTTPException as http_exc:
        success = 0
        error_message = str(http_exc.detail)
        log_api_call(
            user_id=user_id,
            endpoint=f"/tool-call/{tool}/{method}",
            success=success,
            error_message=error_message
        )
        raise
    
    except Exception as exc:
        success = 0
        error_message = str(exc)
        log_api_call(
            user_id=user_id,
            endpoint=f"/tool-call/{tool}/{method}",
            success=success,
            error_message=error_message
        )
        raise HTTPException(status_code=500, detail=f"Internal server error: {error_message}")
    
    finally:
        if success == 1:
            try:
                log_api_call(
                    user_id=user_id,
                    endpoint=f"/tool-call/{tool}/{method}",
                    success=success,
                    error_message=None
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
        user_tools = get_user_tools_from_actions(user_id)
        
        if isinstance(user_tools, dict) and "error" in user_tools:
            raise Exception(user_tools["error"])
            
        if not user_tools:
            tools_response = {"tools": {}}
            tools_response["tools"]["examples"] = json.loads(get_tools_example_prompt_empty)
            tools_response["tools"]["memories"] = {}
            return tools_response
        
        response_tools = {"tools": user_tools}
        response_tools["tools"]["examples"] = json.loads(get_tools_example_prompt)
        
        user_memories = await get_user_memories(user_id)
        response_tools["tools"]["memories"] = user_memories
        
        log_api_call(
            user_id=user_id,
            endpoint="/get-tools",
            success=1
        )
        
        return response_tools
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
                
                user_tools[name] = provider_tools
        
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

@app.post("/tool-execute")
async def execute_tool_from_body(request: Request, include_component: bool = False):
    success = 0
    error_message = None
    user_id = None
    
    try:
        user_id = await get_user_from_request(request)
    except Exception as auth_error:
        log_api_call(
            user_id="anonymous",
            endpoint=f"/tool-execute",
            success=0,
            error_message=f"Authentication error: {str(auth_error)}"
        )
        raise HTTPException(status_code=401, detail=f"Invalid authentication: {str(auth_error)}")
        
    try:
        try:
            request_data = await request.json()
            print(request_data)
            tool = request_data.get("tool")
            method = request_data.get("method")
            params = request_data.get("params", request_data.get("parameters", {}))
            
            if not tool or not method:
                error_message = "Tool and method are required fields"
                raise HTTPException(status_code=400, detail=error_message)
                
        except Exception as e:
            error_message = f"Invalid request format: {str(e)}"
            raise HTTPException(status_code=400, detail=error_message)
        
        new_request = Request(scope=request.scope)
        new_request._json = params
        
        response = await handle_tool_call(tool=tool, method=method, request=new_request, include_component=include_component)
        success = 1
        return response
        
    except HTTPException as http_exc:
        success = 0
        error_message = str(http_exc.detail)
        log_api_call(
            user_id=user_id,
            endpoint=f"/tool-execute",
            success=success,
            error_message=error_message
        )
        raise
        
    except Exception as exc:
        success = 0
        error_message = str(exc)
        log_api_call(
            user_id=user_id,
            endpoint=f"/tool-execute",
            success=success,
            error_message=error_message
        )
        raise HTTPException(status_code=500, detail=f"Internal server error: {error_message}")
        
    finally:
        if success == 1:
            try:
                log_api_call(
                    user_id=user_id,
                    endpoint=f"/tool-execute",
                    success=success,
                    error_message=None
                )
            except Exception as log_error:
                print(f"Error logging API call for Supabase: {str(log_error)}")
