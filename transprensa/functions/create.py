"""
Orquestador V2 - Flujo completo de guías

Funciones para ejecutar el workflow completo de una sola guía:
1. Obtener datos de guía (sin y con detalle)
2. Mapear a Remesa usando remesaMapperV2
3. Crear remesa en Transprensa
4. Obtener PDF (print/impresión)
5. Descargar PDF
6. Guardar PDF en BD
"""

from __future__ import annotations
import base64
import requests
import time
from typing import Dict, Any, Optional

from transprensa.services import clientService
from transprensa.functions.remesaMapper import mapear_guia_a_remesa, crear_payload_api


def download_pdf_from_url(pdf_url: str, timeout: int = 20) -> Optional[bytes]:
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
    except requests.Timeout:
        print(f"Timeout descargando PDF desde {pdf_url}")
        return None
    except requests.RequestException as e:
        print(f"Error descargando PDF: {e}")
        return None
    except Exception as e:
        print(f"Error inesperado descargando PDF: {e}")
        return None


def execute_guide_workflow_v2(picking: str, bigpedido: str) -> Dict[str, Any]:
    """
    Ejecuta el workflow COMPLETO de UNA SOLA GUÍA:

    1. Obtiene datos de guía (sin y con detalle)
    2. Mapea a Remesa usando remesaMapperV2
    3. Crea remesa en Transprensa
    4. Imprime y obtiene PDF
    5. Descarga PDF
    6. Guarda PDF en BD

    Args:
        picking: Código de picking
        bigpedido: Número de pedido

    Returns:
        Dict con respuesta de Transprensa + metadata:
        {
            "success": bool,
            "picking": str,
            "bigpedido": str,
            "remesa_numero": str (si se creó),
            "pdf_saved": bool,
            "msg": str,
            "tiempo_ms": int
        }
    """
    start_time = time.time()
    picking = str(picking).strip()
    bigpedido = str(bigpedido).strip()

    # Validaciones básicas
    if not picking or not bigpedido:
        return {
            "success": False,
            "picking": picking,
            "bigpedido": bigpedido,
            "remesa_numero": "",
            "pdf_saved": False,
            "msg": "picking y bigpedido son requeridos",
            "tiempo_ms": 0,
        }

    try:
        # PASO 1: Obtener datos de guía (sin y con detalle)
        print(
            f"[PASO 1] Obteniendo datos de guía: picking={picking}, bigpedido={bigpedido}"
        )

        guia_comparativa = clientService.get_guide_data_comparative(picking, bigpedido)

        if not guia_comparativa:
            total_time = int((time.time() - start_time) * 1000)
            return {
                "success": False,
                "picking": picking,
                "bigpedido": bigpedido,
                "remesa_numero": "",
                "pdf_saved": False,
                "msg": "No se encontraron datos de guía",
                "tiempo_ms": total_time,
            }

        # PASO 2: Mapear a Remesa usando remesaMapperV2
        print("[PASO 2] Mapeando guía a Remesa")
        remesa_mapeada = mapear_guia_a_remesa(guia_comparativa)

        if not remesa_mapeada:
            total_time = int((time.time() - start_time) * 1000)
            return {
                "success": False,
                "picking": picking,
                "bigpedido": bigpedido,
                "remesa_numero": "",
                "pdf_saved": False,
                "msg": "No se pudo mapear la guía a remesa",
                "tiempo_ms": total_time,
            }

        # PASO 3: Crear remesa en Transprensa
        print("[PASO 3] Creando remesa en Transprensa")

        # Crear payload usando crear_payload_api
        payload = crear_payload_api([guia_comparativa])

        create_response = clientService.create_remesas(payload)

        if not create_response.get("success"):
            total_time = int((time.time() - start_time) * 1000)
            error_msg = create_response.get("msg", "Error desconocido en creación")
            return {
                "success": False,
                "picking": picking,
                "bigpedido": bigpedido,
                "remesa_numero": "",
                "pdf_saved": False,
                "msg": f"Error al crear remesa: {error_msg}",
                "tiempo_ms": total_time,
            }

        # Extraer número de remesa creada
        remesa_creada_numero = ""
        data = create_response.get("data", [])
        if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
            remesa_creada_numero = str(data[0].get("remesa", "")).strip()

        if not remesa_creada_numero:
            total_time = int((time.time() - start_time) * 1000)
            return {
                "success": False,
                "picking": picking,
                "bigpedido": bigpedido,
                "remesa_numero": "",
                "pdf_saved": False,
                "msg": "Remesa creada pero no se obtuvo número",
                "tiempo_ms": total_time,
            }

        print(f"✓ Remesa creada: {remesa_creada_numero}")

        # PASO 4: Obtener PDF (print/impresión)
        print("[PASO 4] Obteniendo PDF de remesa")
        print_response = clientService.print_remesas([remesa_creada_numero])

        if not print_response.get("success"):
            total_time = int((time.time() - start_time) * 1000)
            return {
                "success": True,  # Remesa creada pero sin PDF
                "picking": picking,
                "bigpedido": bigpedido,
                "remesa_numero": remesa_creada_numero,
                "pdf_saved": False,
                "msg": f"Remesa creada. Error en PDF: {print_response.get('msg', 'Error desconocido')}",
                "tiempo_ms": total_time,
            }

        # Extraer URL del PDF de la respuesta
        pdf_data = print_response.get("data", {})
        pdf_url = (
            pdf_data.get(remesa_creada_numero, "") if isinstance(pdf_data, dict) else ""
        )

        if not pdf_url:
            total_time = int((time.time() - start_time) * 1000)
            return {
                "success": True,  # Remesa creada pero sin URL de PDF
                "picking": picking,
                "bigpedido": bigpedido,
                "remesa_numero": remesa_creada_numero,
                "pdf_saved": False,
                "msg": "Remesa creada. No se obtuvo URL del PDF",
                "tiempo_ms": total_time,
            }

        # PASO 5: Descargar PDF
        print("[PASO 5] Descargando PDF")
        pdf_content = download_pdf_from_url(pdf_url)

        if not pdf_content:
            total_time = int((time.time() - start_time) * 1000)
            return {
                "success": True,  # Remesa creada pero no se descargó PDF
                "picking": picking,
                "bigpedido": bigpedido,
                "remesa_numero": remesa_creada_numero,
                "pdf_saved": False,
                "msg": "Remesa creada. Error descargando PDF",
                "tiempo_ms": total_time,
            }

        pdf_base64 = base64.b64encode(pdf_content).decode("utf-8")
        print(f"✓ PDF descargado ({len(pdf_content)} bytes)")

        # PASO 6: Guardar PDF en BD
        print("[PASO 6] Guardando PDF en BD")
        save_result = clientService.save_guide_pdf(
            remesa_num=remesa_creada_numero, picking=picking, pdf_base64=pdf_base64
        )

        pdf_saved = (
            save_result.get("success", False)
            if isinstance(save_result, dict)
            else False
        )

        if pdf_saved:
            print("✓ PDF guardado correctamente")

        # RESPUESTA FINAL
        total_time = int((time.time() - start_time) * 1000)

        return {
            "success": True,
            "picking": picking,
            "bigpedido": bigpedido,
            "remesa_numero": remesa_creada_numero,
            "pdf_saved": pdf_saved,
            "msg": "Guía procesada exitosamente",
            "tiempo_ms": total_time,
        }

    except Exception as e:
        total_time = int((time.time() - start_time) * 1000)
        print(f"✗ Error: {e}")
        return {
            "success": False,
            "picking": picking,
            "bigpedido": bigpedido,
            "remesa_numero": "",
            "pdf_saved": False,
            "msg": f"Error inesperado: {str(e)}",
            "tiempo_ms": total_time,
        }
