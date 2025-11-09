"""
Orquestador V2 - Flujo completo de guías

Ejecuta el workflow completo de una guía:
1. Obtener datos de guía (sin y con detalle) - ASYNC
2. Mapear a Remesa
3. Crear remesa en Transprensa
4. Obtener PDF
5. Descargar y guardar PDF en background
"""

from __future__ import annotations
import base64
import requests
import time
import threading
import asyncio
from typing import Dict, Any, Optional

from transprensa.services import clientService
from transprensa.functions.remesaMapper import mapear_guia_a_remesa, crear_payload_api


def download_pdf_from_url(pdf_url: str, timeout: int = 10) -> Optional[bytes]:
    """
    Descarga un PDF desde una URL.

    Args:
        pdf_url: URL del PDF
        timeout: Timeout en segundos

    Returns:
        Contenido del PDF en bytes o None si falla
    """
    try:
        response = requests.get(pdf_url, timeout=timeout)
        response.raise_for_status()
        return response.content
    except (requests.Timeout, requests.RequestException, Exception) as e:
        print(f"Error descargando PDF desde {pdf_url}: {e}")
        return None


def _process_pdf_background(
    remesa_num: str, picking: str, pdf_url: str, timeout: int = 10
) -> None:
    """
    Procesa el PDF en background: descarga y guarda en BD.
    Se ejecuta en un thread separado sin bloquear la respuesta al cliente.

    Args:
        remesa_num: Número de remesa
        picking: Código de picking
        pdf_url: URL del PDF
        timeout: Timeout para descargar PDF
    """
    try:
        print(f"[BACKGROUND] Procesando PDF para remesa {remesa_num}")

        pdf_content = download_pdf_from_url(pdf_url, timeout=timeout)
        if not pdf_content:
            print(
                f"[BACKGROUND] Error: No se pudo descargar PDF para remesa {remesa_num}"
            )
            return

        pdf_base64 = base64.b64encode(pdf_content).decode("utf-8")
        print(f"[BACKGROUND] PDF descargado ({len(pdf_content)} bytes)")

        save_result = clientService.save_guide_pdf(
            remesa_num=remesa_num, picking=picking, pdf_base64=pdf_base64
        )

        if isinstance(save_result, dict) and save_result.get("success"):
            print(f"✓ [BACKGROUND] PDF guardado correctamente para remesa {remesa_num}")
        else:
            print(f"[BACKGROUND] Error guardando PDF: {save_result}")

    except Exception as e:
        print(f"[BACKGROUND] Error procesando PDF: {e}")


