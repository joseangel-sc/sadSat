import json
import pandas as pd
import csv

def flatten_data(input_file='output.json', output_file='taxonomia.csv'):
    with open(input_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    rows = []
    for segmento in data:
        tipo_num = segmento["key"]
        tipo = segmento["name"]

        for familia in segmento.get("segments", []):
            div_num = familia["key"]
            division = familia["name"]

            for grupo in familia.get("families", []):
                grupo_num = grupo["key"]
                grupo_name = grupo["name"]

                for clase in grupo.get("classes", []):
                    clase_num = clase["key"]
                    clase_name = clase["name"]

                    rows.append({
                        "tipo_num": tipo_num,
                        "Tipo": tipo,
                        "Div_num": div_num,
                        "División": division,
                        "Grupo_num": grupo_num,
                        "Grupo": grupo_name,
                        "Clase_num": clase_num,
                        "Clase": clase_name
                    })

    df = pd.DataFrame(rows)
    df.to_csv(output_file, index=False, quoting=csv.QUOTE_NONNUMERIC, encoding='utf-8-sig')
    