"""
Funciones para exportar datos a XML y JSON
"""

import json
import xml.dom.minidom as minidom
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional


def export_to_xml(data: List[Dict[str, Any]], output_file: Optional[str] = None) -> Optional[str]:
    """
    Exporta los datos a XML.
    
    Args:
        data: Datos estructurados del catálogo PyS.
        output_file: Ruta del archivo donde guardar el XML. Si es None, solo devuelve el string.
        
    Returns:
        str: Contenido XML si output_file es None, None en caso contrario.
    """
    root = ET.Element("pys")
    
    for type_data in data:
        type_elem = ET.SubElement(root, "type", key=type_data["key"], name=type_data["name"])
        
        for segment_data in type_data["segments"]:
            segment_elem = ET.SubElement(type_elem, "segment", key=segment_data["key"], name=segment_data["name"])
            
            for family_data in segment_data["families"]:
                family_elem = ET.SubElement(segment_elem, "family", key=family_data["key"], name=family_data["name"])
                
                for class_data in family_data["classes"]:
                    ET.SubElement(family_elem, "class", key=class_data["key"], name=class_data["name"])
    
    # Crear XML con formato
    xml_str = minidom.parseString(ET.tostring(root, encoding="utf-8")).toprettyxml(indent="  ")
    
    # Guardar a archivo o devolver string
    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(xml_str)
        return None
    
    return xml_str


def export_to_json(data: List[Dict[str, Any]], output_file: Optional[str] = None) -> Optional[List[Dict[str, Any]]]:
    """
    Exporta los datos a JSON.
    
    Args:
        data: Datos estructurados del catálogo PyS.
        output_file: Ruta del archivo donde guardar el JSON. Si es None, solo devuelve los datos.
        
    Returns:
        List[Dict[str, Any]]: Datos estructurados si output_file es None, None en caso contrario.
    """
    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return None
    
    return data 