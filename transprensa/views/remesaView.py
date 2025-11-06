# -*- coding: utf-8 -*-
"""
Vista para procesar el workflow completo de remesas.

Endpoint único:
- POST /api/remesa/procesar/ -> Ejecuta workflow completo end-to-end
"""

import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

from transprensa.functions.create import executeRemesaWorkflow


@csrf_exempt
@require_http_methods(["POST"])
def procesar_remesa(request):
    """
    Procesa remesas desde órdenes: obtiene, mapea, crea, obtiene guías y almacena.

    Entrada JSON:
    {
        "order_ids": ["103888", "103889"]
    }

    Salida JSON (formato limpio tipo Transprensa):
    {
        "success": true,
        "data": [
            {
                "orden": "103888",
                "remesa": "103999",
                "validacion": "",
                "success": true
            },
            {
                "orden": "103889",
                "remesa": "",
                "validacion": "Mensaje de error",
                "success": false
            }
        ],
        "msg": "OK | [ 2145 ]"
    }
    """
    try:
        # Parsear JSON del body
        body = {}
        if request.body:
            try:
                body = json.loads(request.body.decode("utf-8"))
            except json.JSONDecodeError:
                return JsonResponse(
                    {
                        "success": False,
                        "data": [],
                        "msg": "Body debe ser JSON válido",
                    },
                    status=400,
                )

        # Validar presencia de order_ids
        order_ids = body.get("order_ids", [])
        if not order_ids or not isinstance(order_ids, list):
            return JsonResponse(
                {
                    "success": False,
                    "data": [],
                    "msg": 'Falta "order_ids" o no es una lista. Envía: {"order_ids": ["123", "456"]}',
                },
                status=400,
            )

        # Convertir IDs a strings
        order_ids = [str(oid).strip() for oid in order_ids if oid]

        if not order_ids:
            return JsonResponse(
                {
                    "success": False,
                    "data": [],
                    "msg": "Proporciona al menos una order_id válida",
                },
                status=400,
            )

        # Ejecutar workflow - ya devuelve formato limpio
        result = executeRemesaWorkflow(order_ids)

        # Retornar resultado
        status_code = 200 if result.get("success") else 400
        return JsonResponse(result, status=status_code)

    except Exception as e:
        return JsonResponse(
            {
                "success": False,
                "data": [],
                "msg": f"Error inesperado: {str(e)}",
            },
            status=500,
        )
