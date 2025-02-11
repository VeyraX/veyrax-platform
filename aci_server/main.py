from fastapi import FastAPI
from integrations.gmail.route import router as gmail_router

app = FastAPI()

app.include_router(gmail_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}
