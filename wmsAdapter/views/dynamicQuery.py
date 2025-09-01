from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse
#from inventory.functions.purchase_orders.read import *
from wmsAdapter.functions.TdaWmsArt.create import create_articles
from wmsAdapter.functions.TdaWmsArt.delete import delete_articles
from wmsAdapter.functions.TdaWmsArt.read import read_articles
from wmsAdapter.functions.TdaWmsArt.update import update_articles
from wmsAdapter.models import *
from settings import *
from django.db.models import Q
from django.utils import timezone
from django.db import connections
from wmsAdapter.utils.reserved_words import get_reserved_words
# from django.shortcuts import render_to_response

@csrf_exempt
def executeSp(request):

    try:
        db_name = request.db_name
    
    except Exception as e:
        return JsonResponse({'error': 'Apikey error'}, safe=False, status=500)

    # Get products
    if request.method == 'POST':
        sp = request.GET.get('sp', None)

        if sp is None:
            return JsonResponse({'error': 'No stored procedure specified'}, safe=False, status=404)

        print(sp)
    
        params = ''
        if(request.body):
            request_data = json.loads(request.body)

            for r in request_data:
                params += str(r) + ' = ' + "'" + str(request_data[r]) + "'" + ', '

            params = params[:-2]

        reserved_words = list(get_reserved_words())
        try:
            if sp != None:
                with connections[db_name].cursor() as cursor:

                    if(params != ''):
                        query = f"EXECUTE [dbo].[{sp}] {params}" 
                    else: 
                        query = f"EXECUTE [dbo].[{sp}]"

                    query_list = str(query).upper().split(' ')


                    for r in reserved_words:
                        if r in query_list:
                            print(r)
                            return JsonResponse({'error': 'Invalid query'}, safe=False, status=400)
                    
                    cursor.execute(query)
                    columns = [col[0] for col in cursor.description] # type: ignore
                    # row = cursor.fetchall()
                    data = [
                        dict(zip(columns, row))
                        for row in cursor.fetchall()
                    ]
                    return JsonResponse({'data': data}, status=200)
        except Exception as e:
            print(e)
            return JsonResponse({'error': str(e)}, safe=False, status=500)
