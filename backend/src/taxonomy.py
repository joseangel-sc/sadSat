import json
from db import Classification
from session import with_db


@with_db
def load_flatten_data(input_file="output.json", *, db):
    with open(input_file, "r", encoding="utf-8") as file:
        data = json.load(file)

    entries = []
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
                    entries.append(
                        Classification(
                            tipo_num=tipo_num,
                            Tipo=tipo,
                            Div_num=div_num,
                            Division=division,
                            Grupo_num=grupo_num,
                            Grupo=grupo_name,
                            Clase_num=clase_num,
                            Clase=clase_name,
                        )
                    )
    db.bulk_save_objects(entries)
    db.commit()
