# -*- coding: utf-8 -*-
"""
Vista para procesar el workflow completo de remesas y guías.

Endpoints:
- POST /api/remesa/procesar/ -> Ejecuta workflow completo end-to-end (MÚLTIPLES órdenes)
- POST /api/guia/procesar/ -> Procesa UNA SOLA guía completamente (NUEVO - V2)
- GET /wms/tp/v1/guia/obtener/ -> Obtiene guía comparativa (sin y con detalle)
- POST /api/remesa/procesar_multiple/ -> Procesa múltiples guías (solo obtención)
"""

import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from transprensa.functions.create import execute_guide_workflow_v2


@csrf_exempt
@require_http_methods(["GET", "POST"])
def procesar_guia(request):
    """
    NUEVO FLUJO V2 - Procesa UNA SOLA GUÍA completamente:
    1. Obtiene datos (sin y con detalle)
    2. Mapea a Remesa
    3. Crea en Transprensa
    4. Obtiene PDF
    5. Descarga PDF
    6. Guarda en BD

    Soporta GET y POST:

    GET (Query Parameters):
    /wms/tp/v1/guia/procesar/?picking=7746&bigpedido=PD-103888

    POST (Body JSON):
    {
        "picking": "7746",
        "bigpedido": "PD-103888"
    }

    Salida JSON:
    {
        "success": true,
        "picking": "7746",
        "bigpedido": "PD-103888",
        "remesa_numero": "103999",
        "pdf_saved": true,
        "estado": "completado",
        "msg": "Guía procesada exitosamente",
        "tiempo_ms": 5234
    }
    """
    try:
        # Obtener parámetros según el método
        if request.method == "GET":
            # Obtener de query parameters
            picking = request.GET.get("picking", "").strip()
            bigpedido = request.GET.get("bigpedido", "").strip()
        else:
            # Obtener de body JSON (POST)
            body = {}
            if request.body:
                try:
                    body = json.loads(request.body.decode("utf-8"))
                except json.JSONDecodeError:
                    return JsonResponse(
                        {
                            "success": False,
                            "picking": "",
                            "bigpedido": "",
                            "remesa_numero": "",
                            "pdf_saved": False,
                            "estado": "error",
                            "msg": "Body debe ser JSON válido",
                        },
                        status=400,
                    )

            picking = str(body.get("picking", "")).strip()
            bigpedido = str(body.get("bigpedido", "")).strip()

        # Validar parámetros requeridos
        if not picking or not bigpedido:
            return JsonResponse(
                {
                    "success": False,
                    "picking": picking,
                    "bigpedido": bigpedido,
                    "remesa_numero": "",
                    "pdf_saved": False,
                    "estado": "error",
                    "msg": 'Faltan parámetros. Requeridos: picking, bigpedido. GET: ?picking=7746&bigpedido=PD-103888 o POST: {"picking": "7746", "bigpedido": "PD-103888"}',
                },
                status=400,
            )

        result = execute_guide_workflow_v2(picking, bigpedido)

        # Retornar resultado
        status_code = 200 if result.get("success") else 400
        return JsonResponse(result, status=status_code)

    except Exception as e:
        return JsonResponse(
            {
                "success": False,
                "picking": "",
                "bigpedido": "",
                "remesa_numero": "",
                "pdf_saved": False,
                "estado": "error",
                "msg": f"Error inesperado: {str(e)}",
            },
            status=500,
        )
