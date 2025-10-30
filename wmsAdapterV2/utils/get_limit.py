def get_limit(params):
    # Initialize limit
    default_limit = 100

    # Check if limit is in params
    if 'limit' in params:
        try: 
            default_limit = int(params['limit'][0])
            if default_limit > 500:
                raise ValueError('Limit must be less than 500')
        except Exception as e:
            raise ValueError(e)
        
        params.pop('limit')
    return default_limit, params