"""
Funciones para extraer datos del sitio web del SAT
"""

import requests
import logging
from bs4 import BeautifulSoup
from typing import Dict

# Configure logger
logger = logging.getLogger(__name__)

# URL principal del sitio
PYS_URL = "http://pys.sat.gob.mx/PyS/catPyS.aspx"

# Variables para mantener el estado entre solicitudes
_session = requests.Session()
_last_soup = None


def _send_get() -> BeautifulSoup:
    """Envía una solicitud GET a la URL principal y devuelve el soup."""
    global _last_soup

    logger.info(f"Sending GET request to {PYS_URL}")
    try:
        response = _session.get(PYS_URL)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        _last_soup = soup
        logger.debug("GET request successful")
        return soup
    except requests.exceptions.RequestException as e:
        logger.error(f"Error in GET request: {str(e)}")
        raise


def _send_post(data: Dict[str, str]) -> BeautifulSoup:
    """Envía una solicitud POST con los datos proporcionados y devuelve el soup."""
    global _last_soup

    if not _last_soup:
        logger.error("No previous request made, _last_soup is None")
        raise ValueError("No se ha realizado una solicitud previa")

    # Extraer el estado del formulario actual
    form_state = _extract_form_state(_last_soup)

    # Combinar con los datos proporcionados
    full_data = {**form_state, **data, "__ASYNCPOST": "false"}

    headers = {
        "Accept-Encoding": "gzip, deflate",
        "Referer": PYS_URL,
        "X-Requested-With": "XMLHttpRequest",
        "X-Microsoft-Ajax": "delta=false",
    }

    logger.info(f"Sending POST request to {PYS_URL}")
    logger.debug(f"POST data: {data}")
    try:
        response = _session.post(PYS_URL, data=full_data, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        _last_soup = soup
        logger.debug("POST request successful")
        return soup
    except requests.exceptions.RequestException as e:
        logger.error(f"Error in POST request: {str(e)}")
        raise


def _extract_select_values(soup: BeautifulSoup, select_id: str) -> Dict[str, str]:
    """Extrae los valores de un elemento select."""
    logger.debug(f"Extracting values from select with id: {select_id}")
    select = soup.find("select", id=select_id)
    if not select:
        logger.warning(f"Select with id '{select_id}' not found")
        return {}

    options = select.find_all("option")
    values = {}
    for option in options:
        key = option.get("value", "")
        if key:  # Excluir opciones sin valor
            values[key] = option.text

    logger.debug(f"Found {len(values)} options in select '{select_id}'")
    return values


def _extract_form_state(soup: BeautifulSoup) -> Dict[str, str]:
    """Extrae el estado del formulario (campos ocultos)."""
    logger.debug("Extracting form state")
    form = soup.find("form", id="form1")
    if not form:
        logger.warning("Form with id 'form1' not found")
        return {}

    result = {}
    for input_field in form.find_all("input", type=["hidden", "text"]):
        name = input_field.get("name")
        value = input_field.get("value", "")
        if name:
            result[name] = value

    logger.debug(f"Extracted {len(result)} form state fields")
    return result


def obtain_types() -> Dict[str, str]:
    """Obtiene la lista de tipos desde la página principal."""
    logger.info("Obtaining types list")
    soup = _send_get()
    types = _extract_select_values(soup, "cmbTipo")
    logger.info(f"Found {len(types)} types")
    return types


def obtain_segments(type_id: str) -> Dict[str, str]:
    """Obtiene la lista de segmentos para un tipo determinado."""
    logger.info(f"Obtaining segments for type ID: {type_id}")
    inputs = {
        "myScript": "pnlTipo|cmbTipo",
        "__EVENTTARGET": "cmbTipo",
        "cmbTipo": type_id,
    }
    soup = _send_post(inputs)
    segments = _extract_select_values(soup, "cmbSegmento")
    logger.info(f"Found {len(segments)} segments for type ID: {type_id}")
    return segments


def obtain_families(type_id: str, segment_id: str) -> Dict[str, str]:
    """Obtiene la lista de familias para un tipo y segmento determinados."""
    logger.info(f"Obtaining families for type ID: {type_id}, segment ID: {segment_id}")
    inputs = {
        "myScript": "pnlSegmento|cmbSegmento",
        "__EVENTTARGET": "cmbSegmento",
        "cmbTipo": type_id,
        "cmbSegmento": segment_id,
    }
    soup = _send_post(inputs)
    families = _extract_select_values(soup, "cmbFamilia")
    logger.info(
        f"Found {len(families)} families for type ID: {type_id}, segment ID: {segment_id}"
    )
    return families


def obtain_classes(type_id: str, segment_id: str, family_id: str) -> Dict[str, str]:
    """Obtiene la lista de clases para un tipo, segmento y familia determinados."""
    logger.info(
        f"Obtaining classes for type ID: {type_id}, segment ID: {segment_id}, family ID: {family_id}"
    )
    inputs = {
        "myScript": "pnlFamilia|cmbFamilia",
        "__EVENTTARGET": "cmbFamilia",
        "cmbTipo": type_id,
        "cmbSegmento": segment_id,
        "cmbFamilia": family_id,
    }
    soup = _send_post(inputs)
    classes = _extract_select_values(soup, "cmbClase")
    logger.info(
        f"Found {len(classes)} classes for type ID: {type_id}, segment ID: {segment_id}, family ID: {family_id}"
    )
    return classes
