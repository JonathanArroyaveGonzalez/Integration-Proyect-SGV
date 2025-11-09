"""
Cliente Transprensa y consultas internas.
Funciones para interactuar con el servicio de Transprensa.
"""

from __future__ import annotations
from typing import Dict, Any, List
import requests
from cachetools.func import ttl_cache
import json as json_module

from transprensa.services.internalService import get_internal_query_service
from transprensa.services.transprensaService import get_transprensa_service


def getInternalService():
    """Obtiene instancia singleton del servicio de consultas internas."""
    return get_internal_query_service()


def getExternalService():
    """Obtiene instancia singleton del servicio Transprensa."""
    return get_transprensa_service()


@ttl_cache(maxsize=128, ttl=900)
def get_cliente_codigo_by_nit(nit: str) -> str:
    """
    Consulta el código de cliente en Transprensa por NIT.

    Args:
        nit: Número de identificación tributaria del cliente

    Returns:
        Código del cliente o cadena vacía
    """
    if not nit:
        return ""

    tp_client = getExternalService()
    payload = {"cliente_documento": nit.strip()}

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


@ttl_cache(maxsize=128, ttl=900)
def get_ciudad_codigo_by_nombre(nombre_ciudad: str) -> str:
    """
    Consulta el código DANE de ciudad por nombre usando el servicio de Transprensa.

    Args:
        nombre_ciudad: Nombre de la ciudad a consultar

    Returns:
        Código DANE de la ciudad o cadena vacía
    """
    if not nombre_ciudad:
        return ""

    nombre_normalizado = nombre_ciudad.upper().strip()
    tp_client = getExternalService()

    payload = {
        "ciudad_codigo": "",
        "departamento_codigo": "",
        "departamento_codigodane": "",
        "nombre_ciudad": nombre_normalizado,
    }

    try:
        resp = tp_client.request(
            method="POST",
            endpoint="servicio.Consultas.ciudad",
            data=payload,
            timeout=5,
        )

        if not resp or not resp.get("success") or not resp.get("data"):
            return ""

        ciudades = resp.get("data", [])
        if not ciudades or not isinstance(ciudades[0], dict):
            return ""

        return ciudades[0].get("ciudad_codigodane", "")

    except Exception:
        return ""


def get_guide_data(picking: str, bigpedido: str) -> Dict[str, Any]:
    """
    Obtiene datos de guía desde el servicio interno.

    Args:
        picking: Código de picking
        bigpedido: Número de pedido

    Returns:
        Dict con datos de la guía (con y sin detalle) o diccionario vacío
    """
    try:
        internal_service = getInternalService()
        result = internal_service.getGuiaData(picking, bigpedido)
        return result if result else {}
    except Exception as e:
        print(f"Error obteniendo datos de guía: {e}")
        return {}



def create_remesas(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Crea remesas en Transprensa usando el payload proporcionado.

    Args:
        payload: Dict con estructura de remesas

    Returns:
        Respuesta de Transprensa (success, data, msg)
    """
    try:
        print("  [DEBUG] Payload enviando a Transprensa:")
        print(f"  {json_module.dumps(payload, indent=2, default=str)}")

        tp_client = getExternalService()
        response = tp_client.request(
            method="POST",
            endpoint="servicio.Remesa.crear",
            data=payload,
            timeout=10,
        )

        print("  [DEBUG] Respuesta de Transprensa:")
        print(f"  {json_module.dumps(response, indent=2, default=str)}")

        return response if response else {"success": False, "data": [], "msg": "No response"}
        
    except requests.exceptions.HTTPError as http_err:
        print(f"Error HTTP creando remesas: {http_err}")
        try:
            print("Respuesta del servidor:", http_err.response.text)
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
        return response if response else {"success": False, "data": {}, "msg": "No response"}
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

        if isinstance(result, dict):
            if "message" in result and "error" not in result:
                return {
                    "success": True,
                    "message": result.get("message", "PDF guardado exitosamente"),
                }
            if "success" in result:
                return result

        return {"success": False, "message": "Respuesta inválida"}
    except Exception as e:
        print(f"Error guardando PDF: {e}")
        return {"success": False, "message": str(e)}