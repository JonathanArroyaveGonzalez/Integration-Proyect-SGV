from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from contapyme.functions.tercero.list import list_thirdparty
from contapyme.functions.tercero.read import read_thirdparty

@csrf_exempt
def tercero(request):
    if request.method == 'GET':
        db_name = request.db_name
        init = request.GET.get('init', None)
        if not init:
            response = list_thirdparty(db_name)

            # Check the response  
            if response:
                return JsonResponse(response, safe=False, status=200)
            else:
                return JsonResponse({'Error': 'Third Party does not exist in ContaPyme'}, safe=False, status=403)

        try:
            # Get client
            response = read_thirdparty(db_name, init)

            # Check the response  
            if response:
                return JsonResponse(response, safe=False, status=200)
            else:
                return JsonResponse({'Error': 'Third Party does not exist in ContaPyme'}, safe=False, status=403)
                    
            
        # If there is an error    
        except Exception as e:
            return JsonResponse({'Error': str(e)}, safe=False, status=500)