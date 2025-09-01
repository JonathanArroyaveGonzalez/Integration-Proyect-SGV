""" Dependencis """
from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse

""" Models and functions """
from wmsAdapter.models.TdaWmsConsultasDinamicas import TdaWmsConsultasDinamicas
from wmsAdapter.functions.TdaWmsConsultasAleatorias.read import read_consultas_dinamicas
from wmsAdapter.functions.TdaWmsConsultasAleatorias.create import create_consultas_dinamicas
from wmsAdapter.functions.TdaWmsConsultasAleatorias.update import update_consultas_dinamicas
from wmsAdapter.functions.TdaWmsConsultasAleatorias.delete import delete_consultas_dinamicas

""" View """

@csrf_exempt
def consultasDinamicas(request):
    '''
    This view is used to get, create, update and delete consultasDinamicas
    '''
    try:
        
        # Get the database name
        db_name = request.db_name

        print(db_name)
    
    except Exception as e:
        return JsonResponse({'error': 'Apikey error'}, safe=False, status=500)

    # Get dynamic queries
    if request.method == 'GET':

        try:
            response = read_consultas_dinamicas(request, db_name=db_name)
            return JsonResponse(list(response.values()), safe=False, status=200)  # type: ignore
        except Exception as e:
            print(e)
            return JsonResponse({'message': str(e)}, safe=False, status=500)

  # Create dynamic queries
    if request.method == 'POST':
        try:
            response = create_consultas_dinamicas(request, db_name=db_name)
            return JsonResponse(response, safe=False, status=200)
        except Exception as e:
            print(e)
            return JsonResponse({'error': str(e)}, safe=False, status=500)


  # Update 
    if request.method == 'PUT':
        try:
            response = update_consultas_dinamicas(request, db_name=db_name)
            if response == 'Updated successfully':
                return JsonResponse({'success': 'Updated successfully'}, safe=False, status=200)
            else:
                return JsonResponse({'error': response}, safe=False, status=500)
        except Exception as e:
            print(e)
            return JsonResponse({'error': 'Error updating the register'}, safe=False, status=500)


    if request.method == 'DELETE':

        try:
            response = delete_consultas_dinamicas(request, db_name=db_name)
            if response == 'Deleted successfully':
                return JsonResponse({'success': 'Deleted successfully'}, safe=False, status=200)
            else:
                return JsonResponse({'error': response}, safe=False, status=500)
        except Exception as e:
            print(e)
            return JsonResponse({'error': 'Error deleting consultasDinamicas'}, safe=False, status=500)
