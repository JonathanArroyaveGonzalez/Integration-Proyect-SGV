"""
Vista para actualización de productos individuales desde MercadoLibre hacia WMS
"""

import json
import logging
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from mercadolibre.functions.Product.update import update_product_from_meli_to_wms
from mercadolibre.utils.response_helpers import (
    create_success_response,
    create_error_response,
    handle_json_decode_error,
    handle_internal_server_error,
)
from mercadolibre.utils.auth_helpers import extract_auth_headers

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
        if not product_id or not product_id.strip():
            return create_error_response(
                message="ID de producto requerido",
                errors="Debe proporcionar un ID de producto válido",
                status=400,
            )

        # Extraer headers de autenticación usando utilidad
        auth_headers = extract_auth_headers(request)

        # Ejecutar la actualización
        result = update_product_from_meli_to_wms(product_id, auth_headers)

        # Procesar resultado y determinar respuesta
        return _process_update_result(result)

    except Exception as e:
        logger.exception(f"Error inesperado actualizando producto {product_id}")
        return handle_internal_server_error(
            e, f"actualización de producto {product_id}"
        )


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
        # Validar y parsear JSON del request
        try:
            request_data = json.loads(request.body)
        except json.JSONDecodeError:
            return handle_json_decode_error()

        # Validar product_id
        product_id = request_data.get("product_id")
        if not product_id or not str(product_id).strip():
            return create_error_response(
                message="ID de producto requerido",
                errors="Debe proporcionar un product_id válido en el cuerpo de la petición",
                status=400,
            )

        logger.info(
            f"Recibida solicitud POST de actualización para producto: {product_id}"
        )

        # Extraer headers de autenticación usando utilidad
        auth_headers = extract_auth_headers(request)

        # Ejecutar la actualización
        result = update_product_from_meli_to_wms(product_id, auth_headers)

        # Procesar resultado y determinar respuesta
        return _process_update_result(result)

    except Exception as e:
        logger.exception("Error inesperado en endpoint de actualización POST")
        return handle_internal_server_error(e, "actualización de producto via POST")


def _process_update_result(result):
    """
    Procesa el resultado de la actualización y determina la respuesta apropiada

    Args:
        result (dict): Resultado de la función de actualización

    Returns:
        JsonResponse: Respuesta HTTP apropiada
    """
    if result["success"]:
        return create_success_response(
            data=result.get("data", {}), message=result["message"], status=200
        )

    # Determinar código de error basado en el mensaje
    error_message = result["message"].lower()

    if "no se pudo obtener" in error_message:
        status_code = 404
        error_code = "PRODUCT_NOT_FOUND"
    elif any(
        keyword in error_message
        for keyword in ["error mapeando", "product id is required", "invalid"]
    ):
        status_code = 400
        error_code = "INVALID_REQUEST"
    else:
        status_code = 500
        error_code = "INTERNAL_ERROR"

    return create_error_response(
        message=result["message"],
        errors=result.get("errors"),
        status=status_code,
        error_code=error_code,
    )
