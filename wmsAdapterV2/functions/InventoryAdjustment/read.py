from django.db.models import Q


from wmsAdapterV2.models.TdaWmsCecoMrm import TdaWmsCecoMrm
from wmsAdapterV2.utils.filter_by_field import filter_by_field
from wmsAdapterV2.utils.get_data import exec_query_orm
from wmsAdapterV2.utils.get_date_range import get_date_range
from wmsAdapterV2.utils.get_fields_filter import get_fields_filter
from wmsAdapterV2.utils.get_limit import get_limit
from wmsAdapterV2.utils.get_since_identifier import get_since_identifier
from wmsAdapterV2.utils.get_sort import get_sort
from wmsAdapterV2.utils.validate_fields import validate_fields

def read_inventory_adjustment(request, db_name):

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
        query, params = get_since_identifier(query, params)
        fields, params = get_fields_filter(params)
        sort, params = get_sort(TdaWmsCecoMrm, params)
        fields = validate_fields(fields, TdaWmsCecoMrm)
        query, params = filter_by_field(TdaWmsCecoMrm, query, params)
        query, params = get_date_range(query, Q(), params, 'fecha_contabilizacion')
        print(query)
    except Exception as e:
        raise ValueError(e)

    try:    
        json_query_orm = {
                'db_name': db_name, 
                'model': TdaWmsCecoMrm, 
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
    