from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from contapyme.functions.operaciones.read import read_operations

@csrf_exempt
def operaciones(request):
    if request.method == 'GET':
        itdoper = request.GET.get('itdoper', None)
        quantity = request.GET.get('quantity', None)
        
        if not itdoper:
            return JsonResponse({'Error': 'No operation identifier provided'}, safe=False, status=400)
        
        try:
            db_name = request.db_name
            # Get Operations
            response = read_operations(db_name, itdoper, quantity)
            
            if response:
                return JsonResponse(response, safe=False, status=200)
            else:
                return JsonResponse({'Error': 'Operation does not exist in ContaPyme'}, safe=False, status=403)
            
        # If there is an error    
        except Exception as e:
            return JsonResponse({'Error': str(e)}, safe=False, status=500)