from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import json
import os
import aiofiles
import asyncio
from src import pull_json
import threading

app = FastAPI()

# Global lock flag to prevent concurrent pulls
pull_in_progress = False
pull_lock = threading.Lock()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """
    Return the current timestamp as a hello world response.
    """
    current_time = datetime.now().isoformat()
    return {"message": "Hello World!", "timestamp": current_time}

@app.get("/health")
async def health():
    """
    Health check endpoint
    """
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "healthy"}
    )

@app.get("/hello_world")
async def hello_world():
    """
    Hello world endpoint
    """
    current_time = datetime.now().isoformat()
    return {"message": "Hello World!", "timestamp": current_time}

@app.get("/show_latest")
async def show_latest():
    """
    Returns the content of /app/output.json using async I/O
    """
    file_path = '/app/output.json'
    try:
        if not os.path.exists(file_path):
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"error": f"File {file_path} does not exist", "timestamp": datetime.now().isoformat()}
            )
        
        # Use async file operations
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
            content = await f.read()
        
        # Parse JSON in a separate thread to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: json.loads(content))
        
        return data
    except json.JSONDecodeError as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": f"Invalid JSON format: {str(e)}", "timestamp": datetime.now().isoformat()}
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": str(e), "timestamp": datetime.now().isoformat()}
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
    