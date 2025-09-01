from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from contapyme.functions.factura.read import read_invoices




@csrf_exempt
def factura(request):
    snumsop = request.GET.get('ord_no', None)
    if not snumsop:
        return JsonResponse({'Error': 'No invoice identifier provided'}, safe=False, status=400)
    
    if request.method == 'GET':
        try:
            db_name = request.db_name
            response = read_invoices(db_name, snumsop)
            
            # Check the response  
            if response:
                return JsonResponse(response, safe=False, status=200)
            else:
                return JsonResponse({'Error': 'Invoice does not exist in ContaPyme'}, safe=False, status=403)
        
            
        # If there is an error    
        except Exception as e:
            return JsonResponse({'Error': str(e)}, safe=False, status=500)
