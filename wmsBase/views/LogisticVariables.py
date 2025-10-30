import json
from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse
from wmsAdapterV2.utils.create_response import created_response
from wmsBase.functions.LogisticVariables.bulk_create import create_list_logistic_variables
from wmsBase.functions.LogisticVariables.delete import delete_logistic_variables
from wmsBase.functions.LogisticVariables.read import read_logistic_variables
from wmsBase.functions.LogisticVariables.update import update_logistic_variables



@csrf_exempt
def logistic_variables(request):
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
            response, _ = read_logistic_variables(request, db_name=db_name)

            # Check the response
            return JsonResponse(response, safe=False, status=200)
            
        # If there is an error    
        except Exception as e:
            return JsonResponse({'error': str(e)}, safe=False, status=500)

#   # Create a new article
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
                    created, errors = create_list_logistic_variables(None, db_name=db_name, request_data=request_data)

                # If there is an error
                except Exception as e:
                    return JsonResponse({'error': str(e)}, safe=False, status=500)
                
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
            created, errors = update_logistic_variables(request, db_name=db_name, request_data=request_data)

        # If there is an error
        except Exception as e:
            return JsonResponse({'error': str(e)}, safe=False, status=500)
        
        # Return the response
        return created_response(created, errors, 'update')


 # Get storage by location
    if request.method == 'DELETE':

        try:

            try:
        # Check the request data
                request_data = json.loads(request.body)
            except Exception as e:
                request_data = {}
            
            # Delete the articles
            deleted, errors = delete_logistic_variables(request, db_name, request_data)
        
            return created_response(deleted, errors, 'delete')
        except Exception as e:
            return JsonResponse({'error': str(e)}, safe=False, status=500)