async def execute_guide_workflow_async(picking: str, bigpedido: str) -> Dict[str, Any]:
    """
    Versión ASYNC del workflow V2.

    Args:
        picking: Código de picking
        bigpedido: Número de pedido

    Returns:
        Dict con respuesta de Transprensa + metadata
    """
    start_time = time.time()
    picking = str(picking).strip()
    bigpedido = str(bigpedido).strip()

    if not picking or not bigpedido:
        return {
            "success": False,
            "picking": picking,
            "bigpedido": bigpedido,
            "remesa_numero": "",
            "msg": "picking y bigpedido son requeridos",
            "tiempo_ms": 0,
            "pdf_en_background": False,
        }

    try:
        print(
            f"[PASO 1] Obteniendo datos de guía: picking={picking}, bigpedido={bigpedido}"
        )
        step1_start = time.time()

        guia_comparativa = await clientService.get_guide_data(picking, bigpedido)

        step1_time = int((time.time() - step1_start) * 1000)
        print(f"✓ Paso 1 completado en {step1_time}ms")

        if not guia_comparativa:
            return {
                "success": False,
                "picking": picking,
                "bigpedido": bigpedido,
                "remesa_numero": "",
                "msg": "No se encontraron datos de guía",
                "tiempo_ms": int((time.time() - start_time) * 1000),
                "pdf_en_background": False,
            }

        print("[PASO 2] Mapeando guía a Remesa")
        remesa_mapeada = mapear_guia_a_remesa(guia_comparativa)

        if not remesa_mapeada:
            return {
                "success": False,
                "picking": picking,
                "bigpedido": bigpedido,
                "remesa_numero": "",
                "msg": "No se pudo mapear la guía a remesa",
                "tiempo_ms": int((time.time() - start_time) * 1000),
                "pdf_en_background": False,
            }

        print("[PASO 3] Creando remesa en Transprensa")
        step3_start = time.time()

        payload = crear_payload_api([remesa_mapeada])
        create_response = clientService.create_remesas(payload)

        step3_time = int((time.time() - step3_start) * 1000)
        print(f"✓ Paso 3 completado en {step3_time}ms")

        if not create_response.get("success"):
            validation_error = ""
            data = create_response.get("data", [])
            if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                validation_error = data[0].get("validacion", "")

            error_msg = validation_error or create_response.get(
                "msg", "Error desconocido"
            )
            return {
                "success": False,
                "picking": picking,
                "bigpedido": bigpedido,
                "remesa_numero": "",
                "mensaje": error_msg,
                "tiempo_ms": int((time.time() - start_time) * 1000),
                "pdf_en_background": False,
            }

        remesa_creada_numero = ""
        data = create_response.get("data", [])
        if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
            remesa_creada_numero = str(data[0].get("remesa", "")).strip()
            validation_error = data[0].get("validacion", "")
            if validation_error and not remesa_creada_numero:
                return {
                    "success": False,
                    "picking": picking,
                    "bigpedido": bigpedido,
                    "remesa_numero": "",
                    "mensaje": validation_error,
                    "tiempo_ms": int((time.time() - start_time) * 1000),
                    "pdf_en_background": False,
                }

        if not remesa_creada_numero:
            return {
                "success": False,
                "picking": picking,
                "bigpedido": bigpedido,
                "remesa_numero": "",
                "mensaje": "Remesa no creada - sin número de remesa",
                "tiempo_ms": int((time.time() - start_time) * 1000),
                "pdf_en_background": False,
            }

        print(f"✓ Remesa creada: {remesa_creada_numero}")

        print("[PASO 4] Obteniendo URL de PDF")
        step4_start = time.time()

        print_response = clientService.print_remesas([remesa_creada_numero])

        step4_time = int((time.time() - step4_start) * 1000)
        print(f"✓ Paso 4 completado en {step4_time}ms")

        if not print_response.get("success"):
            return {
                "success": True,
                "picking": picking,
                "bigpedido": bigpedido,
                "remesa_numero": remesa_creada_numero,
                "msg": f"Remesa creada. Error en PDF: {print_response.get('msg', 'Error desconocido')}",
                "tiempo_ms": int((time.time() - start_time) * 1000),
                "pdf_en_background": False,
            }

        pdf_data = print_response.get("data", {})
        pdf_url = (
            pdf_data.get(remesa_creada_numero, "") if isinstance(pdf_data, dict) else ""
        )

        if not pdf_url:
            return {
                "success": True,
                "picking": picking,
                "bigpedido": bigpedido,
                "remesa_numero": remesa_creada_numero,
                "msg": "Remesa creada. No se obtuvo URL del PDF",
                "tiempo_ms": int((time.time() - start_time) * 1000),
                "pdf_en_background": False,
            }

        print("[PASO 5-6] Iniciando procesamiento de PDF en background")
        pdf_thread = threading.Thread(
            target=_process_pdf_background,
            args=(remesa_creada_numero, picking, pdf_url),
            daemon=True,
        )
        pdf_thread.start()

        return {
            "success": True,
            "picking": picking,
            "bigpedido": bigpedido,
            "remesa_numero": remesa_creada_numero,
            "msg": "Guía procesada exitosamente. PDF en procesamiento",
            "tiempo_ms": int((time.time() - start_time) * 1000),
            "pdf_en_background": True,
        }

    except Exception as e:
        print(f"✗ Error (ASYNC): {e}")
        return {
            "success": False,
            "picking": picking,
            "bigpedido": bigpedido,
            "remesa_numero": "",
            "msg": f"Error inesperado: {str(e)}",
            "tiempo_ms": int((time.time() - start_time) * 1000),
            "pdf_en_background": False,
        }


def execute_guide_workflow(picking: str, bigpedido: str) -> Dict[str, Any]:
    """
    Wrapper sincrónico que llama a la versión async.
    Permite que las views Django (síncronas) puedan llamar a la función async.

    Args:
        picking: Código de picking
        bigpedido: Número de pedido

    Returns:
        Dict con respuesta del workflow
    """
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        result = loop.run_until_complete(
            execute_guide_workflow_async(picking, bigpedido)
        )

        loop.close()
        return result

    except Exception as e:
        print(f"✗ Error en wrapper sincrónico: {e}")
        return {
            "success": False,
            "picking": picking,
            "bigpedido": bigpedido,
            "remesa_numero": "",
            "msg": f"Error inesperado: {str(e)}",
            "tiempo_ms": 0,
            "pdf_en_background": False,
        }
