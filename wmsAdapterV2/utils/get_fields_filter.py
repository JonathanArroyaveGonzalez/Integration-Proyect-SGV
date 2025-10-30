def get_fields_filter(params):
    fields = []
    
    if 'fields' in params:
        try:
            filter_fields = str(params['fields'])
            fields = [field.strip() for field in filter_fields.replace('[','').replace(']','').replace("'","").split(',') if field.strip()]   
        except Exception as e:
            raise ValueError(e)

        params.pop('fields')
    return fields, params