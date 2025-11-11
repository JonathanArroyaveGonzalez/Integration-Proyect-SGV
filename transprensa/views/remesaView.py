"""
Vista para procesar el workflow completo de remesas y guías.

Endpoints:
- GET/POST /wms/tp/v1/guia/procesar/ -> Procesa una guía completamente
"""

import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from transprensa.functions.create import execute_guide_workflow


@csrf_exempt
@require_http_methods("POST")
def procesar_guia(request):
    """
    Procesa UNA GUÍA completamente:
    1. Obtiene datos (sin y con detalle)
    2. Mapea a Remesa
    3. Crea en Transprensa
    4. Obtiene PDF
    5. Descarga y guarda PDF en background
    POST (Query Parameters):
        /wms/tp/v1/guia/procesar/?picking=7746&bigpedido=PD-103888

    Returns:
        JSON con resultado del procesamiento
    """
    try:
        data = json.loads(request.body)
        picking = data.get("picking", "").strip()
        bigpedido = data.get("bigpedido", "").strip()


        if not picking or not bigpedido:
            return JsonResponse(
                {
                    "success": False,
                    "picking": picking,
                    "bigpedido": bigpedido,
                    "remesa_numero": "",
                    "pdf_saved": False,
                    "estado": "error",
                    "msg": 'Faltan parámetros. Requeridos: picking, bigpedido',
                },
                status=400,
            )

        result = execute_guide_workflow(picking, bigpedido)

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