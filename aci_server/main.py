from fastapi import FastAPI
from integrations.gmail.route import router as gmail_router
from integrations.google_calendar.route import router as google_calendar_router

app = FastAPI()

app.include_router(gmail_router)
app.include_router(google_calendar_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}