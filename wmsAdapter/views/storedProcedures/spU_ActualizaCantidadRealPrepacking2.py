
from urllib import request
from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse
from datetime import date
from ...utils.utils import *
import json
# CARGAMOS LA TABLA DE PLAN DESPACHOS


def ejecutar_entrega(cantidad,eandecaja,iddetprepack,lote, numcaja, idempleado,database):


    query = f'''
        select max(dpe.IddetPripack) IddetPripack
            from [CO_PQD_BASE].[dbo].[t_detalle_prepack] dpe
            inner join
                (
                select d.numpicking,d.product
                from [CO_PQD_BASE].[dbo].[t_detalle_prepack] d
                where d.iddetpripack={iddetprepack}
                ) dc on dpe.product=dc.product and dpe.numpicking=dc.numpicking
            where dpe.estadolinea=0  
        '''
    
    try:
        response = exec_query(query, database=database)
        iddetprepack = response[0]['IddetPripack']
    
    except Exception as e:
        raise Exception(e)

    sp = '''SET NOCOUNT ON
        EXEC [CO_PQD_BASE].[dbo].[spU_ActualizaCantidadRealPrepacking2] %s, %s, %s, %s, %s, %s'''
    
    print(sp % (cantidad, eandecaja, iddetprepack, lote, numcaja, idempleado))

    # Query que se hace directamente a la base de datos
    try:
        response = exec_query(
            sp, (cantidad, eandecaja, iddetprepack, lote, numcaja, idempleado), database=database)
        return iddetprepack, response
    except Exception as e:
        print(e)
        raise Exception(e)

    



@csrf_exempt
def picking(request):
    
    request_data = json.loads(request.body)
    print(request_data)
    database = request.db_name
    print(database)

    if database != 'pqd':
        return JsonResponse('Database error!', safe=False, status=500)
    

    if request.method == 'POST':

        success = []
        error = []

        if type(request_data) == list:

            for r in request_data:

                #make all fields lowercase
                r = {k.lower(): v for k, v in r.items()}

                try:
                    iddetprepack, response = ejecutar_entrega(**r, database=database)
                    r['iddetprepack'] = iddetprepack
                    success.append(r)
                except Exception as e:
                    r['mensaje'] = str(e)
                    error.append(r)
               
            return JsonResponse({"success": success, "error": error}, safe=False, status=200)
        
        elif type(request_data) == dict:
                
                #make all fields lowercase
                request_data = {k.lower(): v for k, v in request_data.items()}
                
                try:
                    iddetprepack, response = ejecutar_entrega(**request_data, database=database)
                    request_data['iddetprepack'] = iddetprepack
                    success.append(request_data)
                except Exception as e:
                    request_data['mensaje'] = str(e)
                    error.append(request_data)
                
                return JsonResponse({"success": success, "error": error}, safe=False, status=200)
          
