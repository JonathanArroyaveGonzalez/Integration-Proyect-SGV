"""Dependencies"""

import json
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt

""" Functions and models """
from wmsAdapterV2.functions.Supplier.bulk_supplier import create_list_suppliers
from wmsAdapterV2.functions.Supplier.create import create_prv
from wmsAdapterV2.functions.Supplier.read import read_prv
from wmsAdapterV2.functions.Supplier.update import update_prv
from wmsAdapterV2.utils.create_response import created_response


@csrf_exempt
def prv(request):
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
            response, _ = read_prv(request, db_name=db_name)

            # Check the response
            return JsonResponse(response, safe=False, status=200)

        # If there is an error
        except Exception as e:
            return JsonResponse({"error": str(e)}, safe=False, status=500)

    # Create a new article
    if request.method == "POST":
        try:

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

            # Check if the request data is a list
            if isinstance(request_data, list):
                try:
                    # Create the article
                    created, errors = create_list_suppliers(
                        None, db_name=db_name, request_data=request_data
                    )

                # If there is an error
                except Exception as e:
                    print(str(e))
                    return JsonResponse({"error": str(e)}, safe=False, status=500)

                print(created)
                print(errors)
                # Return the response
                return created_response(created, errors, "create")

            # If the request data is not a list
            elif isinstance(request_data, dict):
                try:
                    # Create the article
                    response = create_prv(request, db_name=db_name)

                    # Append the response
                    created.append(response)

                # If there is an error
                except Exception as e:

                    # Append the error
                    errors.append({"index": "0", "error": str(e)})

                print(created)
                print(errors)
                # Return the response
                return created_response(created, errors, "create")

            # If the request data is not a list or a dict
            else:
                print(str(e))
                return JsonResponse(
                    {"error": "The request data must be a list or a dict"},
                    safe=False,
                    status=400,
                )

        # If there is an error
        except Exception as e:
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
            created, errors = update_prv(
                request, db_name=db_name, request_data=request_data
            )

        # If there is an error
        except Exception as e:
            return JsonResponse({"error": str(e)}, safe=False, status=500)

        # Return the response
        return created_response(created, errors, "update")


#  # Get storage by location
#     if request.method == 'DELETE':

#         try:
#             # Delete the articles
#             response = delete_articles(request, db_name=db_name)
#             if response == 'Deleted successfully':
#                 return JsonResponse({'success': 'Deleted successfully'}, safe=False, status=200)
#             else:
#                 return JsonResponse({'error': response}, safe=False, status=400)
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, safe=False, status=500)


# def created_response(created:list, errors:list):
#     '''
#     This function return the response for the created articles
#     @params:
#         created: list of created articles
#         errors: list of errors
#     '''
#     try:
#         # Initialize response
#         response = {}

#         # Check if there are created articles
#         if len(created) > 0 and len(errors) == 0:
#             response =  JsonResponse(
#                     {'created': created, 'errors': errors}, safe=False, status=201)

#         # Check if there are created articles and errors
#         if len(created) > 0 and len(errors) > 0:
#             response = JsonResponse(
#                     {'created': created, 'errors': errors}, safe=False, status=207)

#         # Check if there are created articles
#         if len(created) == 0 and len(errors) > 0:
#             response = JsonResponse({'created': created, 'errors': errors}, safe=False, status=400)

#         # Return the response
#         return response
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, safe=False, status=500)
