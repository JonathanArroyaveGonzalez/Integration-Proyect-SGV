"""MercadoLibre customer synchronization views - Unified and readable architecture."""

import json
import logging
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from mercadolibre.functions.Customer.sync import get_customer_sync_service
from mercadolibre.functions.Customer.update import get_customer_update_service
from mercadolibre.utils.response_helpers import get_response_status_code

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name="dispatch")
class MeliCustomerSyncView(View):
    """
    Unified view for customer synchronization operations.
    Handles:
    - POST: Sync specific customers
    - PUT: Update single customer
    """

    def __init__(self):
        """Initialize the sync and update service singletons."""
        super().__init__()
        self.sync_service = get_customer_sync_service()
        self.update_service = get_customer_update_service()

    def post(self, request):
        """
        Sync specific customers by their MercadoLibre IDs.

        Expected JSON:
        {
            "customer_ids": ["123", "456"],  # Required: list of ML customer IDs
            "force_update": false            # Optional: force update existing customers
        }

        Returns:
            JSON response with sync results
        """
        try:
            # Step 1: Parse JSON body
            data = json.loads(request.body)
            customer_ids = data.get("customer_ids", [])
            force_update = data.get("force_update", False)

            # Step 2: Validate input
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

            # Step 3: Call the sync service (clear and readable)
            sync_service = self.sync_service  # singleton service
            result = sync_service.sync_specific_customers(
                customer_ids=customer_ids,
                original_request=request,
                force_update=force_update,
            )

            # Step 4: Determine response status code and return
            status_code = get_response_status_code(result)
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

    def put(self, request):
        """
        Update a single customer from MercadoLibre to WMS.

        Expected JSON:
        {
            "customer_id": "123"  # Required: ML customer ID
        }

        Returns:
            JSON response with update results
        """
        try:
            # Step 1: Parse JSON body
            data = json.loads(request.body)
            customer_id = data.get("customer_id")

            # Step 2: Validate input
            if not customer_id:
                return JsonResponse(
                    {"success": False, "message": "No customer_id provided"}, status=400
                )

            if isinstance(customer_id, list):
                if len(customer_id) == 1:
                    customer_id = customer_id[0]
                    logger.warning(
                        f"customer_id was provided as list, extracted single value: {customer_id}"
                    )
                else:
                    return JsonResponse(
                        {
                            "success": False,
                            "message": "customer_id should be a single string, not a list",
                        },
                        status=400,
                    )

            customer_id = str(customer_id)  # ensure it's a string

            logger.info(f"Updating customer {customer_id}")

            # Step 3: Call the update service (singleton)
            update_service = self.update_service
            result = update_service.update_single_customer(customer_id, request)

            # Step 4: Determine response status code and return
            status_code = get_response_status_code(result)
            return JsonResponse(result, status=status_code)

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
