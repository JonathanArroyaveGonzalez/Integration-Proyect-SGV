from django.db.models import Q


from wmsAdapterV2.models import TdaWmsPrv
from wmsAdapterV2.utils.filter_by_field import filter_by_field
from wmsAdapterV2.utils.get_data import exec_query_orm
from wmsAdapterV2.utils.get_date_range import get_date_range
from wmsAdapterV2.utils.get_fields_filter import get_fields_filter
from wmsAdapterV2.utils.get_limit import get_limit
from wmsAdapterV2.utils.get_sort import get_sort
from wmsAdapterV2.utils.validate_fields import validate_fields

def read_prv(request, db_name):

    '''
        This function get the articles from the database
        @params:
            request: request object
            db_name: name of the database
    '''
    
    # Initialize query
    query = Q()

    # Get the parameters
    params = dict(request.GET)

    try:
        default_limit, params = get_limit(params)
        fields, params = get_fields_filter(params)
        sort, params = get_sort(TdaWmsPrv, params)
        fields = validate_fields(fields, TdaWmsPrv)
        query, params = filter_by_field(TdaWmsPrv, query, params)
        query, params = get_date_range(query, Q(), params)
    except Exception as e:
        raise ValueError(e)

    try:    
        json_query_orm = {
                'db_name': db_name, 
                'model': TdaWmsPrv, 
                'query': query, 
                'fields': fields,
                'default_limit': default_limit, 
                'sort': sort,
            }
            
        suppliers, query, _ = exec_query_orm(json_query_orm)
            
        return suppliers, query

    # If there is an error
    except Exception as e:
        raise ValueError(e)
    