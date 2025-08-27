"""Functions"""

import re

# from settings import get_apikeys
from django.conf import settings

""" Dependencies """
from django.http.response import JsonResponse


class MiddlewareApiKey:
    """
    This middleware is used to validate the apikey
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):

        # Get endpoint
        endpoint = request.get_full_path()
        print(request)

        # print(endpoint)

        # Split endpoint
        endpoint = endpoint.split("?")

        # This endpoint doesn't need apikey validation
        if endpoint[0] == "/create-apikey":
            return None
        elif endpoint[0] == "/health_check":
            return JsonResponse({"status": "ok"}, status=200)
        else:
            try:
                # print(dict(request.GET))
                # print(request.body)

                # Get apikeys from mongo
                apikeys = settings.API_KEYS
                # apikeys = get_apikeys()

                # Get apikey from request
                ak = request.headers["Authorization"]
                # print(ak)

                # Validate apikey
                db_name = apikeys[ak]
                print(db_name)

                # add db_name to request
                try:
                    # This validates the endpoint to get the database name. It is base if the endpoint is wms/base/...

                    # This regex would return a list with the endpoint, in this case ['base']
                    validate_endpoint = re.findall(r"wms\/(.*?)\/", endpoint[0])

                    # Check if the list is not empty
                    if len(validate_endpoint) > 0:

                        # The regex would be used like this:
                        if validate_endpoint[0] == "base":

                            # The database name would be db_name + '_base'
                            request.db_name = db_name + "_base"
                        else:

                            # The database name would be db_name which is the adapter database
                            request.db_name = db_name

                    # If the list is empty, the endpoint is wms/...
                    else:

                        # The database name would be db_name which is the adapter database
                        request.db_name = db_name

                # If something goes wrong, the database name would be db_name which is the adapter database
                except Exception:
                    request.db_name = db_name

            # If the apikey is not valid, return an auth error
            except Exception:
                return JsonResponse({"error": "Unauthorized"}, safe=False, status=401)

        return None
