import json
import logging
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from mercadolibre.functions.Customer.sync import get_customer_sync_service
from mercadolibre.functions.Customer.update import get_customer_update_service

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name="dispatch")
class MeliCustomerSyncView(View):
    """
    Unified view for MercadoLibre customer synchronization operations.

    POST: Sync specific customers
    PUT: Update single customer with fallback to create if not exists
    """

    def __init__(self):
        super().__init__()
        self.sync_service = get_customer_sync_service()
        self.update_service = get_customer_update_service()

    # ---------------------
    # POST / Sync customers
    # ---------------------
    def post(self, request):
        try:
            data = json.loads(request.body)
            customer_ids = data.get("customer_ids", [])
            force_update = data.get("force_update", False)

            # Validaciones
            if not customer_ids:
                return JsonResponse(
                    {"success": False, "message": "No customer_ids provided"},
                    status=400,
                )
            if not isinstance(customer_ids, list):
                return JsonResponse(
                    {"success": False, "message": "customer_ids must be a list"},
                    status=400,
                )

            logger.info(
                f"Starting sync for {len(customer_ids)} customers (force_update={force_update})"
            )

            result = self.sync_service.sync_specific_customers(
                customer_ids=customer_ids,
                original_request=request,
            )

            # Status code: 200 si hay al menos un éxito, 500 si todos fallan
            status_code = 200 if result.get("total_created", 0) > 0 else 500
            return JsonResponse(result, status=status_code)

        except json.JSONDecodeError:
            return JsonResponse(
                {"success": False, "message": "Invalid JSON in request body"},
                status=400,
            )
        except Exception as e:
            logger.exception("Error in customer sync endpoint")
            return JsonResponse(
                {"success": False, "message": f"Sync error: {str(e)}", "error": str(e)},
                status=500,
            )

    # ---------------------
    # PUT / Update single customer
    # ---------------------
    def put(self, request):
        try:
            data = json.loads(request.body)
            customer_id = data.get("customer_id")

            # Validaciones
            if not customer_id:
                return JsonResponse(
                    {"success": False, "message": "No customer_id provided"}, status=400
                )
            if isinstance(customer_id, list):
                if len(customer_id) == 1:
                    customer_id = customer_id[0]
                    logger.warning(
                        f"customer_id provided as list, extracted single value: {customer_id}"
                    )
                else:
                    return JsonResponse(
                        {
                            "success": False,
                            "message": "customer_id should be a single string, not a list",
                        },
                        status=400,
                    )

            customer_id = str(customer_id)
            logger.info(f"Updating customer {customer_id}")

            # Llamar al update service
            result = self.update_service.update_single_customer(customer_id, request)

            # Normalizar wms_response para siempre enviar dict
            wms_resp = getattr(result, "wms_response", None) or {}

            response_data = {
                "success": result.success,
                "action": getattr(result, "action", None),
                "message": result.message,
                "wms_response": wms_resp,
                "error": getattr(result, "error", None),
            }

            # Status code: 200 si éxito, updated, created_via_fallback o already_exists
            status_code = (
                200
                if result.success
                or result.action in ["already_exists", "created_via_fallback"]
                else 500
            )

            return JsonResponse(response_data, status=status_code)

        except json.JSONDecodeError:
            return JsonResponse(
                {"success": False, "message": "Invalid JSON in request body"},
                status=400,
            )
        except Exception as e:
            logger.exception("Error in customer update endpoint")
            return JsonResponse(
                {"success": False, "message": f"Unexpected error: {str(e)}"}, status=500
            )
