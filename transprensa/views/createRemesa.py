"""
Vistas para crear y guardar guías de remesa en Transprensa.

Este módulo maneja el flujo completo de:
1. Recibir órdenes (por IDs o directamente)
2. Construir payload de remesas
3. Crear remesas en Transprensa
4. Imprimir y descargar PDFs
5. Guardar guías en la base de datos
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

from transprensa.services.responseService import response_service

# Importar funciones del paquete remesas
from transprensa.functions.remesas import (
    parseRequestPayload,
    getInternalService,
    collectOrdersFromIds,
    buildRemesasFromOrders,
    createRemesasInTransprensa,
    printRemesasInTransprensa,
    extractCreatedRemesas,
    processPdfDownloadsAndSaves,
    extractPdfUrlsFromResponse,
)


@csrf_exempt
@require_http_methods(["POST"])
def crear_y_guardar_guia_view(request):
    """
    Crea y guarda guías de remesa en Transprensa.

    Endpoint: POST /remesas/v2

    Request:
        { "orders_ids": ["103888", "103979"] }

    Response (Success):
        {
            "success": true,
            "message": "Remesas creadas y guardadas",
            "data": {
                "created_remesas": ["100001", "100002"],
                "saved": 2,
                "errors": 0
            }
        }

    Response (Error):
        {
            "success": false,
            "message": "descripción del error"
        }

    Status codes:
        200: Operación completada
        400: Input inválido
        404: No se encontraron órdenes
        500: Error interno
        502: Error de Transprensa
    """
    # Parsear entrada
    parsed = parseRequestPayload(request)
    ids = parsed["ids"]
    incoming_orders = parsed["orders"]
    dry_run = parsed["dry_run"]

    try:
        service = getInternalService()

        # Reunir órdenes
        orders = (
            incoming_orders if incoming_orders else collectOrdersFromIds(service, ids)
        )

        # Construir payload
        preview = buildRemesasFromOrders(service, orders)
        if not preview.get("success"):
            return JsonResponse(preview, status=400)

        payload = preview.get("payload", {})
        remesas_payload = payload.get("remesas", [])

        # Dry run: devolver preview
        if dry_run:
            return JsonResponse(
                {
                    "success": True,
                    "message": "Vista previa (dry_run=true)",
                    "data": {
                        "remesas": len(remesas_payload),
                        "missing_city_codes": preview["stats"]["missing_city_codes"],
                    },
                },
                status=200,
            )

        # Crear remesas en Transprensa
        tp_create = createRemesasInTransprensa(payload)
        created_nums = extractCreatedRemesas(tp_create)

        # Imprimir remesas (obtener URLs)
        tp_print = printRemesasInTransprensa(created_nums)
        pdf_map = extractPdfUrlsFromResponse(tp_print)

        # Descargar y guardar PDFs
        saved, errors = processPdfDownloadsAndSaves(
            service, created_nums, remesas_payload, pdf_map
        )

        return JsonResponse(
            {
                "success": True,
                "message": "Remesas creadas y guardadas",
                "data": {
                    "created_remesas": created_nums,
                    "saved": len(saved),
                    "errors": len(errors),
                },
            },
            status=200,
        )

    except Exception as e:
        error_msg = f"Error: {str(e)}"
        print(f"[REMESA] ERROR: {error_msg}")
        return JsonResponse(
            response_service.format_error_response(error_msg),
            status=500,
        )
