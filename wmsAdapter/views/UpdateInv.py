from datetime import datetime
from urllib import response
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
#from bigcommerce.functions.products.update import *
# from django.shortcuts import render_to_response

# @csrf_exempt
# def updatetinv(request):

#     try:
#         db_name = request.db_name
    
#     except Exception as e:
#         return JsonResponse({'error': 'Apikey error'}, safe=False, status=500)

#     # Get products
#     if request.method == 'POST':
#         try:
#             with connections[db_name].cursor() as cursor:

#                     if(request.body):
#                         request_data = json.loads(request.body)
#                         # print(request_data)
#                         f = open("wmsAdapter/logs/UpdateInv.log", "a")
#                         f.write(f"{datetime.now()} - {db_name}  - " + str(request_data) + "\n")
#                         f.close()   
#                         response = put_product_inv_bigcommerce_by_sku(sku=request_data['ean'], inv= request_data['inventario'], db_name=db_name)
#                         # print(response)
#                         f = open("wmsAdapter/logs/UpdateInv.log", "a")
#                         f.write(f"{datetime.now()} - {db_name}  - UPDATE TDA_WMS_INV OK" + "\n")
#                         f.close()   
    

#                         return JsonResponse({'success': response}, status=200)

#                     else:
#                         return JsonResponse({'warning': "There is nothing to update"}, status= 400)
#         except Exception as e:
#             print(e)
#             f = open("wmsAdapter/logs/UpdateInv.log", "a")
#             f.write(f"{datetime.now()} - {db_name}  - UPDATE TDA_WMS_INV ERROR " + str(e) + "\n")
#             f.close()  
#             return JsonResponse({'error': str(e)}, safe=False, status=500)
