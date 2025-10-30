from wmsAdapterV2.utils.get_include_filter import parse_include_param
from wmsAdapterV2.utils.validate_fields import validate_fields


def get_sort(model, params):
    sort = None
    
    if 'sort_by' in params:
        try: 
            model_fields = [field.name for field in model._meta.get_fields()]
            key, values = parse_include_param(params['sort_by'][0])
            
            if key in model_fields:
                if values == 'desc':
                    sort = '-' + key
                else:
                    sort = key
            
        except Exception as e:
            raise ValueError(e)

        params.pop('sort_by')
    
    return sort, params
    
    
