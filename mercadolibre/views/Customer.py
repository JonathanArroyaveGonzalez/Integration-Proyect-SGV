from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import logging
from mercadolibre.functions.Customer.create import create_customer_in_wms
from mercadolibre.functions.Customer.update import update_customer_in_wms

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def create_customer(request):
    try:
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

        # Extraer IDs - puede ser uno solo o múltiples
        ml_customer_ids = []

        # Caso 1: Un solo ID
        if "ml_customer_id" in request_data:
            ml_customer_ids = [request_data["ml_customer_id"]]

        # Caso 2: Múltiples IDs
        elif "ml_customer_ids" in request_data:
            ml_customer_ids = request_data["ml_customer_ids"]
            if not isinstance(ml_customer_ids, list):
                return JsonResponse(
                    {"created": [], "errors": ["ml_customer_ids debe ser una lista"]},
                    status=400,
                )

        # Sin IDs
        else:
            return JsonResponse(
                {
                    "created": [],
                    "errors": ["Debes enviar 'ml_customer_id' o 'ml_customer_ids'"],
                },
                status=400,
            )

        # Procesar cada ID
        all_created = []
        all_errors = []

        for customer_id in ml_customer_ids:
            if not customer_id:
                all_errors.append("ID vacío encontrado")
                continue

            logger.info(f"Creando cliente ML: {customer_id}")
            result = create_customer_in_wms(customer_id)

            # Agregar resultados
            if "created" in result:
                all_created.extend(result["created"])
            if "errors" in result:
                all_errors.extend(result["errors"])

        # Determinar status code
        if all_created and not all_errors:
            status_code = 201  # Solo éxitos
        elif all_created and all_errors:
            status_code = 207  # Éxitos parciales
        else:
            status_code = 400  # Solo errores

        return JsonResponse(
            {"created": all_created, "errors": all_errors}, status=status_code
        )

    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}")
        return JsonResponse(
            {"created": [], "errors": [f"Error interno: {str(e)}"]}, status=500
        )


# views.py - Vista de actualización


@csrf_exempt
@require_http_methods(["PUT", "PATCH"])  # Métodos HTTP para actualización
def update_customer(request):
    """
    Endpoint para actualizar clientes desde MercadoLibre.
    Acepta un ID o múltiples IDs.
    """
    try:
        # Parse JSON
        try:
            request_data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse(
                {"created": [], "errors": ["JSON inválido"]}, status=400
            )

        # Extraer IDs (mismo formato que creación)
        ml_customer_ids = []
        if "ml_customer_id" in request_data:
            ml_customer_ids = [request_data["ml_customer_id"]]
        elif "ml_customer_ids" in request_data:
            ml_customer_ids = request_data["ml_customer_ids"]
            if not isinstance(ml_customer_ids, list):
                return JsonResponse(
                    {"created": [], "errors": ["ml_customer_ids debe ser una lista"]},
                    status=400,
                )
        else:
            return JsonResponse(
                {
                    "updated": [],
                    "errors": ["Envía 'ml_customer_id' o 'ml_customer_ids'"],
                },
                status=400,
            )

        # Procesar todos los IDs
        all_updated = []
        all_errors = []

        for customer_id in ml_customer_ids:
            if not customer_id:
                all_errors.append("ID vacío ignorado")
                continue

            result = update_customer_in_wms(customer_id)
            # Para actualización, "created" significa "updated"
            all_updated.extend(result.get("created", []))
            all_errors.extend(result.get("errors", []))

        # Status code basado en resultados
        if all_updated and not all_errors:
            status_code = 200  # OK para actualización exitosa
        elif all_updated and all_errors:
            status_code = 207  # Multi-Status
        else:
            status_code = 400  # Bad Request

        return JsonResponse(
            {
                "created": all_updated,  # El WMS usa "created" incluso para updates
                "errors": all_errors,
            },
            status=status_code,
        )

    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}")
        return JsonResponse(
            {"created": [], "errors": ["Error interno del servidor"]}, status=500
        )
