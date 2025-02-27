from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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
from vector_tools.route import router as vector_router
from integrations.common.utils import get_router_tools
from celery_app import celery_app

import os
import importlib
import json
import inspect

load_dotenv()


app = FastAPI()

app.state.celery = celery_app

app.add_middleware(
    CORSMiddleware,
    allow_origins='*',
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(gmail_router)
app.include_router(google_calendar_router)
app.include_router(notion_router)
app.include_router(slack_router)
app.include_router(linear_router)
app.include_router(openweather_router)
app.include_router(perplexity_router)
app.include_router(google_drive_router)
app.include_router(vector_router)
app.include_router(jira_router)
app.include_router(confluence_router)
app.include_router(outlook_router)
app.include_router(dropbox_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/tools")
async def get_tools():
    # routers = [google_calendar_router]
    routers = [gmail_router, google_calendar_router, notion_router, slack_router, linear_router, openweather_router, perplexity_router, google_drive_router, jira_router, confluence_router, outlook_router, dropbox_router]
    
    tools = {}
    for router in routers:
        if router.tags and len(router.tags) > 0:
            integration_name = router.tags[0].lower()
            tools[integration_name] = get_router_tools(router)
    
    return {"tools": tools}

@app.post("/tool-call/{tool}/{method}")
async def handle_tool_call(tool: str, method: str, request: Request):
    # Получаем параметры из тела запроса
    try:
        params = await request.json()
    except:
        params = {}
    
    # Находим нужный роутер
    integration_routers = {
        "gmail": gmail_router,
        "google_calendar": google_calendar_router,
        "notion": notion_router,
        "slack": slack_router,
        "linear": linear_router,
        "openweather": openweather_router,
        "perplexity": perplexity_router,
        "google_drive": google_drive_router,
        "jira": jira_router,
        "confluence": confluence_router,
        "outlook": outlook_router,
        "dropbox": dropbox_router
    }
    
    if tool not in integration_routers:
        raise HTTPException(status_code=404, detail=f"Tool '{tool}' not found")
    
    router = integration_routers[tool]
    
    for route in router.routes:
        if route.name == method:
            # Используем inspect для получения информации о параметрах эндпоинта
            signature = inspect.signature(route.endpoint)
            
            # Создаем словарь для аргументов, которые передадим в endpoint
            endpoint_args = {}
            
            # Добавляем параметры из запроса
            for name, param in signature.parameters.items():
                if name in params:
                    endpoint_args[name] = params[name]
            
            # Создаем зависимости
            for name, param in signature.parameters.items():
                if name not in endpoint_args:
                    # Проверяем, есть ли у параметра значение по умолчанию и является ли оно Depends
                    if param.default != inspect.Parameter.empty and hasattr(param.default, "__class__") and param.default.__class__.__name__ == "Depends":
                        dep_func = param.default.dependency
                        try:
                            # Создаем зависимость и сохраняем её с именем параметра функции
                            endpoint_args[name] = await dep_func(request)
                        except Exception as e:
                            print(f"Error resolving dependency {name}: {str(e)}")
            
            # Вызываем эндпоинт с нужными аргументами
            return await route.endpoint(**endpoint_args)
    
    raise HTTPException(status_code=404, detail=f"Method '{method}' not found in tool '{tool}'")