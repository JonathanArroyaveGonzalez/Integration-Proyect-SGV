from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

from mercadolibre.functions.Products.sync import sync_products_to_wms
from mercadolibre.utils.response_helpers import (
    create_success_response,
    create_error_response,
    handle_json_decode_error,
    handle_internal_server_error
)
from mercadolibre.utils.auth_helpers import extract_auth_headers


@csrf_exempt
@require_http_methods(["POST"])
def sync_products_view(request):
    """
    Endpoint para sincronizar productos de MercadoLibre con el WMS

    POST /wms/ml/v1/products/sync/
    Headers: Authorization: Bearer <token>
    """
    try:
        # Extraer headers de autorización usando utilidad
        auth_headers = extract_auth_headers(request)

        # Ejecutar sincronización pasando los headers
        result = sync_products_to_wms(auth_headers=auth_headers)

        if result["success"]:
            return create_success_response(
                data=result.get("data", {}),
                message=result["message"],
                status=200
            )
        else:
            return create_error_response(
                message=result["message"],
                status=400
            )

    except Exception as e:
        return handle_internal_server_error(e, "sincronización de productos")


@csrf_exempt
@require_http_methods(["GET"])
def sync_status_view(request):
    """
    Endpoint para verificar el estado de la sincronización

    GET /wms/ml/v1/products/sync/status/
    """
    endpoints_data = {
        "sync": "/wms/ml/v1/products/sync/",
        "status": "/wms/ml/v1/products/sync/status/",
    }
    
    return create_success_response(
        data={"endpoints": endpoints_data},
        message="Servicio de sincronización disponible",
        extra_fields={"status": "ready"}
    )


@csrf_exempt
@require_http_methods(["POST"])
def sync_specific_products_view(request):
    """
    Endpoint para sincronizar productos específicos por IDs

    POST /wms/ml/v1/products/sync/specific/
    Headers: Authorization: Bearer <token>
    Body: {"product_ids": ["MLA123", "MLA456"]}
    """
    try:
        # Extraer headers de autorización usando utilidad
        auth_headers = extract_auth_headers(request)

        # Validar y parsear JSON del request
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return handle_json_decode_error()

        # Validar que se proporcionaron product_ids
        product_ids = data.get("product_ids", [])
        if not product_ids:
            return create_error_response(
                message="Se requiere una lista de product_ids",
                errors="El campo 'product_ids' es obligatorio y debe contener al menos un ID",
                status=400
            )

        # Importar funciones necesarias
        from mercadolibre.functions.Products.sync import (
            get_product_details,
            map_products_to_wms_format,
            send_products_to_wms,
        )

        # Obtener detalles de productos específicos
        meli_items = get_product_details(product_ids)

        if not meli_items:
            return create_error_response(
                message="No se pudieron obtener detalles de los productos especificados",
                errors=f"IDs proporcionados: {product_ids}",
                status=400
            )

        # Mapear y enviar al WMS con headers de autorización
        wms_products = map_products_to_wms_format(meli_items)
        result = send_products_to_wms(wms_products, auth_headers=auth_headers)

        if result["success"]:
            return create_success_response(
                data=result.get("data", {}),
                message=result["message"],
                status=200
            )
        else:
            return create_error_response(
                message=result["message"],
                status=400
            )

    except Exception as e:
        return handle_internal_server_error(e, "sincronización de productos específicos")
