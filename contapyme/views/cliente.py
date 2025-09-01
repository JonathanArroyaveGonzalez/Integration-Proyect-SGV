from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from contapyme.functions.cliente.read import read_clients

@csrf_exempt
def cliente(request):
    if request.method == 'GET':

        init = request.GET.get('init', None)
        if not init:
            return JsonResponse({'Error': 'No client identifier provided'}, safe=False, status=400)

        try:
            db_name = request.db_name
            # Get client
            response = read_clients(db_name, init)

            # Check the response  
            if response:
                return JsonResponse(response, safe=False, status=200)
            else:
                return JsonResponse({'Error': 'Client does not exist in ContaPyme'}, safe=False, status=403)
                    
            
        # If there is an error    
        except Exception as e:
            return JsonResponse({'Error': str(e)}, safe=False, status=500)