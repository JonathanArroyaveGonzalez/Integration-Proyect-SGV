from django.db.models import Q

def get_since_identifier(query, params):
    if 'since_picking' in params:
        try: 
            since_picking = int(params['since_picking'][0])
            query &= Q(picking__gt=since_picking)
        except Exception:
            raise ValueError('Picking must be an integer')

        params.pop('since_picking')
    
    elif 'since_id' in params:
        try:
            since_id = int(params['since_id'][0])
            query &= Q(id__gte=since_id)
        except Exception:
            raise ValueError('Id must be an integer')
        params.pop('since_id')
        
    return query, params
    
        
