""" Dependencies """
import json
from django.utils import timezone
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from wmsAdapter.functions.TdaWmsRelacionSeriales.create import create_relacion_seriales
from wmsAdapter.functions.TdaWmsRelacionSeriales.delete import delete_relacion_seriales
from wmsAdapter.functions.TdaWmsRelacionSeriales.read import read_relacion_seriales
from wmsAdapter.functions.TdaWmsRelacionSeriales.update import update_relacion_seriales

""" Models and functions """


@csrf_exempt
def relacion_seriales(request):
    '''
    This view is used to create, read, update and delete extended articles
    @params:
        request: request object
    '''

    try:
        # Get the database name
        db_name = request.db_name
    except Exception as e:
        return JsonResponse({'error': 'Unauthorized'}, safe=False, status=401)
    
    # Get products extended
    if request.method == 'GET':

        try:

            # Get articles
            response = read_relacion_seriales(request, db_name=db_name)
            
            if type(response) == str:
                return JsonResponse({'message': response}, status=400)
            else:
                response_json = list(response.values())   # type: ignore
                return JsonResponse(response_json, safe=False, status=200)
        except Exception as e:
            print(e)
            return JsonResponse({'error': 'Error getting extended serial'}, safe=False, status=500)
        
    # Create a new article extended
    if request.method == 'POST':
        try:

            # Check the request data
            request_data = json.loads(request.body) 
            
            created = []
            errors = []

            if type(request_data) == list:
                for data in request_data:
                    response = create_relacion_seriales(None, db_name=db_name, request_data=data)
                    if response != 'created successfully':
                        errors.append(data)
                    else:
                        created.append(data)

                return JsonResponse(
                    {'created': created, 'errors': errors}
                    , safe=False, status=200)

            else:
                response = create_relacion_seriales(request, db_name=db_name)
                if response == 'created successfully':
                    return JsonResponse({'success': 'Serial created'}, safe=False, status=200)
                else:
                    return JsonResponse({'error': response}, safe=False, status=500)
        except Exception as e:
            print(e)
            return JsonResponse({'error': 'Error creating relacion serial'}, safe=False, status=500)


    # Update an article
    if request.method == 'PUT':

        try:
            response = update_relacion_seriales(request, db_name=db_name)
            if response == 'Updated successfully':
                return JsonResponse({'success': 'Serial updated'}, safe=False, status=200)
            else:
                return JsonResponse({'error': response}, safe=False, status=500)
        except Exception as e:
            print(e)
            return JsonResponse({'error': 'Error updating extended article'}, safe=False, status=500)
        
    if request.method == 'DELETE':
        try:
            response = delete_relacion_seriales(request, db_name=db_name)
            if response == 'Deleted successfully':
                return JsonResponse({'success': 'Deleted successfully'}, safe=False, status=200)
            else:
                return JsonResponse({'error': response}, safe=False, status=500)
        except Exception as e:
            print(e)
            return JsonResponse({'error': 'Error deleting serial'}, safe=False, status=500)