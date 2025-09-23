from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from mercadolibre.functions.Products.sync import sync_products_to_wms

@csrf_exempt
@require_http_methods(["POST"])
def sync_products_view(request):
    """
    Endpoint para sincronizar productos de MercadoLibre con el WMS
    
    POST /wms/ml/v1/products/sync/
    Headers: Authorization: Bearer <token>
    """
    try:
        # Obtener headers de autorización del request
        auth_headers = {}
        if 'HTTP_AUTHORIZATION' in request.META:
            auth_headers['Authorization'] = request.META['HTTP_AUTHORIZATION']
        elif 'Authorization' in request.headers:
            auth_headers['Authorization'] = request.headers['Authorization']
        
        # Ejecutar sincronización pasando los headers
        result = sync_products_to_wms(auth_headers=auth_headers)
        
        if result["success"]:
            return JsonResponse({
                "status": "success",
                "message": result["message"],
                "data": result.get("data", {})
            }, status=200)
        else:
            return JsonResponse({
                "status": "error",
                "message": result["message"]
            }, status=400)
            
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": f"Error interno del servidor: {str(e)}"
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def sync_status_view(request):
    """
    Endpoint para verificar el estado de la sincronización
    
    GET /wms/ml/v1/products/sync/status/
    """
    return JsonResponse({
        "status": "ready",
        "message": "Servicio de sincronización disponible",
        "endpoints": {
            "sync": "/wms/ml/v1/products/sync/",
            "status": "/wms/ml/v1/products/sync/status/"
        }
    })

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
        # Obtener headers de autorización del request
        auth_headers = {}
        if 'HTTP_AUTHORIZATION' in request.META:
            auth_headers['Authorization'] = request.META['HTTP_AUTHORIZATION']
        elif 'Authorization' in request.headers:
            auth_headers['Authorization'] = request.headers['Authorization']
            
        data = json.loads(request.body)
        product_ids = data.get("product_ids", [])
        
        if not product_ids:
            return JsonResponse({
                "status": "error",
                "message": "Se requiere una lista de product_ids"
            }, status=400)
        
        from mercadolibre.functions.Products.sync import get_product_details, map_products_to_wms_format, send_products_to_wms
        
        # Obtener detalles de productos específicos
        meli_items = get_product_details(product_ids)
        
        if not meli_items:
            return JsonResponse({
                "status": "error",
                "message": "No se pudieron obtener detalles de los productos especificados"
            }, status=400)
        
        # Mapear y enviar al WMS con headers de autorización
        wms_products = map_products_to_wms_format(meli_items)
        result = send_products_to_wms(wms_products, auth_headers=auth_headers)
        
        if result["success"]:
            return JsonResponse({
                "status": "success",
                "message": result["message"],
                "data": result.get("data", {})
            }, status=200)
        else:
            return JsonResponse({
                "status": "error",
                "message": result["message"]
            }, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({
            "status": "error",
            "message": "JSON inválido en el cuerpo de la solicitud"
        }, status=400)
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": f"Error interno del servidor: {str(e)}"
        }, status=500)