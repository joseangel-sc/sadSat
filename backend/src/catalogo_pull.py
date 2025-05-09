from datetime import datetime, timedelta
import pandas as pd
import requests
from io import BytesIO
import os

def fetch_latest_cfdi_catalog_sheet(local_dir="."):
    today = datetime.today()
    base_url = "http://omawww.sat.gob.mx/tramitesyservicios/Paginas/documentos/catCFDI_V_4_{}.xls"
    for delta in range(90):
        date_str = (today - timedelta(days=delta)).strftime('%Y%m%d')
        filename = f"catCFDI_V_4_{date_str}.xls"
        local_path = os.path.join(local_dir, filename)
        parquet_path = os.path.join(local_dir, "catalogo.parquet")

        if os.path.isfile(parquet_path):
            return pd.read_parquet(parquet_path)

        if os.path.isfile(local_path):
            excel_data = pd.ExcelFile(local_path)
        else:
            url = base_url.format(date_str)
            response = requests.get(url)
            if not response.ok:
                continue
            with open(local_path, "wb") as f:
                f.write(response.content)
            excel_data = pd.ExcelFile(BytesIO(response.content))

        if "c_ClaveProdServ" in excel_data.sheet_names:
            df = pd.read_excel(excel_data, sheet_name="c_ClaveProdServ", skiprows=4)
            df.to_parquet(parquet_path, index=False)
            return df

    raise FileNotFoundError("No valid Excel file with c_ClaveProdServ sheet found in last 90 days")


    