from fastapi import FastAPI, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import json
import os
import aiofiles
import threading
import logging

from src.generator import pull_json
from src.generator import is_pull_locked
from src.catalogo_pull import fetch_cfdi_catalog_by_date
from db import Base, ClaveProdServ, Clasificacion

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - LINE %(lineno)d - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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
    if is_locked["locked"]:
        return {
            "Message": "Can't trigger a new pull rightnow",
            "reason": is_locked["reason"],
        }
    pull_json_thread = threading.Thread(target=pull_json)
    pull_json_thread.start()
    return {"message": "JSON pulled triggered", "timestamp": current_time}


@app.get("/pull_json_forced")
async def pull_json_forced_endpoint():
    current_time = datetime.now().isoformat()
    logger.info("Pull JSON endpoint by forced, accessed")
    pull_json_thread = threading.Thread(target=pull_json)
    pull_json_thread.start()
    return {
        "message": "JSON pulled triggered, forced the execution",
        "timestamp": current_time,
    }


@app.get("/favicon.ico")
async def favicon():
    return JSONResponse(status_code=204, content={"status": "healthy"})


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
        return JSONResponse(
            status_code=400, content={"error": f"Invalid JSON: {str(e)}"}
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/search")
async def search_catalog(q: str):
    with open("output.json", encoding="utf-8") as f:
        data = json.load(f)
    matches = []
    for tipo in data:
        for div in tipo.get("segments", []):
            for grupo in div.get("families", []):
                for clase in grupo.get("classes", []):
                    if q.lower() in clase["name"].lower():
                        matches.append(
                            {
                                "tipo_num": tipo["key"],
                                "tipo": tipo["name"],
                                "div_num": div["key"],
                                "division": div["name"],
                                "grupo_num": grupo["key"],
                                "grupo": grupo["name"],
                                "clase_num": clase["key"],
                                "clase": clase["name"],
                            }
                        )
    return matches


@app.post("/pull_catalogo/{date_str}")
async def pull_catalogo(date_str: str):
    catalog = fetch_cfdi_catalog_by_date(date_str)
    if catalog["success"]:
        return JSONResponse(status_code=200, content={"message": catalog["reason"]})
    if not catalog["success"] and catalog["reason"] == "Not a valid date":
        return JSONResponse(status_code=404, content={"error": "Date not found on SAT"})

    return JSONResponse(status_code=500, content={"error": "server error"})


@app.get("/api/clave_prod_serv")
def get_clave_prod_serv(db: Session = Depends(get_db)):
    results = db.query(ClaveProdServ).limit(10).all()
    return [r.__dict__ for r in results]


@app.get("/api/clasificacion")
def get_clasificacion(db: Session = Depends(get_db)):
    results = db.query(Clasificacion).limit(10).all()
    return [r.__dict__ for r in results]


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting application server")
    uvicorn.run(app, host="0.0.0.0", port=8080, reload=True, log_level="debug")
