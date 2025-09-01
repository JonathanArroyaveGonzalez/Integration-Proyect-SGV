from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from contapyme.functions.operaciones.charging_document import create_charging_document
from contapyme.functions.sync_orders import return_ddc_orders

@csrf_exempt
def ddc(request):
    try:
        db_name = request.db_name
    except Exception as e:
        return JsonResponse({'error': 'Apikey error'}, safe=False, status=500)

    if request.method == 'POST':
        doctoerp = request.GET.get('doctoerp', None)
        
        try:
            if not doctoerp:
                response = return_ddc_orders(db_name)
                return JsonResponse(response, safe=False, status=200)
                
            response = create_charging_document(db_name, doctoerp)
            if response:
                return JsonResponse(response, safe=False, status=200)
            else:
                return JsonResponse({'Error': 'Charging document on ContaPyme failed'}, safe=False, status=403)
            
        # If there is an error    
        except Exception as e:
            return JsonResponse({'Error': str(e)}, safe=False, status=500)