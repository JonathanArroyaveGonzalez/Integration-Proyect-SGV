def update_multiple_records(params):
    # Initialize limit
    mult = 0

    # Check if limit is in params
    if 'multiple_records' in params:
        try: 
            mult = int(params['multiple_records'][0])
        except Exception:
            raise ValueError('multiple_records must be an integer')
        params.pop('multiple_records')
        
    return mult, params
         
        