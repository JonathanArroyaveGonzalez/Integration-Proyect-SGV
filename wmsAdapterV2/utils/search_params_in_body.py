from json import loads


def search_params_in_body(request, params):
    body = request.body
    if body:
        body = loads(body)
        if body:
            for key, value in body.items():
                if key in params:
                    print(value)
                    params[key] = params[key][0] + "," + value
                else:
                    params[key] = [value]

    return params