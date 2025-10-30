def validate_fields_not_unique(model, params):
    unique = model._meta.unique_together
    
    model_fields= []
    if unique:
        model_fields = [field for field in unique[0]]
    
    model_fields.append(model._meta.pk.name)

    parameters = {}
    for key, value in params.items():
        if key not in model_fields:
            parameters[key] = value

    return parameters


def validate_fields_not_primary(model, params):
    model_fields= []
    model_fields.append(model._meta.pk.name)

    parameters = {}
    for key, value in params.items():
        if key not in model_fields:
            parameters[key] = value
        else:
            if key != 'id':
                parameters[key] = value

    return parameters