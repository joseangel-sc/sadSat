"""
Funciones para generar la estructura completa de datos
"""

import sys
from typing import Dict, List, Any

from .scraper import (
    obtain_types,
    obtain_segments,
    obtain_families,
    obtain_classes
)


def generate_pys_data(silent=False) -> List[Dict[str, Any]]:
    """
    Genera toda la estructura de datos del catálogo PyS.
    
    Args:
        silent: Si es True, no muestra mensajes de progreso.
        
    Returns:
        List[Dict[str, Any]]: Lista de tipos con su estructura jerárquica completa.
    """
    types_list = []
    
    if not silent:
        print("Obteniendo tipos...", file=sys.stderr)
    
    types = obtain_types()
    for type_id, type_name in types.items():
        type_data = {"key": type_id, "name": type_name, "segments": []}
        
        if not silent:
            print(f"Tipo: {type_id} - {type_name}", file=sys.stderr)

        segments = obtain_segments(type_id)
        for segment_id, segment_name in segments.items():
            segment_data = {"key": segment_id, "name": segment_name, "families": []}
            
            if not silent:
                print(f"  Segmento: {segment_id} - {segment_name}", file=sys.stderr)

            families = obtain_families(type_id, segment_id)
            for family_id, family_name in families.items():
                family_data = {"key": family_id, "name": family_name, "classes": []}
                
                if not silent:
                    print(f"    Familia: {family_id} - {family_name}", file=sys.stderr)

                classes = obtain_classes(type_id, segment_id, family_id)
                for class_id, class_name in classes.items():
                    class_data = {"key": class_id, "name": class_name}
                    family_data["classes"].append(class_data)
                    
                    if not silent:
                        print(f"      Clase: {class_id} - {class_name}", file=sys.stderr)

                segment_data["families"].append(family_data)
            type_data["segments"].append(segment_data)
        types_list.append(type_data)

    return types_list 