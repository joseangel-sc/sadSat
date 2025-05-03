"""
Herramienta para obtener el catálogo de productos y servicios del SAT
"""

from .scraper import (
    obtain_types, 
    obtain_segments, 
    obtain_families, 
    obtain_classes
)
from .generator import generate_pys_data
from .exporter import export_to_xml, export_to_json

def pull_xml(output_file=None):
    """
    Obtiene los datos del catálogo PyS del SAT y los devuelve en formato XML.
    
    Args:
        output_file: Ruta del archivo donde guardar el XML. Si es None, solo devuelve el string.
        
    Returns:
        str: Contenido XML si output_file es None
    """
    data = generate_pys_data()
    return export_to_xml(data, output_file)

def pull_json(output_file=None):
    """
    Obtiene los datos del catálogo PyS del SAT y los devuelve en formato JSON.
    
    Args:
        output_file: Ruta del archivo donde guardar el JSON. Si es None, solo devuelve el dict.
        
    Returns:
        list: Datos estructurados si output_file es None
    """
    data = generate_pys_data()
    return export_to_json(data, output_file) 