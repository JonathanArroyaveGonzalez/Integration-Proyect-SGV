from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from contapyme.functions.producto.read import read_items

@csrf_exempt
def producto(request):
    
    if request.method == 'GET':
        irecurso = request.GET.get('irecurso', None)
        if not irecurso:
            return JsonResponse({'Error': 'No item identifier provided'}, safe=False, status=400)

        try:
            # Get Item
            db_name = request.db_name
            response = read_items(db_name, irecurso)

            if response:
                return JsonResponse(response, safe=False, status=200)
            else:
                return JsonResponse({'Error': 'Item does not exist in ContaPyme'}, safe=False, status=403)
            
        # If there is an error    
        except Exception as e:
            return JsonResponse({'Error': str(e)}, safe=False, status=500)