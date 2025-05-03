from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import json

app = FastAPI()

# Add CORS middleware to allow cross-origin requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/hello_world")
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

