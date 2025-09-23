"""Dependencies"""

import json
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt

""" Functions and models """
from wmsAdapterV2.functions.SaleOrder.bulk_create_v2 import (
    create_list_sale_order_without_orm_validation,
)
from wmsAdapterV2.functions.SaleOrder.delete import delete_sale_order
from wmsAdapterV2.functions.SaleOrder.read import read_sale_orders
from wmsAdapterV2.functions.SaleOrder.update import update_sale_order
from wmsAdapterV2.utils.create_response import created_response, created_response_orders


@csrf_exempt
def sale_order(request):
    """
    This view is used to create, read, update and delete articles
    @params:
        request: request object
    """
    try:
        # Get the database name
        db_name = request.db_name
        # print(db_name)
    except Exception as e:
        return JsonResponse({"error": "Unauthorized"}, safe=False, status=401)

    # Get products
    if request.method == "GET":

        try:
            # Get articles
            response, _, _ = read_sale_orders(request, db_name=db_name)

            # Check the response
            return JsonResponse(response, safe=False, status=200)

        # If there is an error
        except Exception as e:
            return JsonResponse({"error": str(e)}, safe=False, status=500)

    # Create a new article
    if request.method == "POST":
        try:
            # Check the request data
            request_data = json.loads(request.body)
            # Solo mostrar información básica de la request
            if db_name == "couca01_test":
                print(f"Request for {db_name}: {len(request_data)} items")

        except Exception as e:
            return JsonResponse(
                {"error": "Error loading the body. Please check and try again"},
                safe=False,
                status=422,
            )

        # Initialize created and errors
        created = []
        errors = []

        try:
            # Create the article
            created, created_detail, error = (
                create_list_sale_order_without_orm_validation(
                    None, db_name=db_name, request_data=request_data
                )
            )

            # Solo mostrar información básica para seguimiento funcional
            if db_name == "couca01_test":
                print(f"Created orders for {db_name}: {len(created)} EPK, {len(created_detail)} DPK")

            return created_response_orders(created, created_detail, error)
        # If there is an error
        except Exception as e:
            return JsonResponse({"error": str(e)}, safe=False, status=500)

    # Update an article
    if request.method == "PUT":

        try:
            # Check the request data
            request_data = json.loads(request.body)
        except Exception as e:
            return JsonResponse(
                {"error": "Error loading the body. Please check and try again"},
                safe=False,
                status=422,
            )

        # Initialize created and errors
        created = []
        errors = []

        # Check if the request data is a list

        try:
            # Create the article
            created, errors = update_sale_order(
                request, db_name=db_name, request_data=request_data
            )

        # If there is an error
        except Exception as e:
            return JsonResponse({"error": str(e)}, safe=False, status=500)

        # Return the response
        return created_response(created, errors, "update")

    if request.method == "DELETE":

        try:
            # Check the request data
            request_data = json.loads(request.body)
        except Exception as e:
            request_data = {}

        # Initialize created and errors
        created = []
        errors = []

        # Check if the request data is a list

        try:
            # Create the article
            created, errors = delete_sale_order(
                request, db_name=db_name, request_data=request_data
            )

        # If there is an error
        except Exception as e:
            return JsonResponse({"error": str(e)}, safe=False, status=500)

        # Return the response
        return created_response(created, errors, "delete")
