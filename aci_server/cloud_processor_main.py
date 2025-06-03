from fastapi import FastAPI
from typing import Dict, Any
import logging
import os

app = FastAPI(title="Fild Cloud Processor", version="1.0.0")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/process-batch")
async def process_batch_endpoint(batch_data: Dict[str, Any]) -> Dict[str, Any]:
    try:
        from fild.cloud_processor import process_batch
        result = await process_batch(batch_data)
        return result
    except Exception as e:
        logging.exception(f"Error in process-batch endpoint: {e}")
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port) 