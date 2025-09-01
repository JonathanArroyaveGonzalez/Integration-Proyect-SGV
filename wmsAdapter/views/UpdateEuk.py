from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse
#from inventory.functions.purchase_orders.read import *
from wmsAdapter.functions import *
from wmsAdapter.models import *
from settings import *
from django.db.models import Q
from django.utils import timezone
# from django.shortcuts import render_to_response

@csrf_exempt
def updateEuk(request):

    try:
        db_name = request.db_name
    
    except Exception as e:
        return JsonResponse({'error': 'Apikey error'}, safe=False, status=500)

  # Create a new article
    if request.method == 'POST':
        try:    
            request_body = json.loads(request.body)
            return JsonResponse(request_body, status=200)
        except Exception as e:
            print(e)
            return JsonResponse({'error': 'Error creating euk'}, safe=False, status=500)
