"""
Vista para operaciones CRUD básicas de productos en MercadoLibre
"""

from django.views.decorators.csrf import csrf_exempt
import json

from mercadolibre.utils.api_client import make_authenticated_request, get_meli_api_base_url
from mercadolibre.utils.response_helpers import (
    create_success_response,
    create_error_response,
    handle_json_decode_error,
    handle_internal_server_error,
    handle_request_validation
)


@csrf_exempt
def art(request):
    """
    Vista para operaciones CRUD básicas de productos en MercadoLibre
    
    GET: Lista productos del usuario
    POST: Crea un nuevo producto
    
    @params:
        request: request object de Django
    """
    # Validar métodos permitidos
    allowed_methods = ["GET", "POST"]
    method_validation = handle_request_validation(request, allowed_methods)
    if method_validation:
        return method_validation
    
    try:
        base_url = get_meli_api_base_url()
        
        # GET: Listar productos del usuario
        if request.method == "GET":
            return _handle_get_products(base_url)
        
        # POST: Crear nuevo producto
        elif request.method == "POST":
            return _handle_create_product(request, base_url)
            
    except Exception as e:
        return handle_internal_server_error(e, "operaciones de productos")


def _handle_get_products(base_url):
    """
    Maneja la obtención de productos del usuario desde MercadoLibre
    """
    try:
        url = f"{base_url}users/me/items/search"
        response = make_authenticated_request('GET', url)
        
        if response.status_code == 200:
            return create_success_response(
                data=response.json(),
                message="Productos obtenidos exitosamente"
            )
        else:
            return create_error_response(
                message="Error obteniendo productos de MercadoLibre",
                errors=f"API error: {response.status_code} - {response.text}",
                status=response.status_code
            )
            
    except Exception as e:
        return handle_internal_server_error(e, "obtención de productos")


def _handle_create_product(request, base_url):
    """
    Maneja la creación de un nuevo producto en MercadoLibre
    """
    try:
        # Validar y parsear JSON del request
        try:
            request_data = json.loads(request.body)
        except json.JSONDecodeError:
            return handle_json_decode_error()
        
        # Crear producto en MercadoLibre
        url = f"{base_url}items"
        response = make_authenticated_request('POST', url, json=request_data)
        
        if response.status_code == 201:
            return create_success_response(
                data=response.json(),
                message="Producto creado exitosamente",
                status=201
            )
        else:
            return create_error_response(
                message="Error creando producto en MercadoLibre",
                errors=f"API error: {response.status_code} - {response.text}",
                status=response.status_code
            )
            
    except Exception as e:
        return handle_internal_server_error(e, "creación de producto")