from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import json
import os
import aiofiles
import asyncio
import threading
import logging

from src.generator import pull_json
from src.generator import is_pull_locked


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("app.log")],
)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    current_time = datetime.now().isoformat()
    logger.info("Root endpoint accessed")
    return {"message": "Hello World!", "timestamp": current_time}

@app.get("/health")
async def health():
    logger.info("Health check endpoint accessed")
    return JSONResponse(status_code=status.HTTP_200_OK, content={"status": "healthy"})

@app.get("/pull_json")
async def pull_json_endpoint():
    current_time = datetime.now().isoformat()
    logger.info("Pull JSON endpoint accessed")
    is_locked = is_pull_locked()
    if is_locked['locked']:
        return {"Message": "Can't trigger a new pull rightnow", "reason": is_locked['reason']}
    pull_json_thread = threading.Thread(target=pull_json)
    pull_json_thread.start()
    return {"message": "JSON pulled triggered", "timestamp": current_time}



@app.get("/pull_json_forced")
async def pull_json_endpoint():
    current_time = datetime.now().isoformat()
    logger.info("Pull JSON endpoint by forced, accessed")
    pull_json_thread = threading.Thread(target=pull_json)
    pull_json_thread.start()
    return {"message": "JSON pulled triggered, forced the execution", "timestamp": current_time}

@app.get("/favicon.ico")
async def favicon():
    return JSONResponse(status_code=204)

@app.get("/show_latest")
async def show_latest():
    file_path = "/app/output.json"
    try:
        if not os.path.exists(file_path):
            return JSONResponse(status_code=404, content={"error": "File not found"})
        async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
            content = await f.read()
        data = json.loads(content)
        created = datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
        return {"date_pulled": created, "data": data}
    except json.JSONDecodeError as e:
        return JSONResponse(status_code=400, content={"error": f"Invalid JSON: {str(e)}"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting application server")
    uvicorn.run(app, host="0.0.0.0", port=8080, reload=True, log_level="debug")
