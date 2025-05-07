"""
Herramienta para obtener el catálogo de productos y servicios del SAT
"""

import logging

from .generator import generate_pys_data
from .exporter import export_to_xml, export_to_json

# Configure logger
logger = logging.getLogger(__name__)


def pull_xml(output_file=None):
    """
    Obtiene los datos del catálogo PyS del SAT y los devuelve en formato XML.

    Args:
        output_file: Ruta del archivo donde guardar el XML. Si es None, solo devuelve el string.

    Returns:
        str: Contenido XML si output_file es None
    """
    logger.info("Starting pull_xml operation")
    data = generate_pys_data()
    result = export_to_xml(data, output_file)
    logger.info("pull_xml operation completed")
    return result


def pull_json(output_file=None):
    """
    Obtiene los datos del catálogo PyS del SAT y los devuelve en formato JSON.

    Args:
        output_file: Ruta del archivo donde guardar el JSON. Si es None, solo devuelve el dict.

    Returns:
        list: Datos estructurados si output_file es None
    """
    logger.info("Starting pull_json operation")
    data = generate_pys_data()
    result = export_to_json(data, output_file)
    logger.info("pull_json operation completed")
    return result
