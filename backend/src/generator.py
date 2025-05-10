"""
Funciones para generar la estructura completa de datos
"""

import os
import sys
import time
import logging
from typing import Dict, List, Any

from src.scraper import obtain_types
from src.scraper import obtain_segments
from src.scraper import obtain_families
from src.scraper import obtain_classes
from src.exporter import export_to_json
from src.exporter import export_to_xml
from src.taxonomy import flatten_data


logger = logging.getLogger(__name__)


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
        logger.info("Obteniendo tipos...")

    types = obtain_types()
    for type_id, type_name in types.items():
        if type_id == "0":
            continue
        type_data = {"key": type_id, "name": type_name, "segments": []}

        if not silent:
            logger.info(f"Tipo: {type_id} - {type_name}")

        segments = obtain_segments(type_id)
        for segment_id, segment_name in segments.items():
            if segment_id == "0":
                continue
            segment_data = {"key": segment_id, "name": segment_name, "families": []}

            if not silent:
                logger.info(f"  Segmento: {segment_id} - {segment_name}")

            families = obtain_families(type_id, segment_id)
            for family_id, family_name in families.items():
                if family_id == "0":
                    continue
                family_data = {"key": family_id, "name": family_name, "classes": []}

                if not silent:
                    logger.info(f"    Familia: {family_id} - {family_name}")

                classes = obtain_classes(type_id, segment_id, family_id)
                for class_id, class_name in classes.items():
                    if class_id == "0":
                        continue
                    class_data = {"key": class_id, "name": class_name}
                    family_data["classes"].append(class_data)

                    if not silent:
                        logger.info(f"      Clase: {class_id} - {class_name}")

                segment_data["families"].append(family_data)
            type_data["segments"].append(segment_data)
        types_list.append(type_data)

    return types_list


def pull_xml(output_file=None):
    logger.info("Starting pull_xml operation")
    data = generate_pys_data()
    result = export_to_xml(data, output_file)
    logger.info("pull_xml operation completed")
    return result


def is_pull_locked():
    lock_file = "output.json.lock"
    output_file = "output.json"

    if os.path.exists(lock_file):
        return {"locked": True, "reason": "lock file exists"}

    if not os.path.exists(output_file):
        return {"locked": False, "reason": "output.json does not exist"}

    file_age = time.time() - os.path.getmtime(output_file)
    one_week = 7 * 24 * 60 * 60

    if file_age < one_week:
        return {"locked": True, "reason": "output.json is younger than 1 week"}

    return {"locked": False, "reason": "output.json is older than 1 week"}


def pull_json(forced=False):
    locked_status = is_pull_locked()
    if locked_status["locked"] and not forced:
        logger.info("Lock is active, not pulling anything")
        return
    output_file = "output.json"
    logger.info("Starting pull_json operation")
    open("output.json.lock", "w").close()
    try:
        data = generate_pys_data()
        result = export_to_json(data, output_file)
        flatten_data(output_file)
        return result
    finally:
        if os.path.exists("output.json.lock"):
            os.remove("output.json.lock")
        logger.info("pull_json operation completed")
