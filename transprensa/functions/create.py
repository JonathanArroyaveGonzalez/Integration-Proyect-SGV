from __future__ import annotations
import base64
import requests
import time
from typing import Dict, Any, List, Tuple

from .remesaMapper import (
    mapear_lista_ordenes,
    crear_payload_api,
)

from transprensa.functions.clientService import (
    getInternalService,
    collectOrdersFromIds,
    createRemesasInTransprensa,
    printRemesasInTransprensa,
    extractCreatedRemesas,
)


def buildRemesasFromOrdersV2(orders: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Construye payload de remesas usando pruebaMapper (RECOMENDADO).

    Versión simplificada y eficiente:
    - No requiere servicio externo
    - Mapper consulta ciudades internamente
    - Retorna payload listo para Transprensa

    Args:
        orders: Lista de órdenes con estructura estándar

    Returns:
        Dict con:
            - success: bool
            - payload: dict con remesas mapeadas
            - stats: dict con estadísticas
            - error: str (si success=False)
    """
    try:
        # Mapear órdenes a remesas usando dataclasses
        remesas = mapear_lista_ordenes(orders)

        # Crear payload API
        payload = crear_payload_api(remesas)

        # Estadísticas
        stats = {
            "total_orders": len(orders),
            "remesas_built": len(remesas),
            "mapper_version": "V2_Dataclasses",
        }

        return {
            "success": True,
            "payload": payload,
            "stats": stats,
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "payload": {},
            "stats": {
                "total_orders": len(orders),
                "remesas_built": 0,
                "mapper_version": "V2_Dataclasses",
            },
        }


def processPdfDownloadsAndSaves(
    service,
    created_remesas: List[str],
    remesas_payload: List[Dict[str, Any]],
    pdf_urls_map: Dict[str, str],
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Procesa descarga y guardado de PDFs."""
    saved: List[Dict[str, Any]] = []
    errors: List[Dict[str, Any]] = []

    for i, remesa_num in enumerate(created_remesas):
        picking = ""

        if i < len(remesas_payload):
            remesa_item = remesas_payload[i]
            if isinstance(remesa_item, dict):
                picking = str(remesa_item.get("remesa_codigo", ""))

        pdf_url = pdf_urls_map.get(remesa_num)
        if not pdf_url:
            errors.append(
                {
                    "remesa": remesa_num,
                    "picking": picking,
                    "error": "No llegó URL de PDF desde Transprensa",
                }
            )
            continue

        try:
            # Descargar PDF
            response = requests.get(pdf_url, timeout=20)
            response.raise_for_status()
            pdf_b64 = base64.b64encode(response.content).decode("utf-8")

            # Guardar en BD
            save_result = service.guardar_pdf_guia(
                delivery_number=remesa_num, picking=picking, pdf_base64=pdf_b64
            )

            if isinstance(save_result, dict):
                if save_result.get("success"):
                    saved.append(
                        {
                            "remesa": remesa_num,
                            "picking": picking,
                            "status": "saved",
                        }
                    )
                else:
                    error_msg = save_result.get("message", "Error desconocido")
                    errors.append(
                        {
                            "remesa": remesa_num,
                            "picking": picking,
                            "error": error_msg,
                        }
                    )
            else:
                errors.append(
                    {
                        "remesa": remesa_num,
                        "picking": picking,
                        "error": f"Respuesta inesperada: {type(save_result).__name__}",
                    }
                )

        except requests.Timeout:
            errors.append(
                {
                    "remesa": remesa_num,
                    "picking": picking,
                    "error": "Timeout al descargar PDF (>20s)",
                }
            )

        except requests.RequestException as e:
            errors.append(
                {
                    "remesa": remesa_num,
                    "picking": picking,
                    "error": f"Error al descargar PDF: {str(e)}",
                }
            )

        except Exception as e:
            errors.append(
                {
                    "remesa": remesa_num,
                    "picking": picking,
                    "error": f"Excepción inesperada: {str(e)}",
                }
            )

    return saved, errors


def extractPdfUrlsFromResponse(tp_print_response: Dict[str, Any]) -> Dict[str, str]:
    """Extrae mapeo {remesa_num: pdf_url} de respuesta de impresión."""
    if not tp_print_response or not isinstance(tp_print_response, dict):
        return {}

    if not tp_print_response.get("success"):
        return {}

    data = tp_print_response.get("data")
    if isinstance(data, dict):
        return data

    return {}



def executeRemesaWorkflow(order_ids: List[str]) -> Dict[str, Any]:
    """
    Ejecuta el workflow completo de remesas y devuelve respuesta limpia.

    Retorna formato similar a Transprensa:
    {
        "success": true,
        "data": [
            {
                "orden": "103888",
                "remesa": "103999",
                "validacion": "",
                "success": true
            },
            ...
        ],
        "msg": "OK | [ tiempo_total_ms ]"
    }

    Args:
        order_ids: Lista de IDs de órdenes (strings)

    Returns:
        Dict con formato limpio de Transprensa
    """
    start_time = time.time()
    data_response = []

    try:
        # STEP 1: Obtener órdenes
        try:
            internal_service = getInternalService()
            orders = collectOrdersFromIds(internal_service, order_ids)

            if not orders:
                return {
                    "success": False,
                    "data": [],
                    "msg": "No se encontraron órdenes con los IDs proporcionados",
                }
        except Exception as e:
            return {
                "success": False,
                "data": [],
                "msg": f"Error al obtener órdenes: {str(e)}",
            }

        # STEP 2: Mapear a remesas
        try:
            result_mapeo = buildRemesasFromOrdersV2(orders)

            if not result_mapeo.get("success"):
                error_msg = result_mapeo.get("error", "Error desconocido en mapeo")
                return {
                    "success": False,
                    "data": [],
                    "msg": f"Error al mapear remesas: {error_msg}",
                }

            payload = result_mapeo.get("payload", {})

        except Exception as e:
            return {"success": False, "data": [], "msg": f"Error en mapeo: {str(e)}"}

        # STEP 3: Crear remesas en Transprensa
        try:
            tp_response = createRemesasInTransprensa(payload)

            # Procesar respuesta de Transprensa
            if not tp_response.get("success"):
                # Transprensa devolvió error - extraer detalles por orden
                tp_data = tp_response.get("data", [])

                if isinstance(tp_data, list):
                    # Transprensa devolvió array con detalles por orden
                    for item in tp_data:
                        orden_id = str(item.get("orden", ""))
                        remesa_num = str(item.get("remesa", ""))
                        validacion = str(item.get("validacion", ""))
                        item_success = item.get("success", False)

                        data_response.append(
                            {
                                "orden": orden_id,
                                "remesa": remesa_num if remesa_num else "",
                                "validacion": validacion,
                                "success": bool(
                                    item_success in [True, "true", "True", 1, "1"]
                                ),
                            }
                        )
                else:
                    # Transprensa devolvió error general
                    error_msg = tp_response.get("msg", "Error en creación de remesas")
                    for order in orders:
                        data_response.append(
                            {
                                "orden": str(order.get("orden_id", "")),
                                "remesa": "",
                                "validacion": error_msg,
                                "success": False,
                            }
                        )

                total_time = int((time.time() - start_time) * 1000)
                return {
                    "success": False,
                    "data": data_response,
                    "msg": tp_response.get("msg", "Error en Transprensa")
                    + f" | [ {total_time} ]",
                }

            # Transprensa éxito - extraer remesas creadas
            created_remesas = extractCreatedRemesas(tp_response)
            tp_data = tp_response.get("data", [])

            if isinstance(tp_data, list):
                # Procesar respuesta con detalles por orden
                for item in tp_data:
                    orden_id = str(item.get("orden", ""))
                    remesa_num = str(item.get("remesa", ""))
                    validacion = (
                        str(item.get("validacion", ""))
                        if item.get("validacion")
                        else ""
                    )
                    item_success = item.get("success", False)

                    data_response.append(
                        {
                            "orden": orden_id,
                            "remesa": remesa_num if remesa_num else "",
                            "validacion": validacion,
                            "success": bool(
                                item_success in [True, "true", "True", 1, "1"]
                            ),
                        }
                    )
            else:
                # Fallback si no viene array
                for i, order in enumerate(orders):
                    remesa_num = created_remesas[i] if i < len(created_remesas) else ""
                    data_response.append(
                        {
                            "orden": str(order.get("orden_id", "")),
                            "remesa": remesa_num,
                            "validacion": "",
                            "success": bool(remesa_num),
                        }
                    )

        except Exception as e:
            return {
                "success": False,
                "data": [],
                "msg": f"Error al crear remesas en Transprensa: {str(e)}",
            }

        # STEP 4: Obtener guías (PDFs) de remesas creadas
        try:
            # Extraer remesas exitosas
            successful_remesas = [
                item["remesa"]
                for item in data_response
                if item["success"] and item["remesa"]
            ]

            if successful_remesas:
                print_response = printRemesasInTransprensa(successful_remesas)
                pdf_urls_map = (
                    extractPdfUrlsFromResponse(print_response)
                    if print_response.get("success")
                    else {}
                )

                # STEP 5: Descargar y guardar PDFs
                if pdf_urls_map:
                    remesas_list = payload.get("remesas", [])
                    processPdfDownloadsAndSaves(
                        internal_service, successful_remesas, remesas_list, pdf_urls_map
                    )
        except Exception:
            # No detener el flujo si falla descarga de PDFs
            pass

        # Respuesta final exitosa
        total_time = int((time.time() - start_time) * 1000)

        return {"success": True, "data": data_response, "msg": f"OK | [ {total_time} ]"}

    except Exception as e:
        total_time = int((time.time() - start_time) * 1000)
        return {
            "success": False,
            "data": data_response,
            "msg": f"Error inesperado: {str(e)} | [ {total_time} ]",
        }
