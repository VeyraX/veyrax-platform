from fastapi import FastAPI
from integrations.gmail.route import router as gmail_router
from integrations.google_calendar.route import router as google_calendar_router
from integrations.common.utils import get_router_tools

app = FastAPI()

app.include_router(gmail_router)
app.include_router(google_calendar_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/tools")
async def get_tools():
    routers = [gmail_router, google_calendar_router]
    
    tools = {}
    for router in routers:
        if router.tags and len(router.tags) > 0:
            integration_name = router.tags[0].lower()
            tools[integration_name] = get_router_tools(router, integration_name)
    
    return {"tools": tools}