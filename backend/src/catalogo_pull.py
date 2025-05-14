import os
import logging
import pandas as pd
import requests
from datetime import datetime
from session import with_db
from db import ClaveProdServ
import unicodedata

logger = logging.getLogger(__name__)


def download_cfdi_catalog(date_str):
    xls_filename = f"catCFDI_V_4_{date_str}.xls"
    xls_path = f"/app/{xls_filename}"

    if not os.path.isfile(xls_path):
        url = f"http://omawww.sat.gob.mx/tramitesyservicios/Paginas/documentos/{xls_filename}"
        response = requests.get(url)
        if response.status_code == 404:
            return {"success": False, "reason": "Not a valid date"}
        try:
            response.raise_for_status()
            with open(xls_path, "wb") as f:
                f.write(response.content)
        except Exception as e:
            logger.error(f"Failed to download Excel file: {e}")
            return {"success": False, "reason": e}

    return {"success": True, "reason": "file already exists"}


def remove_accents(text):
    if not isinstance(text, str):
        return ''
    new_text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('utf-8')
    new_text = new_text.replace('ñ', '')
    if text != new_text:
        return new_text

    return ''


def transform_to_parquet(date_str):
    xls_filename = f"catCFDI_V_4_{date_str}.xls"
    xls_path = f"/app/{xls_filename}"
    parquet_filename = f"catalogo_{date_str}.parquet"
    parquet_path = f"/app/{parquet_filename}"

    excel_data = pd.ExcelFile(xls_path)
    df = pd.read_excel(excel_data, sheet_name="c_ClaveProdServ", skiprows=4)
    df.columns = [
        'c_ClaveProdServ',
        'Descripcion',
        'Incluir_IVA_trasladado',
        'Incluir_IEPS_trasladado',
        'Complemento_que_debe_incluir',
        'FechaInicioVigencia',
        'FechaFinVigencia',
        'Estimulo_Franja_Fronteriza',
        'Palabras_similares',
    ]

    df['FechaInicioVigencia'] = pd.to_datetime(df['FechaInicioVigencia'], errors='coerce')
    df['FechaFinVigencia'] = pd.to_datetime(df['FechaFinVigencia'], errors='coerce')
    df['FechaInicioVigencia'] = df['FechaInicioVigencia'].apply(lambda x: x if pd.notna(x) else None)
    df['FechaFinVigencia'] = df['FechaFinVigencia'].apply(lambda x: x if pd.notna(x) else None)

    df['c_ClaveProdServ'] = pd.to_numeric(df['c_ClaveProdServ'], errors='coerce')
    df['Combined'] = (
            df['Descripcion'].fillna('').astype(str) + ' ' +
            df['Palabras_similares'].fillna('').astype(str) + ' ' +
            df['Descripcion'].fillna('').apply(remove_accents).astype(str) + ' ' +
            df['Palabras_similares'].fillna('').apply(remove_accents).astype(str)
    )

    df.to_parquet(parquet_path, index=False)

    logger.info(f"Success: saved as {parquet_filename}")
    logger.info(f"Represents data from: {date_str}")
    logger.info(f"Pulled on: {datetime.now().isoformat()}")

    return parquet_path


@with_db
def load_latest_catalog_to_db(*, db):
    files = [f for f in os.listdir("/app") if f.startswith("catalogo_") and f.endswith(".parquet")]
    if not files:
        raise FileNotFoundError("No catalog files found")

    latest_file = max(files, key=str)
    latest_date = latest_file.split("_")[1].split(".")[0]

    transform_to_parquet(latest_date)

    df = pd.read_parquet(f"/app/{latest_file}")
    records = df.to_dict(orient="records")

    db.query(ClaveProdServ).delete()
    db.bulk_insert_mappings(ClaveProdServ, records)
    db.commit()

    return {"success": True, "date": latest_date}
