import json


def validate_request_data(request, type_data, request_data=None):
    if request_data:
        if not isinstance(request_data, list) and type_data == list:
            request_data = [request_data]
    elif request.body:
        request_data = json.loads(request.body)
    else:
        raise ValueError('No data to create')
    
    if not isinstance(request_data, type_data):
        raise ValueError(f"The provided data should be a {type_data}.")
    
    return request_data