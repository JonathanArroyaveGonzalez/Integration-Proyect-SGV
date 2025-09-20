"""Dependencies"""

from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from mercadolibre.utils.api_client import make_authenticated_request, get_meli_api_base_url
import json


@csrf_exempt
def art(request):
    """
    This view handles MercadoLibre product operations
    @params:
        request: request object
    """
    
    try:
        base_url = get_meli_api_base_url()
        
        # GET: List user's items
        if request.method == "GET":
            try:
                # Get user's items from MercadoLibre
                url = f"{base_url}users/me/items/search"
                response = make_authenticated_request('GET', url)
                
                if response.status_code == 200:
                    return JsonResponse({
                        "success": True,
                        "data": response.json()
                    }, safe=False, status=200)
                else:
                    return JsonResponse({
                        "success": False,
                        "error": f"MercadoLibre API error: {response.status_code}",
                        "message": response.text
                    }, safe=False, status=response.status_code)
                    
            except Exception as e:
                return JsonResponse({
                    "success": False,
                    "error": str(e),
                    "message": "Failed to get products from MercadoLibre"
                }, safe=False, status=500)
        
        # POST: Create a new item
        elif request.method == "POST":
            try:
                # Get request data
                request_data = json.loads(request.body)
                
                # Create item in MercadoLibre
                url = f"{base_url}items"
                response = make_authenticated_request('POST', url, json=request_data)
                
                if response.status_code == 201:
                    return JsonResponse({
                        "success": True,
                        "data": response.json(),
                        "message": "Product created successfully"
                    }, safe=False, status=201)
                else:
                    return JsonResponse({
                        "success": False,
                        "error": f"MercadoLibre API error: {response.status_code}",
                        "message": response.text
                    }, safe=False, status=response.status_code)
                    
            except json.JSONDecodeError:
                return JsonResponse({
                    "success": False,
                    "error": "Invalid JSON in request body",
                    "message": "Please provide valid JSON data"
                }, safe=False, status=400)
                
            except Exception as e:
                return JsonResponse({
                    "success": False,
                    "error": str(e),
                    "message": "Failed to create product in MercadoLibre"
                }, safe=False, status=500)
        
        # Handle invalid methods
        else:
            return JsonResponse({
                "success": False,
                "error": "Method not allowed",
                "message": "Only GET and POST methods are allowed"
            }, safe=False, status=405)
            
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e),
            "message": "Internal server error"
        }, safe=False, status=500)