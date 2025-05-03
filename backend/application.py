from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

# Add CORS middleware to allow cross-origin requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def hello_world():
    """
    Return the current timestamp as a hello world response.
    """
    current_time = datetime.now().isoformat()
    return {"message": "Hello World!", "timestamp": current_time}

@app.get("/")
async def root():
    """
    Root endpoint that redirects to hello_world.
    """
    return {"message": "Welcome to the API. Try /hello_world endpoint."}

# @app.get("/pull_fresh")
# async def pull_fresh():
#     """
#     Triggers the pull_json function to generate and save fresh data to /app/output.json
#     Uses a lock to prevent concurrent pulls
#     """
#     global pull_in_progress
    
#     # Check if pull is already in progress
#     with pull_lock:
#         if pull_in_progress:
#             return {"message": "Data pull already in progress", "timestamp": datetime.now().isoformat()}
#         else:
#             pull_in_progress = True
    
#     try:
#         result = pull_json('/app/output.json')
#         return {"message": "Data successfully pulled and saved to /app/output.json", "timestamp": datetime.now().isoformat()}
#     except Exception as e:
#         return {"error": str(e), "timestamp": datetime.now().isoformat()}
#     finally:
#         # Release the lock when done
#         with pull_lock:
#             pull_in_progress = False

@app.get("/show_latest")
async def show_latest():
    """
    Returns the content of /app/output.json using async I/O
    """
    file_path = '/app/output.json'
    try:
        if not os.path.exists(file_path):
            return {"error": f"File {file_path} does not exist", "timestamp": datetime.now().isoformat()}
        
        # Use async file operations
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
            content = await f.read()
        
        # Parse JSON in a separate thread to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: json.loads(content))
        
        return data
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON format: {str(e)}", "timestamp": datetime.now().isoformat()}
    except Exception as e:
        return {"error": str(e), "timestamp": datetime.now().isoformat()}
    


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

