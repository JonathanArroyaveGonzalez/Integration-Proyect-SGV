""" Dependencies """
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from wmsBase.functions.Warehouse.read import read_cellars

@csrf_exempt
def bod(request):
    '''
    This view is used to read cellars
    @params:
        request: request object
    '''
    try:
        # Get the database name
        db_name = request.db_name
    except Exception as e:
        return JsonResponse({'error': 'Unauthorized'}, safe=False, status=401)

    # Get products
    if request.method == 'GET':

        try:
            # Get articles
            response, _ = read_cellars(request, db_name=db_name)

            # Check the response
            return JsonResponse(response, safe=False, status=200)
            
        # If there is an error    
        except Exception as e:
            return JsonResponse({'error': str(e)}, safe=False, status=500)
