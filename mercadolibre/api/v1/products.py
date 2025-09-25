"""
API v1 - Productos MercadoLibre
Vistas delgadas que delegan en la capa de servicios/funciones y estandarizan respuestas.
"""
from typing import List
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from mercadolibre.services.product_service import (
    list_products as svc_list_products,
    create_product as svc_create_product,
    update_product_from_meli_to_wms as svc_update_product,
)
from mercadolibre.utils.response_helpers import (
    create_success_response,
    create_error_response,
    handle_json_decode_error,
    handle_internal_server_error,
    handle_request_validation,
)
from mercadolibre.utils.auth_helpers import extract_auth_headers


@csrf_exempt
@require_http_methods(["GET", "POST"])
def products(request):
    """
    GET: Lista productos del usuario en ML
    POST: Crea un producto en ML
    """
    try:
        if request.method == "GET":
            result = svc_list_products()
            if result.get("success"):
                return create_success_response(data=result.get("data"), message="Productos obtenidos exitosamente")
            return create_error_response(
                message="Error obteniendo productos de MercadoLibre",
                errors=result.get("errors"),
                status=result.get("status", 500),
            )

        # POST
        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return handle_json_decode_error()

        result = svc_create_product(body)
        if result.get("success"):
            return create_success_response(data=result.get("data"), message="Producto creado exitosamente", status=201)
        return create_error_response(
            message="Error creando producto en MercadoLibre",
            errors=result.get("errors"),
            status=result.get("status", 500),
        )

    except Exception as e:
        return handle_internal_server_error(e, "operaciones de productos")


@csrf_exempt
@require_http_methods(["PUT"])  # Uso explícito de PUT para id en path

def update_product(request, product_id: str):
    """Actualiza un producto específico desde ML hacia WMS."""
    try:
        if not product_id or not product_id.strip():
            return create_error_response(
                message="ID de producto requerido",
                errors="Debe proporcionar un ID de producto válido",
                status=400,
            )

        auth_headers = extract_auth_headers(request)
        result = svc_update_product(product_id, auth_headers)

        if result.get("success"):
            return create_success_response(data=result.get("data", {}), message=result.get("message", "Actualizado"))

        # Mapear errores comunes a códigos HTTP coherentes
        msg = (result.get("message") or "").lower()
        if "no se pudo obtener" in msg:
            status_code = 404
            error_code = "PRODUCT_NOT_FOUND"
        elif any(k in msg for k in ["error mapeando", "invalid", "product id is required"]):
            status_code = 400
            error_code = "INVALID_REQUEST"
        else:
            status_code = 500
            error_code = "INTERNAL_ERROR"

        return create_error_response(
            message=result.get("message", "Error actualizando"),
            errors=result.get("errors"),
            status=status_code,
            error_code=error_code,
        )
    except Exception as e:
        return handle_internal_server_error(e, f"actualización de producto {product_id}")


@csrf_exempt
@require_http_methods(["POST"])  # Alternativa con product_id en body

def update_product_post(request):
    try:
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return handle_json_decode_error()

        product_id = data.get("product_id")
        if not product_id or not str(product_id).strip():
            return create_error_response(
                message="ID de producto requerido",
                errors="Debe proporcionar un product_id válido en el cuerpo de la petición",
                status=400,
            )

        auth_headers = extract_auth_headers(request)
        result = svc_update_product(product_id, auth_headers)
        if result.get("success"):
            return create_success_response(data=result.get("data", {}), message=result.get("message", "Actualizado"))
        return create_error_response(message=result.get("message", "Error actualizando"), status=400)
    except Exception as e:
        return handle_internal_server_error(e, "actualización de producto via POST")


# Reexport de sincronización v1 preservando paths existentes
from django.views.decorators.http import require_http_methods
from mercadolibre.functions.Product.sync import (
    sync_products_to_wms_parallel,
    sync_products_to_wms,
    sync_specific_products_to_wms_parallel,
    sync_specific_products_to_wms,
)


@csrf_exempt
@require_http_methods(["POST"])
def sync_products_view(request):
    try:
        from mercadolibre.utils.auth_helpers import extract_auth_headers
        auth_headers = extract_auth_headers(request)

        use_parallel = True
        assume_new = True
        try:
            if request.body:
                data = json.loads(request.body)
                use_parallel = data.get("use_parallel", True)
                assume_new = data.get("assume_new", True)
        except json.JSONDecodeError:
            pass

        if use_parallel:
            result = sync_products_to_wms_parallel(auth_headers=auth_headers, assume_new=assume_new)
        else:
            result = sync_products_to_wms(auth_headers=auth_headers)

        if result.get("success"):
            response_data = result.copy()
            response_data["optimization_info"] = {
                "parallel_execution": result.get("parallel_execution", False),
                "assume_new": result.get("assume_new", False),
                "sync_type": result.get("sync_type", "legacy"),
            }
            return create_success_response(data=response_data, message=result.get("message", "OK"))
        return create_error_response(message=result.get("message", "Error en sincronización"), status=400)
    except Exception as e:
        return handle_internal_server_error(e, "sincronización de productos")


@csrf_exempt
@require_http_methods(["GET"])
def sync_status_view(request):
    endpoints_data = {
        "sync": "/wms/ml/v1/products/sync/",
        "status": "/wms/ml/v1/products/sync/status/",
    }
    return create_success_response(data={"endpoints": endpoints_data}, message="Servicio de sincronización disponible", extra_fields={"status": "ready"})


@csrf_exempt
@require_http_methods(["POST"])
def sync_specific_products_view(request):
    try:
        from mercadolibre.utils.auth_helpers import extract_auth_headers
        auth_headers = extract_auth_headers(request)
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return handle_json_decode_error()

        product_ids: List[str] = data.get("product_ids", [])
        if not product_ids:
            return create_error_response(
                message="Se requiere una lista de product_ids",
                errors="El campo 'product_ids' es obligatorio y debe contener al menos un ID",
                status=400,
            )

        assume_new = data.get("assume_new", True)
        use_parallel = data.get("use_parallel", True)

        if use_parallel:
            result = sync_specific_products_to_wms_parallel(product_ids=product_ids, auth_headers=auth_headers, assume_new=assume_new)
        else:
            result = sync_specific_products_to_wms(product_ids=product_ids, auth_headers=auth_headers, assume_new=assume_new)

        if result.get("success"):
            response_data = {
                "products": result.get("products_data", {}),
                "barcodes_sync": {
                    "processed": result.get("barcodes_processed", 0),
                    "errors": result.get("barcodes_errors_count", 0),
                    "strategies_used": result.get("strategies_used", {}),
                    "success_details": result.get("barcodes_data", []),
                    "error_details": result.get("barcodes_errors", []),
                },
                "optimization": {
                    "assume_new": result.get("assume_new", False),
                    "optimization_used": result.get("optimization_used", False),
                    "parallel_execution": result.get("parallel_execution", False),
                    "use_parallel": use_parallel,
                },
            }
            return create_success_response(data=response_data, message=result.get("message", "OK"))
        return create_error_response(message=result.get("message", "Error en sincronización específica"), status=400)
    except Exception as e:
        return handle_internal_server_error(e, "sincronización de productos específicos")
