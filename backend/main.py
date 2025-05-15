from fastapi import FastAPI, status, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import or_
from sqlalchemy import func

from sqlalchemy.orm import Session
from sqlalchemy import cast, Integer, text

from datetime import datetime
import json
import os
import aiofiles
import threading
import logging

from src.generator import pull_json
from src.generator import is_pull_locked
from src.catalogo_pull import download_cfdi_catalog
from db import Base, ClaveProdServ, Classification
from sqlalchemy import Table, MetaData

from session import get_db, engine, SessionLocal
from src.taxonomy import load_flatten_data
from src.catalogo_pull import load_latest_catalog_to_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - LINE %(lineno)d - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)
metadata = MetaData()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    with SessionLocal() as db:
        db.query(Classification).delete()
        load_flatten_data()
        load_latest_catalog_to_db()


@app.get("/")
async def root():
    current_time = datetime.now().isoformat()
    logger.info("Root endpoint accessed")
    return {"message": "Hello World!", "timestamp": current_time}


@app.get("/health")
async def health():
    logger.info("Health check endpoint accessed")
    return JSONResponse(status_code=status.HTTP_200_OK, content={"status": "healthy"})


@app.get("/pull_taxonomy")
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


@app.post("/pull_catalogo/{date_str}")
async def pull_catalogo(date_str: str):
    catalog = download_cfdi_catalog(date_str)
    if catalog["success"]:
        return JSONResponse(status_code=200, content={"message": catalog["reason"]})
    if not catalog["success"] and catalog["reason"] == "Not a valid date":
        return JSONResponse(status_code=404, content={"error": "Date not found on SAT"})

    return JSONResponse(status_code=500, content={"error": "server error"})


@app.get("/load_db")
async def load_db(db: Session = Depends(get_db)):
    db.query(Classification).delete()
    load_flatten_data()
    load_latest_catalog_to_db()
    classification_count = db.query(Classification).count()
    clave_prod_serv_count = db.query(ClaveProdServ).count()
    return {"classification_count": classification_count, "clave_prod_serv_count": clave_prod_serv_count}


@app.get("/search_clave_prod_and_taxonomy")
async def search_clave_prod_and_taxonomy(q: str, db: Session = Depends(get_db)):
    search_term_full = q.lower()
    words_in_search = q.lower().split()

    try:
        full_ids = db.execute(
            text("SELECT c_ClaveProdServ FROM clave_prod_serv_fts WHERE clave_prod_serv_fts MATCH :match"),
            {"match": f'"{search_term_full}"'}
        ).fetchall()
        full_ids = [x[0] for x in full_ids]
    except Exception:
        db.rollback()
        full_ids = []

    results = db.query(ClaveProdServ, Classification).join(
        Classification,
        cast(ClaveProdServ.c_ClaveProdServ / 100, Integer) == Classification.Clase_num
    ).filter(
        ClaveProdServ.c_ClaveProdServ.in_(full_ids)
    ).all()

    exact_result = []
    for prod, cls in results:
        exact_result.append({
            "c_ClaveProdServ": prod.c_ClaveProdServ,
            "Descripcion": prod.Descripcion,
            "Palabras_similares": prod.Palabras_similares,
            "tipo_num": cls.tipo_num,
            "Tipo": cls.Tipo,
            "Div_num": cls.Div_num,
            "Division": cls.Division,
            "Grupo_num": cls.Grupo_num,
            "Grupo": cls.Grupo,
            "Clase_num": cls.Clase_num,
            "Clase": cls.Clase
        })

    partial_ids = set()
    try:
        for word in words_in_search:
            ids = db.execute(
                text("SELECT c_ClaveProdServ FROM clave_prod_serv_fts WHERE clave_prod_serv_fts MATCH :match"),
                {"match": word}
            ).fetchall()
            partial_ids.update([x[0] for x in ids])
    except Exception:
        db.rollback()
        partial_ids = set()

    partial_ids.difference_update({r["c_ClaveProdServ"] for r in exact_result})

    results = db.query(ClaveProdServ, Classification).join(
        Classification,
        cast(ClaveProdServ.c_ClaveProdServ / 100, Integer) == Classification.Clase_num
    ).filter(
        ClaveProdServ.c_ClaveProdServ.in_(partial_ids)
    ).all()

    or_results = []
    for prod, cls in results:
        or_results.append({
            "c_ClaveProdServ": prod.c_ClaveProdServ,
            "Descripcion": prod.Descripcion,
            "Palabras_similares": prod.Palabras_similares,
            "tipo_num": cls.tipo_num,
            "Tipo": cls.Tipo,
            "Div_num": cls.Div_num,
            "Division": cls.Division,
            "Grupo_num": cls.Grupo_num,
            "Grupo": cls.Grupo,
            "Clase_num": cls.Clase_num,
            "Clase": cls.Clase
        })

    return exact_result + or_results


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting application server")
    uvicorn.run(app, host="0.0.0.0", port=8080, reload=True, log_level="debug")
