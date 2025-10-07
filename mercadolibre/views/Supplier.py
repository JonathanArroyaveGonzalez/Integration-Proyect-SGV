from dataclasses import asdict
import json
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from mercadolibre.functions.Supplier.sync import get_supplier_sync_service
from mercadolibre.functions.Supplier.update import update_single_supplier


@method_decorator(csrf_exempt, name="dispatch")
class SupplierSyncView(View):
    def post(self, request, *args, **kwargs):
        try:
            body = json.loads(request.body.decode("utf-8"))
            supplier_ids = body.get("supplier_ids")
            supplier_id = body.get("supplier_id")

            if supplier_id:
                supplier_ids = [supplier_id]

            if not supplier_ids:
                return JsonResponse(
                    {
                        "success": False,
                        "message": "No se proporcionaron IDs de suppliers",
                    },
                    status=400,
                )

            results = get_supplier_sync_service().sync_specific_suppliers(
                supplier_ids, original_request=request
            )
            return JsonResponse(results, status=200, safe=False)

        except Exception as e:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Error inesperado en la sincronización",
                    "error": str(e),
                },
                status=500,
            )

    def put(self, request, *args, **kwargs):
        try:
            body = json.loads(request.body.decode("utf-8"))
            supplier_id = body.get("supplier_id")

            if not supplier_id:
                return JsonResponse(
                    {"success": False, "message": "supplier_id es requerido"},
                    status=400,
                )

            result = update_single_supplier(supplier_id, original_request=request)

            # Determinar el código de estado HTTP apropiado
            status_code = 200
            if not result.success:
                if result.error == "invalid_supplier_id":
                    status_code = 400
                elif result.error == "meli_not_found":
                    status_code = 404
                elif result.error == "supplier_not_found_in_wms":
                    status_code = 404
                else:
                    status_code = 500

            return JsonResponse(asdict(result), status=status_code)

        except Exception as exception:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Error inesperado al actualizar el supplier",
                    "error": str(exception),
                },
                status=500,
            )
