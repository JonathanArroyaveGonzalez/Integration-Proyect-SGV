from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from contapyme.functions.sync_orders import return_purchase_orders, sync_purchase_orders, sync_req_orders, sync_sales_orders
from contapyme.functions.to_Wms.create_art import create_article
from contapyme.functions.to_Wms.create_clt import create_client
from contapyme.functions.to_Wms.create_prv import create_list_supplier, create_supplier
from contapyme.functions.to_Wms.order import create_order
from contapyme.functions.to_Wms.purchase_order import create_purchase_order



@csrf_exempt
def to_wms(request):
    msg_default = 'Request method not allowed at endpoint'
    try:
        db_name = request.db_name
        description = request.GET.get('description', None)
        parameters = request.GET.get('parameters', None) # valor de doctoerp, productoean o item
        quantity = request.GET.get('quantity', None) # valor de doctoerp, productoean o item

        if request.method == 'POST':
            if not description:
                return JsonResponse({'Error': 'No identifier was provided'}, safe=False, status=400)
            
            if 'ORDENES_COMPRA' in description:
                response = sync_purchase_orders(db_name)
                return JsonResponse(response, safe=False, status=200)
            
            elif 'ORDENES_VENTA' in description:
                response = sync_sales_orders(db_name, quantity)
                return JsonResponse(response, safe=False, status=200)

            elif 'REQUISICION' in description:
                response = sync_req_orders(db_name)
                return JsonResponse(response, safe=False, status=200)

            elif 'EPK_DPK' in description:  
                if 'PED' in parameters:
                    type_order = 'ORD1'  
                elif 'REQ' in parameters:
                    type_order = 'ORD3'

                response = create_order(db_name, type_order, parameters)
                return JsonResponse(response, safe=False, status=200)

            elif 'EUK_DUK' in description:
                response = create_purchase_order(db_name, parameters)
                return JsonResponse(response, safe=False, status=200)

            elif 'CLT' in description:
                response = create_client(db_name, parameters)
                return JsonResponse(response, safe=False, status=200)
                
            elif 'ART' in description:
                response = create_article(db_name, parameters)
                return JsonResponse(response, safe=False, status=200)
            
            elif 'LIST_PRV' in description:
                response = create_list_supplier(db_name)
                return JsonResponse(response, safe=False, status=200)
            
            elif 'PRV' in description:
                response = create_supplier(db_name, parameters)
                return JsonResponse(response, safe=False, status=200)

            else:
                return JsonResponse({'Error': 'No identifier was provided'}, safe=False, status=400)
        
        else:
            return JsonResponse({'Error': msg_default}, safe=False, status=500)

    except Exception as e:
        return JsonResponse({'Error': str(e)}, safe=False, status=500)
