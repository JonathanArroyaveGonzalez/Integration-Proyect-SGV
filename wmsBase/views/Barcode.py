import json
from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse
from wmsAdapterV2.utils.create_response import created_response
from wmsBase.functions.Barcode.bulk_create import create_list_cod_barras
from wmsBase.functions.Barcode.create import create_t_relacion_codbarras
from wmsBase.functions.Barcode.read import read_t_relacion_codbarras
from wmsBase.functions.Barcode.update import update_barcode



@csrf_exempt
def t_relacion_codbarras(request):
    '''
    This view is used to create, read, update and delete articles
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
            response, _ = read_t_relacion_codbarras(request, db_name=db_name)

            # Check the response
            return JsonResponse(response, safe=False, status=200)
            
        # If there is an error    
        except Exception as e:
            return JsonResponse({'error': str(e)}, safe=False, status=500)

  # Create a new article
    if request.method == 'POST':
        try:

            # Check the request data
            request_data = json.loads(request.body) 
            
            # Initialize created and errors
            created = []
            errors = []

            # Check if the request data is a list
            if isinstance(request_data, list):
                try:
                    # Create the article
                    created, errors = create_list_cod_barras(None, db_name=db_name, request_data=request_data)

                # If there is an error
                except Exception as e:
                    return JsonResponse({'error': str(e)}, safe=False, status=500)
                
                # Return the response
                return created_response(created, errors, 'create')

            # If the request data is not a list
            elif isinstance(request_data, dict):
                try:

                    # Create the article
                    response = create_t_relacion_codbarras(request, db_name=db_name)

                    # Append the response
                    created.append(response)

                # If there is an error
                except Exception as e:

                    # Append the error
                    errors.append({
                            'index': '0',
                            'error': str(e)
                    })
                

                # Return the response
                return created_response(created, errors, 'create')

            # If the request data is not a list or a dict
            else:
                return JsonResponse({'error': 'The request data must be a list or a dict'}, safe=False, status=400)
        
        # If there is an error
        except Exception as e:
            return JsonResponse({'error': str(e)}, safe=False, status=500)


  # Update an article
    if request.method == 'PUT':

        try:
        # Check the request data
            request_data = json.loads(request.body)
        except Exception as e:
            print(e)
            return JsonResponse({'error': 'Error loading the body. Please check and try again'}, safe=False, status=422)
        
        # Initialize created and errors
        created = []
        errors = []

        # Check if the request data is a list
    
        try:
            # Create the article
            created, errors = update_barcode(request, db_name=db_name, request_data=request_data)
            print(created)
            print(errors)
        # If there is an error
        except Exception as e:
            return JsonResponse({'error': str(e)}, safe=False, status=500)
        
        # Return the response
        return created_response(created, errors, 'update')
