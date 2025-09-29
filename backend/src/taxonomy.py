import json
from db import Classification
from session import with_db


@with_db
def load_flatten_data(input_file="pys_flattened_latest.json", *, db):
    """Load flattened PYS catalog data into the database"""
    import os
    
    # Check if the file exists
    if not os.path.exists(input_file):
        print(f"Warning: {input_file} not found. Skipping taxonomy data load.")
        return
    
    # Clear existing data first
    db.query(Classification).delete()
    db.commit()
    print("Cleared existing classification data")
    
    with open(input_file, "r", encoding="utf-8") as file:
        data = json.load(file)

    entries = []
    seen_clase_nums = set()
    
    for item in data:
        clase_num = item.get("Clase_num")
        
        # Skip if we've already seen this Clase_num
        if clase_num in seen_clase_nums:
            continue
            
        # Skip entries with missing or invalid data
        if not clase_num or clase_num == 0:
            continue
            
        seen_clase_nums.add(clase_num)
        
        entries.append(
            Classification(
                tipo_num=item.get("tipo_num"),
                Tipo=item.get("Tipo"),
                Div_num=item.get("Div_num"),
                Division=item.get("Division"),
                Grupo_num=item.get("Grupo_num"),
                Grupo=item.get("Grupo"),
                Clase_num=clase_num,
                Clase=item.get("Clase"),
            )
        )
    
    db.bulk_save_objects(entries)
    db.commit()
    print(f"Loaded {len(entries)} taxonomy entries from {input_file}")
