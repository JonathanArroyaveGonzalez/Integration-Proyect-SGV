"""
Cliente Transprensa y consultas internas.
Funciones para interactuar con el servicio de Transprensa.
"""

from __future__ import annotations
from typing import Dict, Any, List
import time
import requests
from cachetools.func import ttl_cache


from transprensa.services.internalService import (
    get_internal_query_service,
    InternalQueryService,
)
from transprensa.services.transprensaService import (
    TransprensaService,
    get_transprensa_service,
)


def getInternalService() -> InternalQueryService:
    """Obtiene instancia singleton del servicio de consultas internas."""
    return get_internal_query_service()


def getExternalService() -> TransprensaService:
    """Obtiene instancia singleton del servicio Transprensa."""
    return get_transprensa_service()


@ttl_cache(maxsize=128, ttl=900)  # Cache por 15 minutos
def get_cliente_codigo_by_nit(nit: str) -> str:
    """
    Consulta el código de cliente en Transprensa por NIT (con cache 1 hora).

    Args:
        nit (str): Número de identificación tributaria del cliente.

    Returns:
        str: Código del cliente si se encuentra, de lo contrario una cadena vacía.
    """
    if not nit:
        return ""

    tp_client = getExternalService()
    payload = {
        "cliente_documento": nit.strip(),
    }

    try:
        resp = tp_client.request(
            method="POST",
            endpoint="servicio.Cliente.consultar",
            data=payload,
            timeout=5,
        )

        if resp.get("success") and isinstance(resp.get("data"), list) and resp["data"]:
            return resp["data"][0].get("cliente_codigo", "")

    except Exception as e:
        print(f"Error al consultar cliente por NIT: {e}")

    return ""


@ttl_cache(maxsize=128, ttl=900)  # Cache por 15 minutos
def get_ciudad_codigo_by_nombre(nombre_ciudad: str) -> str:
    """
    Consulta el código DANE de ciudad por nombre usando el servicio de Transprensa.
    Utiliza cache para evitar consultas repetidas (expira en 1 hora).

    Args:
        nombre_ciudad: Nombre de la ciudad a consultar

    Returns:
        str: Código DANE de la ciudad o cadena vacía si no se encuentra
    """
    if not nombre_ciudad:
        return ""

    # Normalizar nombre para búsqueda
    nombre_normalizado = nombre_ciudad.upper().strip()
    tp_client = getExternalService()

    payload = {
        "ciudad_codigo": "",
        "departamento_codigo": "",
        "departamento_codigodane": "",
        "nombre_ciudad": nombre_normalizado,
    }

    try:
        # Llamar a Transprensa con timeout de 5 segundos
        resp = tp_client.request(
            method="POST",
            endpoint="servicio.Consultas.ciudad",
            data=payload,
            timeout=5,  # Timeout para evitar bloqueos indefinidos
        )

        if not resp or not resp.get("success") or not resp.get("data"):
            return ""

        ciudades = resp.get("data", [])
        if not ciudades or not isinstance(ciudades[0], dict):
            return ""

        codigo_dane = ciudades[0].get("ciudad_codigodane", "")

        return codigo_dane

    except Exception:
        return ""


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


# ============================================================================
# MÉTODOS CENTRALIZADOS - Acceso a servicios externos e internos
# ============================================================================


def get_guide_data(picking: str, bigpedido: str, is_detail: int = 0) -> Dict[str, Any]:
    """
    Obtiene datos de guía desde el servicio interno.

    Args:
        picking: Código de picking
        bigpedido: Número de pedido
        is_detail: 0 (sin detalle) o 1 (con detalle)

    Returns:
        Dict con datos de la guía o diccionario vacío si no se encuentra
    """
    try:
        internal_service = getInternalService()
        result = internal_service.leer_datos_guia(picking, bigpedido, is_detail)
        return result if result else {}
    except Exception as e:
        print(f"Error obteniendo datos de guía: {e}")
        return {}


def get_guide_data_comparative(picking: str, bigpedido: str) -> Dict[str, Any]:
    """
    Obtiene datos de guía comparando ambas versiones (sin y con detalle).

    Args:
        picking: Código de picking
        bigpedido: Número de pedido

    Returns:
        Dict con ambas versiones de la guía
    """
    try:
        internal_service = getInternalService()
        result = internal_service.leer_datos_guia_comparativo(picking, bigpedido)
        return result if result else {}
    except Exception as e:
        print(f"Error obteniendo datos comparativos de guía: {e}")
        return {}


