"""Dependencies"""

import json
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt

""" Functions and models """

from wmsAdapterV2.functions.carrier.read_data_guide import read_data_guide
from wmsAdapterV2.functions.carrier.cancel_guide import cancel_guide
from wmsAdapterV2.functions.carrier.save_guide import save_guide


@csrf_exempt
def carrier(request):
    try:
        # Get the database name
        db_name = request.db_name
    except Exception as e:
        return JsonResponse({"error": "Unauthorized"}, safe=False, status=401)

    # Read information about guide
    if request.method == "GET":
        try:
            picking = request.GET.get("picking", "")
            bigpedido = request.GET.get("bigpedido", "")
            is_detail = request.GET.get("is_detail", "false").lower() == "true"

            response = read_data_guide(
                database=db_name,
                picking=picking,
                bigpedido=bigpedido,
                is_detail=is_detail,
            )
            return JsonResponse(response, safe=False, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, safe=False, status=500)

    # Save guide information
    elif request.method == "POST":
        try:
            request_data = json.loads(request.body)
            delivery_number = request_data.get("delivery_number", "")
            picking = request_data.get("picking", "")
            pdf_base64 = request_data.get("pdf_base64", "")

            response = save_guide(
                database=db_name,
                delivery_number=delivery_number,
                picking=picking,
                pdf_base64=pdf_base64,
            )
            return JsonResponse(response, safe=False, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, safe=False, status=500)

    # Cancel guide information
    elif request.method == "DELETE":
        try:
            request_data = json.loads(request.body)
            delivery_number = request_data.get("delivery_number", "")
            picking = request_data.get("picking", "")

            response = cancel_guide(
                database=db_name, delivery_number=delivery_number, picking=picking
            )
            return JsonResponse(response, safe=False, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, safe=False, status=500)

    else:
        return JsonResponse({"error": "Method not allowed"}, safe=False, status=405)
