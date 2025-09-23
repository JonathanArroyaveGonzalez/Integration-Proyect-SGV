"""
View for updating products from MercadoLibre to WMS
"""

import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from mercadolibre.functions.Products.update import update_product_from_meli_to_wms

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["PUT"])
def update_product(request, product_id):
    """
    Endpoint para actualizar un producto específico desde MercadoLibre al WMS.
    
    Args:
        request: Request object de Django
        product_id: ID del producto en MercadoLibre
        
    Returns:
        JsonResponse: Resultado de la operación de actualización
    """
    try:
        logger.info(f"Recibida solicitud de actualización para producto: {product_id}")
        
        # Validar que se proporcione un product_id
        if not product_id:
            return JsonResponse({
                "success": False,
                "error": "Product ID is required",
                "message": "Debe proporcionar un ID de producto válido"
            }, status=400)
        
        # Obtener headers de autenticación del request
        auth_headers = {}
        if 'Authorization' in request.headers:
            auth_headers['Authorization'] = request.headers['Authorization']
        
        # Ejecutar la actualización
        result = update_product_from_meli_to_wms(product_id, auth_headers)
        
        # Determinar el código de estado de respuesta
        status_code = 200 if result["success"] else 500
        if not result["success"] and "no se pudo obtener" in result["message"].lower():
            status_code = 404
        elif not result["success"] and ("error mapeando" in result["message"].lower() or 
                                       "product id is required" in result["message"].lower()):
            status_code = 400
        
        return JsonResponse(result, status=status_code)
        
    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "error": "Invalid JSON",
            "message": "El cuerpo de la petición debe ser JSON válido"
        }, status=400)
        
    except Exception as e:
        logger.exception(f"Error inesperado actualizando producto {product_id}")
        return JsonResponse({
            "success": False,
            "error": "Internal server error",
            "message": f"Error interno del servidor: {str(e)}"
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def update_product_post(request):
    """
    Endpoint alternativo para actualizar producto usando POST con product_id en el body.
    
    Args:
        request: Request object de Django
        
    Returns:
        JsonResponse: Resultado de la operación de actualización
    """
    try:
        # Parsear el body del request
        request_data = json.loads(request.body)
        product_id = request_data.get('product_id')
        
        if not product_id:
            return JsonResponse({
                "success": False,
                "error": "Product ID is required",
                "message": "Debe proporcionar un product_id en el cuerpo de la petición"
            }, status=400)
        
        logger.info(f"Recibida solicitud POST de actualización para producto: {product_id}")
        
        # Obtener headers de autenticación del request
        auth_headers = {}
        if 'Authorization' in request.headers:
            auth_headers['Authorization'] = request.headers['Authorization']
        
        # Ejecutar la actualización
        result = update_product_from_meli_to_wms(product_id, auth_headers)
        
        # Determinar el código de estado de respuesta
        status_code = 200 if result["success"] else 500
        if not result["success"] and "no se pudo obtener" in result["message"].lower():
            status_code = 404
        elif not result["success"] and "error mapeando" in result["message"].lower():
            status_code = 400
        
        return JsonResponse(result, status=status_code)
        
    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "error": "Invalid JSON",
            "message": "El cuerpo de la petición debe ser JSON válido"
        }, status=400)
        
    except Exception as e:
        logger.exception("Error inesperado en endpoint de actualización POST")
        return JsonResponse({
            "success": False,
            "error": "Internal server error",
            "message": f"Error interno del servidor: {str(e)}"
        }, status=500)