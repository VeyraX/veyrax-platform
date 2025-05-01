from fastapi import Request, HTTPException, Body
from typing import Dict, Any, List, Optional, Callable, Union, Type
from db.supabase import get_supabase
import asyncio
import inspect
import httpx
import traceback
import os
import json
import openai
import posthog
from posthog.ai.openai import AsyncOpenAI as PosthogAsyncOpenAI
from datetime import date
from integrations.common.utils import log_api_call
from integrations.common.auth import get_user_from_request
from mcp_deployment.queries import get_user_mcp_image_names, get_user_connected_mcp_actions
from prompts import get_parameter_generation_prompt

class ToolsService:
    def __init__(self, integration_routers: Dict[str, Any]):
        self.integration_routers = integration_routers
        self.mcp_api_url = os.getenv("VEYRAX_DEPLOY_API_URL")
        if not self.mcp_api_url:
            self.mcp_api_url = ""
            print("Warning: VEYRAX_DEPLOY_API_URL environment variable is not set")
    
    async def _generate_params_with_llm(self, tool: str, method: str, question: str, tool_schema: dict, user_id: str) -> dict:
        prompt = get_parameter_generation_prompt(tool, method, question, tool_schema)
        
        try:
            api_key = os.getenv("OPENROUTER_API_KEY")
            if not api_key:
                raise ValueError("OPENROUTER_API_KEY is not configured")
            
            posthog_api_key = os.getenv("POSTHOG_API_KEY")
            posthog_host = os.getenv("POSTHOG_HOST", "https://us.i.posthog.com")
            posthog_client = None
            if posthog_api_key:
                posthog.project_api_key = posthog_api_key
                posthog.host = posthog_host
                posthog_client = posthog
                print("PostHog Observability enabled for LLM parameter generation.")
            else:
                print("Warning: POSTHOG_API_KEY not set. PostHog Observability for LLM parameter generation is disabled.")
            
            client = PosthogAsyncOpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key,
                posthog_client=posthog_client
            )
            
            custom_properties = {
                "endpoint": "tool-call-simplified",
                "tool_name": tool,
                "tool_method": method,
                "user_question": question[:400],
                "user_id": user_id
            }
            
            completion = await client.chat.completions.create(
                model="openai/gpt-4.1",
                messages=[
                    {"role": "system", "content": "You are an expert API parameter generator. When receiving a query, carefully analyze and reason through the user's intent. Consider the logical context provided by the intelligent AI agent. Your goal is to identify and produce the optimal JSON parameters that will effectively solve the user's request based on the given tool schema. Respond strictly with a JSON object containing these parameters."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0,
                posthog_properties=custom_properties,
                posthog_distinct_id=user_id # Use distinct_id for user identification
            )

            if (completion is None) or (completion.choices is None) or (isinstance(completion.choices, list) and len(completion.choices) == 0):
                return {}
            
            generated_params_json = completion.choices[0].message.content
            
            if not generated_params_json:
                 return {}
                 
            return json.loads(generated_params_json)
            
        except json.JSONDecodeError as json_err:
            raise HTTPException(status_code=500, detail=f"LLM failed to generate valid JSON parameters. Response: {generated_params_json}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"LLM parameter generation failed: {str(e)}")

    async def handle_simplified_tool_call(
        self, 
        tool: str, 
        method: str, 
        question: str, 
        request: Request
    ) -> Dict[str, Any]:
        try:
            user_id = await get_user_from_request(request)
            
            tool_spec_full = await self.get_tool_spec(tool, request)
            tool_actions = tool_spec_full.get("tools", {})
            method_schema = None

            if isinstance(tool_actions, dict):
                if method in tool_actions:
                    method_schema = tool_actions[method]
            elif isinstance(tool_actions, list):
                for action in tool_actions:
                    if isinstance(action, dict) and action.get("type") == "function":
                        func_details = action.get("function", {})
                        if func_details.get("name") == method:
                            method_schema = action
                            break
                            
            if not method_schema:
                raise HTTPException(status_code=404, detail=f"Method '{method}' not found in tool '{tool}' schema.")


            print("[debug] method_schema: ", method_schema)
            # Pass user_id to the LLM function
            generated_params = await self._generate_params_with_llm(tool, method, question, method_schema, user_id)

            print("[debug] generated_params: ", generated_params)

            new_scope = dict(request.scope)
            new_scope['method'] = 'POST'
            
            async def receive():
                 return {"type": "http.request", "body": json.dumps(generated_params).encode('utf-8'), "more_body": False}

            new_request = Request(scope=new_scope, receive=receive)
            
            new_request._json = generated_params 

            metadata = {
                "parameters": generated_params,
                "question": question,
                "simplified": True
            }

            response = await self.handle_tool_call(tool=tool, method=method, request=new_request, include_component=False, skip_logging=True)
            
            self._log_api_call(
                user_id=user_id,
                endpoint=f"/tool-call-simplified/{tool}/{method}",
                success=1,
                error_message=None,
                metadata=metadata
            )
            
            return response

        except HTTPException as e:
            user_id_on_error = await get_user_from_request(request) 

            metadata = {
                "parameters": {},
                "question": question,
                "simplified": True
            }
            self._log_api_call(
                user_id=user_id_on_error,
                endpoint=f"/tool-call-simplified/{tool}/{method}",
                success=0,
                error_message=str(e.detail),
                metadata=metadata
            )
            raise e
        except Exception as e:
            user_id_on_error = await get_user_from_request(request)
            
            metadata = {
                "parameters": {},
                "question": question,
                "simplified": True
            }
            self._log_api_call(
                user_id=user_id_on_error,
                endpoint=f"/tool-call-simplified/{tool}/{method}",
                success=0,
                error_message=str(e),
                metadata=metadata
            )
            print(f"Error in simplified tool call processing: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to execute simplified tool call: {str(e)}")

    async def handle_tool_call(
        self, 
        tool: str, 
        method: str, 
        request: Request, 
        include_component: bool = True,
        skip_logging: bool = False
    ) -> Dict[str, Any]:
        success = 0
        response = None
        error_message = None
        user_id = None
        
        query_params = dict(request.query_params)
        question = query_params.get("question")
        
        try:
            user_id = await get_user_from_request(request)
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Invalid authentication: {str(e)}")
            
        try:
            try:
                params = await request.json()
            except:
                params = {}
            
            metadata = {
                "parameters": params,
                "question": question
            }
            
            if tool in self.integration_routers:
                response = await self._handle_integration_tool(tool, method, request, params, include_component)
                success = 1
                return response
            
            else:
                mcp_image_names = await get_user_mcp_image_names(user_id)
                
                if tool in mcp_image_names:
                    response = await self._handle_mcp_tool(tool, method, params, request)
                    success = 1
                    return response
                
                error_message = f"Tool '{tool}' not found or not available for this user"
                raise HTTPException(status_code=404, detail=error_message)
        
        except HTTPException as http_exc:
            success = 0
            error_message = str(http_exc.detail)
            if not skip_logging:
                self._log_api_call(
                    user_id=user_id,
                    endpoint=f"/tool-call/{tool}/{method}",
                    success=success,
                    error_message=error_message,
                    metadata=metadata
                )
            raise
        
        except Exception as exc:
            success = 0
            error_message = str(exc)
            if not skip_logging:
                self._log_api_call(
                    user_id=user_id,
                    endpoint=f"/tool-call/{tool}/{method}",
                    success=success,
                    error_message=error_message,
                    metadata=metadata
                )
            raise HTTPException(status_code=500, detail=f"Internal server error: {error_message}")
        
        finally:
            if success == 1 and not skip_logging:
                try:
                    self._log_api_call(
                        user_id=user_id,
                        endpoint=f"/tool-call/{tool}/{method}",
                        success=success,
                        error_message=None,
                        metadata=metadata
                    )
                except Exception as log_error:
                    print(f"Error logging API call for Supabase: {str(log_error)}")
    
    async def _handle_integration_tool(
        self, 
        tool: str, 
        method: str, 
        request: Request, 
        params: Dict[str, Any],
        include_component: bool
    ) -> Dict[str, Any]:
        router = self.integration_routers[tool]
        
        from integrations.common.route_identifier import route_method
        
        for route in router.routes:
            if route_method(route) == method:
                signature = inspect.signature(route.endpoint)
                
                endpoint_args = {}
                
                for name, param in signature.parameters.items():
                    if param.default != inspect.Parameter.empty and hasattr(param.default, "__class__") and param.default.__class__.__name__ == "Depends":
                        dep_func = param.default.dependency
                        try:
                            async def resolve_dependency_recursively(dep_func, req):
                                sig = inspect.signature(dep_func)
                                dep_args = {}
                                
                                for dep_name, dep_param in sig.parameters.items():
                                    if dep_param.default != inspect.Parameter.empty and hasattr(dep_param.default, "__class__") and dep_param.default.__class__.__name__ == "Depends":
                                        nested_dep_func = dep_param.default.dependency
                                        dep_args[dep_name] = await resolve_dependency_recursively(nested_dep_func, req)
                                    elif dep_name == "request":
                                        dep_args[dep_name] = req
                                
                                if asyncio.iscoroutinefunction(dep_func):
                                    return await dep_func(**dep_args)
                                else:
                                    return dep_func(**dep_args)
                            
                            dependency_result = await resolve_dependency_recursively(dep_func, request)
                            
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
                except Exception as exc:
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
    
    async def _handle_mcp_tool(
        self, 
        tool: str, 
        method: str, 
        params: Dict[str, Any],
        request: Request
    ) -> Dict[str, Any]:
        try:
            payload = {
                "mcp_name": tool,
                "tool_name": method,
                "parameters": params
            }
            
            headers = {}
            auth_header = request.headers.get("Authorization")
            veyrax_api_key = request.headers.get("VEYRAX_API_KEY")
            
            if auth_header:
                headers["Authorization"] = auth_header
            if veyrax_api_key:
                headers["VEYRAX_API_KEY"] = veyrax_api_key
            
            async with httpx.AsyncClient() as client:
                base_url = self.mcp_api_url or ""
                endpoint = "/call_mcp_tool"
                full_url = f"{base_url.rstrip('/')}{endpoint}"
                
                response = await client.post(
                    full_url,
                    json=payload,
                    headers=headers,
                    timeout=60.0
                )
                
                response.raise_for_status()
                
                return {
                    "data": response.json(),
                    "component": None
                }
        
        except httpx.HTTPStatusError as e:
            try:
                error_detail = e.response.json()
                error_message = error_detail.get("detail", str(e))
            except:
                error_message = f"MCP tool error: {str(e)}"
            
            raise HTTPException(
                status_code=e.response.status_code,
                detail=error_message
            )
        
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error connecting to MCP deployment service: {str(e)}"
            )
        
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error processing MCP tool request: {str(e)}"
            )
    
    def _log_api_call(self, user_id: str, endpoint: str, success: int, error_message: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None):
        try:
            log_api_call(
                user_id=user_id,
                endpoint=endpoint,
                success=success,
                error_message=error_message,
                metadata=metadata
            )
        except Exception as e:
            print(f"Error logging API call: {str(e)}")
    
    async def get_tool_spec(self, tool_name: str, request: Request) -> Dict[str, Any]:
        from integrations.common.utils import get_router_tools
        
        if tool_name in self.integration_routers:
            router = self.integration_routers[tool_name]
            return {"tools": get_router_tools(router)}
        
        try:
            user_id = await get_user_from_request(request)
            
            mcp_actions = await get_user_connected_mcp_actions(user_id)
            
            if tool_name in mcp_actions:
                return {"tools": mcp_actions[tool_name]}
        except Exception as e:
            pass
            
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")