def collect_orders_by_ids(order_ids: List[str]) -> List[Dict[str, Any]]:
    """
    Obtiene lista de órdenes desde el servicio interno usando sus IDs.

    Args:
        order_ids: Lista de IDs de órdenes

    Returns:
        Lista de diccionarios con datos de las órdenes
    """
    try:
        internal_service = getInternalService()
        orders = internal_service.collectOrdersFromIds(order_ids)
        return orders if orders else []
    except Exception as e:
        print(f"Error obteniendo órdenes: {e}")
        return []


def collect_guides_by_pickings(
    picking_list: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Obtiene lista de guías desde el servicio interno usando sus pickings.

    Args:
        picking_list: Lista de dicts con {"picking": "...", "bigpedido": "..."}

    Returns:
        Lista de diccionarios con datos de las guías
    """
    try:
        internal_service = getInternalService()
        guides = internal_service.collectGuidesFromPickings(picking_list)
        return guides if guides else []
    except Exception as e:
        print(f"Error obteniendo guías: {e}")
        return []


def create_remesas(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Crea remesas en Transprensa usando el payload proporcionado.

    Args:
        payload: Dict con estructura de remesas

    Returns:
        Respuesta de Transprensa (success, data, msg)
    """
    try:
        import json as json_module

        # DEBUG: Imprimir payload ANTES de enviar
        print("  [DEBUG] Payload enviando a Transprensa:")
        print(f"  {json_module.dumps(payload, indent=2, default=str)}")

        tp_client = getExternalService()
        response = tp_client.request(
            method="POST",
            endpoint="servicio.Remesa.crear",
            data=payload,
            timeout=10,
        )

        # DEBUG: Imprimir respuesta
        print("  [DEBUG] Respuesta de Transprensa:")
        print(f"  {json_module.dumps(response, indent=2, default=str)}")

        return (
            response
            if response
            else {"success": False, "data": [], "msg": "No response"}
        )
    except requests.exceptions.HTTPError as http_err:
        print(f"Error HTTP creando remesas: {http_err}")
        try:
            error_text = http_err.response.text
            print("Respuesta del servidor:")
            print(error_text)
        except Exception as ex:
            print(f"No se pudo obtener respuesta del servidor: {ex}")
        import traceback

        traceback.print_exc()
        return {"success": False, "data": [], "msg": str(http_err)}
    except Exception as e:
        print(f"Error creando remesas: {e}")
        import traceback

        traceback.print_exc()
        return {"success": False, "data": [], "msg": str(e)}


def print_remesas(remesa_numbers: List[str]) -> Dict[str, Any]:
    """
    Solicita impresión de remesas a Transprensa y obtiene URLs de PDFs.

    Args:
        remesa_numbers: Lista de números de remesa

    Returns:
        Respuesta de Transprensa con mapeo {remesa: pdf_url}
    """
    try:
        tp_client = getExternalService()
        body = {"remesas": remesa_numbers}
        response = tp_client.request(
            method="POST",
            endpoint="servicio.Remesa.impresionRemesa",
            data=body,
            timeout=10,
        )
        return (
            response
            if response
            else {"success": False, "data": {}, "msg": "No response"}
        )
    except Exception as e:
        print(f"Error imprimiendo remesas: {e}")
        return {"success": False, "data": {}, "msg": str(e)}


def save_guide_pdf(remesa_num: str, picking: str, pdf_base64: str) -> Dict[str, Any]:
    """
    Guarda el PDF de una guía en la base de datos interna.

    Args:
        remesa_num: Número de remesa
        picking: Código de picking
        pdf_base64: Contenido del PDF en base64

    Returns:
        Dict con {"success": bool, "message": str}
    """
    try:
        internal_service = getInternalService()
        result = internal_service.guardar_pdf_guia(
            delivery_number=remesa_num, picking=picking, pdf_base64=pdf_base64
        )
        return (
            result
            if isinstance(result, dict)
            else {"success": False, "message": "Invalid response"}
        )
    except Exception as e:
        print(f"Error guardando PDF: {e}")
        return {"success": False, "message": str(e)}
