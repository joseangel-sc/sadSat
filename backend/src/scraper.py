"""
Funciones para extraer datos del sitio web del SAT
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict

# URL principal del sitio
PYS_URL = "http://pys.sat.gob.mx/PyS/catPyS.aspx"

# Variables para mantener el estado entre solicitudes
_session = requests.Session()
_last_soup = None


def _send_get() -> BeautifulSoup:
    """Envía una solicitud GET a la URL principal y devuelve el soup."""
    global _last_soup

    response = _session.get(PYS_URL)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    _last_soup = soup
    return soup


def _send_post(data: Dict[str, str]) -> BeautifulSoup:
    """Envía una solicitud POST con los datos proporcionados y devuelve el soup."""
    global _last_soup

    if not _last_soup:
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

    response = _session.post(PYS_URL, data=full_data, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    _last_soup = soup
    return soup


def _extract_select_values(soup: BeautifulSoup, select_id: str) -> Dict[str, str]:
    """Extrae los valores de un elemento select."""
    select = soup.find("select", id=select_id)
    if not select:
        return {}

    options = select.find_all("option")
    values = {}
    for option in options:
        key = option.get("value", "")
        if key:  # Excluir opciones sin valor
            values[key] = option.text

    return values


def _extract_form_state(soup: BeautifulSoup) -> Dict[str, str]:
    """Extrae el estado del formulario (campos ocultos)."""
    form = soup.find("form", id="form1")
    if not form:
        return {}

    result = {}
    for input_field in form.find_all("input", type=["hidden", "text"]):
        name = input_field.get("name")
        value = input_field.get("value", "")
        if name:
            result[name] = value

    return result


def obtain_types() -> Dict[str, str]:
    """Obtiene la lista de tipos desde la página principal."""
    soup = _send_get()
    return _extract_select_values(soup, "cmbTipo")


def obtain_segments(type_id: str) -> Dict[str, str]:
    """Obtiene la lista de segmentos para un tipo determinado."""
    inputs = {
        "myScript": "pnlTipo|cmbTipo",
        "__EVENTTARGET": "cmbTipo",
        "cmbTipo": type_id,
    }
    soup = _send_post(inputs)
    return _extract_select_values(soup, "cmbSegmento")


def obtain_families(type_id: str, segment_id: str) -> Dict[str, str]:
    """Obtiene la lista de familias para un tipo y segmento determinados."""
    inputs = {
        "myScript": "pnlSegmento|cmbSegmento",
        "__EVENTTARGET": "cmbSegmento",
        "cmbTipo": type_id,
        "cmbSegmento": segment_id,
    }
    soup = _send_post(inputs)
    return _extract_select_values(soup, "cmbFamilia")


def obtain_classes(type_id: str, segment_id: str, family_id: str) -> Dict[str, str]:
    """Obtiene la lista de clases para un tipo, segmento y familia determinados."""
    inputs = {
        "myScript": "pnlFamilia|cmbFamilia",
        "__EVENTTARGET": "cmbFamilia",
        "cmbTipo": type_id,
        "cmbSegmento": segment_id,
        "cmbFamilia": family_id,
    }
    soup = _send_post(inputs)
    return _extract_select_values(soup, "cmbClase")