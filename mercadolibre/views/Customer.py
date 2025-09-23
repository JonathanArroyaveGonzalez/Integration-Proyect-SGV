from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import logging
from mercadolibre.functions.Customer.sync_customer import (
    create_customer_in_wms,
    update_customer_in_wms,
)

logger = logging.getLogger(__name__)


def _extract_auth_headers(request):
    """
    Extrae los headers de autorización del request de Django
    """
    auth_headers = {}
    if "HTTP_AUTHORIZATION" in request.META:
        auth_headers["Authorization"] = request.META["HTTP_AUTHORIZATION"]
    elif "Authorization" in request.headers:
        auth_headers["Authorization"] = request.headers["Authorization"]
    return auth_headers


def _extract_customer_ids(request_data):
    """
    Extrae y valida los IDs de clientes del request
    Returns: (ml_customer_ids, error_response)
    """
    ml_customer_ids = []

    if "ml_customer_id" in request_data:
        ml_customer_ids = [request_data["ml_customer_id"]]
    elif "ml_customer_ids" in request_data:
        ml_customer_ids = request_data["ml_customer_ids"]
        if not isinstance(ml_customer_ids, list):
            return None, JsonResponse(
                {"created": [], "errors": ["ml_customer_ids debe ser una lista"]},
                status=400,
            )
    else:
        return None, JsonResponse(
            {
                "created": [],
                "errors": ["Debes enviar 'ml_customer_id' o 'ml_customer_ids'"],
            },
            status=400,
        )

    return ml_customer_ids, None


def _determine_status_code(created, errors):
    """
    Determina el código de estado HTTP basado en los resultados
    """
    if created and not errors:
        return 201  # Solo éxitos (para create) / 200 (para update)
    elif created and errors:
        return 207  # Éxitos parciales (Multi-Status)
    else:
        return 400  # Solo errores


@csrf_exempt
@require_http_methods(["POST"])
def create_customer(request):
    try:
        # Extraer headers de autorización
        auth_headers = _extract_auth_headers(request)

        # Parse JSON
        try:
            request_data = json.loads(request.body)
        except json.JSONDecodeError:
            logger.warning("Request con JSON inválido")
            return JsonResponse(
                {
                    "created": [],
                    "errors": ["Invalid JSON - Please provide valid JSON data"],
                },
                status=400,
            )

        # Extraer y validar IDs
        ml_customer_ids, error_response = _extract_customer_ids(request_data)
        if error_response:
            return error_response

        # Procesar cada ID
        all_created = []
        all_errors = []

        for customer_id in ml_customer_ids:
            if not customer_id:
                all_errors.append("ID vacío encontrado")
                continue

            logger.info(f"Creando cliente ML: {customer_id}")
            result = create_customer_in_wms(customer_id, auth_headers=auth_headers)

            all_created.extend(result.get("created", []))
            all_errors.extend(result.get("errors", []))

        status_code = _determine_status_code(all_created, all_errors)
        if status_code == 201:  # Ajuste para create
            status_code = 201
        elif status_code == 200:
            status_code = 201  # Create siempre usa 201

        return JsonResponse(
            {"created": all_created, "errors": all_errors}, status=status_code
        )

    except Exception as e:
        logger.error(f"Error inesperado en create_customer: {str(e)}", exc_info=True)
        return JsonResponse(
            {"created": [], "errors": [f"Error interno: {str(e)}"]}, status=500
        )


@csrf_exempt
@require_http_methods(["PUT", "PATCH"])
def update_customer(request):
    """
    Endpoint para actualizar clientes desde MercadoLibre.
    Acepta un ID o múltiples IDs.
    """
    try:
        # Extraer headers de autorización
        auth_headers = _extract_auth_headers(request)

        # Parse JSON
        try:
            request_data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse(
                {"Updated": [], "errors": ["JSON inválido"]}, status=400
            )

        # Extraer y validar IDs
        ml_customer_ids, error_response = _extract_customer_ids(request_data)
        if error_response:
            # Ajustar mensaje de error para update
            if error_response.content:
                content = json.loads(error_response.content)
                if "updated" in content:
                    content["updated"] = content.pop("updated")
                    error_response.content = json.dumps(content)
            return error_response

        # Procesar todos los IDs
        all_updated = []
        all_errors = []

        for customer_id in ml_customer_ids:
            if not customer_id:
                all_errors.append("ID vacío ignorado")
                continue

            logger.info(f"Actualizando cliente ML: {customer_id}")
            result = update_customer_in_wms(customer_id, auth_headers=auth_headers)

            all_updated.extend(result.get("updated", []))  # WMS usa "created"
            all_errors.extend(result.get("errors", []))

        status_code = _determine_status_code(all_updated, all_errors)
        if status_code == 201:  # Ajuste para update
            status_code = 200  # Update usa 200, no 201

        return JsonResponse(
            {
                "updated": all_updated,  # Mantener consistencia con WMS
                "errors": all_errors,
            },
            status=status_code,
        )

    except Exception as e:
        logger.error(f"Error inesperado en update_customer: {str(e)}", exc_info=True)
        return JsonResponse(
            {"updated": [], "errors": ["Error interno del servidor"]}, status=500
        )
