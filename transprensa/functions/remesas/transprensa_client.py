# -*- coding: utf-8 -*-
"""
Cliente Transprensa consolidado.
Funciones para interactuar con el servicio de Transprensa.
"""

from __future__ import annotations
from typing import Dict, Any, List

from transprensa.services.internalService import (
    get_internal_query_service,
    InternalQueryService,
)
from transprensa.services.transprensaService import get_transprensa_service
from transprensa.services.responseService import response_service


# =========================
#  Servicio interno
# =========================
def getInternalService() -> InternalQueryService:
    """Obtiene instancia singleton del servicio de consultas internas."""
    return get_internal_query_service()


# =========================
#  Órdenes
# =========================
def collectOrdersFromIds(
    service: InternalQueryService, ids: List[str]
) -> List[Dict[str, Any]]:
    """Obtiene órdenes completas a partir de una lista de IDs."""
    all_orders: List[Dict[str, Any]] = []

    for oid in ids:
        raw = service.get_orden_por_id(str(oid))
        fmt = response_service.format_wms_response(raw, "Orden encontrada exitosamente")

        if fmt.get("success") and isinstance(fmt.get("data"), list):
            all_orders.extend(fmt["data"])

    return all_orders


# =========================
#  Remesas
# =========================
def createRemesasInTransprensa(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Envía payload de remesas a Transprensa para creación."""
    tp_client = get_transprensa_service()
    return tp_client.request("POST", "servicio.Remesa.crear", payload)


def printRemesasInTransprensa(remesa_numbers: List[str]) -> Dict[str, Any]:
    """Solicita impresión de remesas y obtiene URLs de PDFs."""
    tp_client = get_transprensa_service()
    body = {"remesas": remesa_numbers}
    return tp_client.request("POST", "servicio.Remesa.impresionRemesa", body)


def extractCreatedRemesas(tp_create_response: Dict[str, Any]) -> List[str]:
    """Extrae números de remesa creados desde respuesta de Transprensa."""
    if not tp_create_response or not isinstance(tp_create_response, dict):
        return []

    data = tp_create_response.get("data") or {}

    # Caso 1: data es lista de diccionarios con campo "remesa"
    if isinstance(data, list):
        remesas = []
        for item in data:
            if isinstance(item, dict):
                remesa_num = item.get("remesa")
                if remesa_num:
                    remesas.append(str(remesa_num))

        if remesas:
            return remesas

        return [str(x) for x in data if x]

    # Caso 2: data es diccionario con campo "remesas"
    if isinstance(data, dict) and isinstance(data.get("remesas"), list):
        return [str(x) for x in data["remesas"] if x]

    # Caso 3: buscar en otros campos conocidos
    if isinstance(data, dict):
        for k in ("numeros", "guias", "entregas", "ids"):
            v = data.get(k)
            if isinstance(v, list):
                return [str(x) for x in v if x]

    return []
