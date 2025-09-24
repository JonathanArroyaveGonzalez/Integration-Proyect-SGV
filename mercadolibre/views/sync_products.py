from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

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

        # Obtener parámetros opcionales del body si existe
        use_parallel = True  # Por defecto usar paralelización
        assume_new = True   # Por defecto asumir productos nuevos
        
        try:
            if request.body:
                data = json.loads(request.body)
                use_parallel = data.get("use_parallel", True)
                assume_new = data.get("assume_new", True)
        except json.JSONDecodeError:
            # Si no hay body válido, usar valores por defecto
            pass

        # Ejecutar sincronización con optimizaciones
        if use_parallel:
            # Usar versión paralela optimizada (por defecto)
            from mercadolibre.functions.Product.sync import sync_products_to_wms_parallel
            result = sync_products_to_wms_parallel(auth_headers=auth_headers, assume_new=assume_new)
        else:
            # Usar versión secuencial como fallback
            from mercadolibre.functions.Product.sync import sync_products_to_wms
            result = sync_products_to_wms(auth_headers=auth_headers)

        if result["success"]:
            # Agregar información de optimización en la respuesta
            response_data = result.copy()
            response_data["optimization_info"] = {
                "parallel_execution": result.get("parallel_execution", False),
                "assume_new": result.get("assume_new", False),
                "sync_type": result.get("sync_type", "legacy")
            }
            
            return create_success_response(
                data=response_data,
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
    Incluye procesamiento optimizado de códigos de barras

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

        # Importar función optimizada paralela
        from mercadolibre.functions.Product.sync import sync_specific_products_to_wms_parallel

        # Obtener parámetros opcionales
        assume_new = data.get("assume_new", True)
        use_parallel = data.get("use_parallel", True)  # Por defecto usar paralelización
        
        # Elegir función según configuración
        if use_parallel:
            # Usar versión paralela optimizada (por defecto)
            result = sync_specific_products_to_wms_parallel(
                product_ids=product_ids, 
                auth_headers=auth_headers, 
                assume_new=assume_new
            )
        else:
            # Usar versión secuencial como fallback
            from mercadolibre.functions.Product.sync import sync_specific_products_to_wms
            result = sync_specific_products_to_wms(
                product_ids=product_ids, 
                auth_headers=auth_headers, 
                assume_new=assume_new
            )

        if result["success"]:
            # Crear respuesta con información detallada de optimización
            response_data = {
                "products": result.get("products_data", {}),
                "barcodes_sync": {
                    "processed": result.get("barcodes_processed", 0),
                    "errors": result.get("barcodes_errors_count", 0),
                    "strategies_used": result.get("strategies_used", {}),
                    "success_details": result.get("barcodes_data", []),
                    "error_details": result.get("barcodes_errors", [])
                },
                "optimization": {
                    "assume_new": result.get("assume_new", False),
                    "optimization_used": result.get("optimization_used", False),
                    "parallel_execution": result.get("parallel_execution", False),
                    "use_parallel": use_parallel
                }
            }
            
            return create_success_response(
                data=response_data,
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
