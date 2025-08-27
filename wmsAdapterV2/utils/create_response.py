from django.http import JsonResponse


def created_response(created:list, errors:list, type):
    '''
    This function return the response for the created articles
    @params:
        created: list of created articles
        errors: list of errors
    '''
    try:
        if type == 'create':
            key = 'created'
        elif type == 'update':
            key = 'updated'
        else:
            key = 'deleted'

        # Initialize response
        response = {}

        # Check if there are created articles
        if len(created) > 0 and len(errors) == 0:
            response =  JsonResponse( 
                    {key: created, 'errors': errors}, safe=False, status=201)
        
        # Check if there are created articles and errors
        if len(created) > 0 and len(errors) > 0:
            response = JsonResponse( 
                    {key: created, 'errors': errors}, safe=False, status=207)

        # Check if there are created articles
        if len(created) == 0 and len(errors) > 0:
            response = JsonResponse({key: created, 'errors': errors}, safe=False, status=400)
        
         # Check if there are created articles
        if len(created) == 0 and len(errors) == 0:
            response = JsonResponse(
                {key: ["All records already exist"], "errors": errors}, safe=False, status=200
            )

        # Return the response
        return response
    except Exception as e:
        return JsonResponse({'error': str(e)}, safe=False, status=500)


def created_response_orders(created: list, created_detail:list, errors: list):
    """
    This function return the response for the created articles
    @params:
        created: list of created articles
        errors: list of errors
    """
    try:
        # Initialize response
        response = {}

        # Check if there are created articles
        if (len(created) + len(created_detail)) > 0 and len(errors) == 0:
            response = JsonResponse(
                {"order": created, "detail":created_detail, "errors": errors}, safe=False, status=201
            )

        # Check if there are created articles and errors
        if (len(created) + len(created_detail)) > 0 and len(errors) > 0:
            response = JsonResponse(
                {"order": created, "detail":created_detail, "errors": errors}, safe=False, status=207
            )

        # Check if there are created articles
        if (len(created) + len(created_detail)) == 0 and len(errors) > 0:
            response = JsonResponse(
                {"order": created, "detail":created_detail, "errors": errors}, safe=False, status=400
            )
        
        # Check if there are created articles
        if (len(created) + len(created_detail)) == 0 and len(errors) == 0:
            response = JsonResponse(
                {"order": ["All records already exist"], "detail": ["All records already exist"], "errors": errors}, safe=False, status=200
            )

        # Return the response
        return response
    except Exception as e:
        return JsonResponse({"error": str(e)}, safe=False, status=500)
