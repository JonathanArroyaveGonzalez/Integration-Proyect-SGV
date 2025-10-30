def format_response_from_query_dict(query_dict):
    p = {}
    for key, value in query_dict.items():
        if '__in' in key:
            if len(value) > 1:
                p[key.replace('__in', '')] = value
            elif len(value) == 1:
                p[key.replace('__in', '')] = value[0]
        
        elif '__icontains' in key:
            p[key.replace('__icontains', '')] = "%" + str(value) + "%"

    return p