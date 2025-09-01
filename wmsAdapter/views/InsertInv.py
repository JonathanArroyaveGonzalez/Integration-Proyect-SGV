from datetime import datetime
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
# from django.shortcuts import render_to_response

@csrf_exempt
def insertinv(request):

    try:
        db_name = request.db_name
    
    except Exception as e:
        return JsonResponse({'error': 'Apikey error'}, safe=False, status=500)

    # Get products
    if request.method == 'POST':
        try:
            with connections[db_name].cursor() as cursor:

                    query = f"EXECUTE [dbo].[Insert_TDA_WMS_INV]"
                    # query = '''execute [Insert_TDA_WMS_INV] '''
                    cursor.execute(query)

                    f = open("wmsAdapter/logs/InsertInv.log", "a")
                    f.write(f"{datetime.now()} - {db_name}  - Insert TDA_WMS_INV OK " +  "\n")
                    f.close()   
                    cursor.close()
                    
                    return JsonResponse({'success': "Insert TDA_WMS_INV OK"}, status=200)
        except Exception as e:
            print(e)
            f = open("wmsAdapter/logs/InsertInv.log", "a")
            f.write(f"{datetime.now()} - {db_name}  - Insert TDA_WMS_INV ERROR "+ str(e) + "\n")
            f.close()      
            return JsonResponse({'error': str(e)}, safe=False, status=500)
