"""Dependencies"""

import json
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt


""" Functions and models """
from wmsAdapterV2.functions.ProductionOrder.bulk_create import (
    create_list_production_order,
)
from wmsAdapterV2.functions.ProductionOrder.read import read_production_orders
from wmsAdapterV2.functions.ProductionOrder.update import update_production_order
from wmsAdapterV2.utils.create_response import created_response, created_response_orders


@csrf_exempt
def production_order(request):
    """
    This view is used to create, read, update and delete purchase_orders
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
            response, _, _ = read_production_orders(request, db_name=db_name)

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
            print(len(request_data))
            print(request_data)
        except Exception as e:
            print(str(e))
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
            created, created_detail, errors = create_list_production_order(
                None, db_name=db_name, request_data=request_data
            )

            print(created)
            print(errors)
            return created_response_orders(created, created_detail, errors)
        # If there is an error
        except Exception as e:
            print(str(e))
            return JsonResponse({"error": str(e)}, safe=False, status=500)

    # Update an article
    if request.method == "PUT":

        try:
            # Check the request data
            request_data = json.loads(request.body)
        except Exception as e:
            print(e)
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
            created, errors = update_production_order(
                request, db_name=db_name, request_data=request_data
            )

        # If there is an error
        except Exception as e:
            return JsonResponse({"error": str(e)}, safe=False, status=500)

        # Return the response
        return created_response(created, errors, "update")


# Get storage by location
# if request.method == 'DELETE':

#     try:
#         # Delete the articles
#         response = delete_articles(request, db_name=db_name)
#         if response == 'Deleted successfully':
#             return JsonResponse({'success': 'Deleted successfully'}, safe=False, status=200)
#         else:
#             return JsonResponse({'error': response}, safe=False, status=400)
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, safe=False, status=500)
