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
from src.taxonomy import load_flatten_data
from src.catalogo_pull import download_cfdi_catalog
from src.pys_scraper import scrape_and_save_pys_catalog
from db import Base, ClaveProdServ, Classification
from sqlalchemy import Table, MetaData

from session import get_db, engine, SessionLocal    
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
        try:
            load_latest_catalog_to_db()
        except FileNotFoundError:
            logger.warning("No catalog files found during startup. Use /pull_pys_catalog to scrape new data.")


@app.get("/")
async def root():
    current_time = datetime.now().isoformat()
    logger.info("Root endpoint accessed")
    return {"message": "Hello World!", "timestamp": current_time}


@app.get("/health")
async def health():
    logger.info("Health check endpoint accessed")
    return JSONResponse(status_code=status.HTTP_200_OK, content={"status": "healthy"})


@app.get("/pull_taxonomy") # IDK what to do with this endpoint. It used to pull from output.json
async def pull_taxonomy():
    load_flatten_data()
    return JSONResponse(status_code=200, content={"message": "Taxonomy data pulled successfully"})


@app.get("/favicon.ico")
async def favicon():
    return JSONResponse(status_code=204, content={"status": "healthy"})


@app.get("/show_latest")
async def show_latest():
    """Show latest PYS catalog data and metadata"""
    raw_file_path = "/app/pys_catalog_latest.json"
    flattened_file_path = "/app/pys_flattened_latest.json"
    
    try:
        # Check if PYS catalog files exist
        if not os.path.exists(raw_file_path):
            return JSONResponse(
                status_code=404, 
                content={"error": "No PYS catalog found. Use /pull_pys_catalog to scrape data first."}
            )
        
        # Read the raw catalog file
        async with aiofiles.open(raw_file_path, "r", encoding="utf-8") as f:
            content = await f.read()
        data = json.loads(content)
        
        # Get file modification time
        created = datetime.fromtimestamp(os.path.getmtime(raw_file_path)).isoformat()
        
        # Extract metadata
        metadata = data.get("metadata", {})
        
        # Check if flattened file exists
        flattened_exists = os.path.exists(flattened_file_path)
        
        return {
            "date_pulled": created,
            "source": "PYS Catalog Scraper",
            "metadata": metadata,
            "files": {
                "raw_file": raw_file_path,
                "flattened_file": flattened_file_path,
                "flattened_exists": flattened_exists
            },
            "data_summary": {
                "total_types": metadata.get("total_types", 0),
                "total_segments": metadata.get("total_segments", 0),
                "total_families": metadata.get("total_families", 0),
                "total_classes": metadata.get("total_classes", 0)
            }
        }
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


@app.post("/pull_pys_catalog")
async def pull_pys_catalog():
    """Pull PYS catalog using the new scraping approach"""
    try:
        logger.info("Starting PYS catalog scraping")
        result = scrape_and_save_pys_catalog()
        logger.info(f"PYS catalog scraping completed: {result['metadata']}")
        return JSONResponse(
            status_code=200, 
            content={
                "message": "PYS catalog scraped successfully",
                "raw_file": result["raw_file"],
                "flattened_file": result["flattened_file"],
                "metadata": result["metadata"]
            }
        )
    except Exception as e:
        logger.error(f"Error scraping PYS catalog: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/test_pys_scraper")
async def test_pys_scraper():
    """Test the PYS scraper with basic functionality"""
    try:
        from src._scraper import obtain_types
        logger.info("Testing PYS scraper basic functionality")
        types = obtain_types()
        return JSONResponse(
            status_code=200,
            content={
                "message": "PYS scraper test successful",
                "types_count": len(types),
                "sample_types": dict(list(types.items())[:3])
            }
        )
    except Exception as e:
        logger.error(f"Error testing PYS scraper: {e}")
        return JSONResponse(
            status_code=500, 
            content={
                "error": str(e),
                "message": "PYS scraper test failed. The SAT website might be temporarily unavailable."
            }
        )


@app.get("/cleanup_pys_files")
async def cleanup_pys_files():
    """Clean up old PYS catalog files, keeping only the latest ones"""
    try:
        from src.pys_scraper import cleanup_old_files
        cleanup_old_files()
        return JSONResponse(
            status_code=200,
            content={"message": "Old PYS files cleaned up successfully"}
        )
    except Exception as e:
        logger.error(f"Error cleaning up PYS files: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


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
