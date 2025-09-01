from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from contapyme.functions.pedido.read import read_orders

@csrf_exempt
def pedido(request):
    snumsop = request.GET.get('snumsop', None)
    type_order = request.GET.get('type', None)
    if not snumsop:
        return JsonResponse({'Error': 'No order identifier provided'}, safe=False, status=400)
    
    if request.method == 'GET':
        try:
            db_name = request.db_name
            response = read_orders(db_name, type_order, snumsop)
            
            # Check the response  
            if response:
                return JsonResponse(response, safe=False, status=200)
            else:
                return JsonResponse({'Error': 'Order does not exist in ContaPyme'}, safe=False, status=403)
        
            
        # If there is an error    
        except Exception as e:
            return JsonResponse({'Error': str(e)}, safe=False, status=500)