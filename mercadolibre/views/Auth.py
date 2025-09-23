"""Dependencies"""

from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from mercadolibre.functions.Auth.mongo_config import get_meli_config
from mercadolibre.functions.Auth.refresh_token import refresh_meli_tokens


@csrf_exempt
def auth(request):
    """
    This view is used to refresh MercadoLibre authentication tokens
    @params:
        request: request object
    """

    # Handle GET requests for configuration check
    if request.method == "GET":
        try:
            # Get current configuration (without sensitive data)
            config = get_meli_config()

            return JsonResponse(
                {
                    "success": True,
                    "message": "MercadoLibre configuration found",
                    "client_id": config.get("client_id", "Not found"),
                    "api_base_url": config.get("api_base_url", "Not found"),
                    "has_tokens": bool(
                        config.get("access_token") and config.get("refresh_token")
                    ),
                },
                safe=False,
                status=200,
            )

        except Exception as e:
            return JsonResponse(
                {
                    "success": False,
                    "error": str(e),
                    "message": "Failed to get MercadoLibre configuration",
                },
                safe=False,
                status=500,
            )

    # Only allow POST requests for token refresh
    elif request.method == "POST":
        try:
            # Call the refresh tokens function
            result = refresh_meli_tokens()

            # Return success response
            return JsonResponse(result, safe=False, status=200)

        except Exception as e:
            # Return error response
            return JsonResponse(
                {
                    "success": False,
                    "error": str(e),
                    "message": "Failed to refresh MercadoLibre tokens",
                },
                safe=False,
                status=500,
            )

    # Handle invalid methods
    else:
        return JsonResponse(
            {
                "success": False,
                "error": "Method not allowed",
                "message": "Only GET and POST methods are allowed",
            },
            safe=False,
            status=405,
        )
