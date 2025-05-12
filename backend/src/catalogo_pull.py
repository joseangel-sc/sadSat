import os
import logging
import pandas as pd
import requests
from datetime import datetime

logger = logging.getLogger(__name__)


def fetch_cfdi_catalog_by_date(date_str):
    xls_filename = f"catCFDI_V_4_{date_str}.xls"
    xls_path = f"/app/{xls_filename}"
    parquet_filename = f"catalogo_{date_str}.parquet"
    parquet_path = f"/app/{parquet_filename}"

    if os.path.isfile(parquet_path):
        mtime = datetime.fromtimestamp(os.path.getmtime(parquet_path))
        logger.info(f"File already exists: {parquet_filename}")
        logger.info(f"Represents data from: {date_str}")
        logger.info(f"Pulled on: {mtime.isoformat()}")
        return {"success": True, "reason": "Pull for date already on the system"}

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
            return {"error": e}

    excel_data = pd.ExcelFile(xls_path)
    df = pd.read_excel(excel_data, sheet_name="c_ClaveProdServ", skiprows=4)
    df.to_parquet(parquet_path, index=False)
    logger.info(f"Success: saved as {parquet_filename}")
    logger.info(f"Represents data from: {date_str}")
    logger.info(f"Pulled on: {datetime.now().isoformat()}")
    return {"success": True, "reason": "New file pulled"}


