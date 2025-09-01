from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from contapyme.functions.compra.read import read_purchase_orders
from contapyme.functions.compra.update import update_purchase_order
from contapyme.functions.sync_orders import return_purchase_orders



@csrf_exempt
def compra(request):
    snumsop = request.GET.get('doctoerp', None)
    
    if request.method == 'GET':
        try:
            if not snumsop:
                return JsonResponse({'Error': 'No order identifier provided'}, safe=False, status=400)
    
            db_name = request.db_name
            response = read_purchase_orders(db_name, snumsop)
            
            # Check the response  
            if response:
                return JsonResponse(response, safe=False, status=200)
            else:
                return JsonResponse({'Error': 'Purchase Order does not exist in ContaPyme'}, safe=False, status=403)
        
            
        # If there is an error    
        except Exception as e:
            return JsonResponse({'Error': str(e)}, safe=False, status=500)
        
        
    elif request.method == 'PUT':
        try:
            db_name = request.db_name
            
            if not snumsop:
                response = return_purchase_orders(db_name)
                return JsonResponse(response, safe=False, status=200)   
                
            response = update_purchase_order(db_name, snumsop)
            # Check the response  
            if response:
                return JsonResponse(response, safe=False, status=200)
            else:
                return JsonResponse({'Error': f'Error updating the purchase order {snumsop} in ContaPyme'}, safe=False, status=403)
        
            
        # If there is an error    
        except Exception as e:
            return JsonResponse({'Error': str(e)}, safe=False, status=500)