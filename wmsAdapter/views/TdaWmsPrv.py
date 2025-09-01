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
def prv(request):

    try:
        db_name = request.db_name
    
    except Exception as e:
        return JsonResponse({'error': 'Apikey error'}, safe=False, status=500)

    # Get products
    if request.method == 'GET':

        try:
            response = read_prv(request, db_name=db_name)
            if type(response) == str:
                return JsonResponse({'message': response}, status=400)
            else:
                response_json = list(response.values())
                return JsonResponse(response_json, safe=False, status=200)
        except Exception as e:
            print(e)
            return JsonResponse({'error': 'Error getting prv'}, safe=False, status=500)

  # Create a new article
    if request.method == 'POST':
        try:
            # response = 'created successfully's
            response = create_prv(request, db_name=db_name)
            if response == 'created successfully':
                return JsonResponse({'success': 'Prv created'}, safe=False, status=200)
            else:
                return JsonResponse({'error': response}, safe=False, status=500)
        except Exception as e:
            print(str(e))
            return JsonResponse({'error': 'Error creating prv'}, safe=False, status=500)


  # Update an article
    if request.method == 'PUT':

        try:
            response = update_prv(request, db_name=db_name)
            if response == 'Updated successfully':
                return JsonResponse({'success': 'Updated successfully'}, safe=False, status=200)
            else:
                return JsonResponse({'error': response}, safe=False, status=500)
        except Exception as e:
            print(e)
            return JsonResponse({'error': 'Error updating the register'}, safe=False, status=500)


 # Get storage by location
    if request.method == 'DELETE':

        try:
            response = delete_prv(request, db_name=db_name)
            if response == 'Deleted successfully':
                return JsonResponse({'success': 'Deleted successfully'}, safe=False, status=200)
            else:
                return JsonResponse({'error': response}, safe=False, status=500)
        except Exception as e:
            print(e)
            return JsonResponse({'error': 'Error deleting prv'}, safe=False, status=500)
