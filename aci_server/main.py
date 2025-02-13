from fastapi import FastAPI
from integrations.gmail.route import router as gmail_router
from integrations.google_calendar.route import router as google_calendar_router
from integrations.notion.route import router as notion_router
from integrations.slack.route import router as slack_router
from integrations.linear.route import router as linear_router
from integrations.openweather.route import router as openweather_router
from integrations.common.utils import get_router_tools

app = FastAPI()

app.include_router(gmail_router)
app.include_router(google_calendar_router)
app.include_router(notion_router)
app.include_router(slack_router)
app.include_router(linear_router)
app.include_router(openweather_router)
@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/tools")
async def get_tools():
    routers = [gmail_router, google_calendar_router, notion_router, slack_router, linear_router, openweather_router]
    
    tools = {}
    for router in routers:
        if router.tags and len(router.tags) > 0:
            integration_name = router.tags[0].lower()
            tools[integration_name] = get_router_tools(router)
    
    return {"tools": tools}