""" Dependencies """
from django.db.models import Q

from wmsAdapterV2.utils.get_data import exec_query_orm
from wmsAdapterV2.utils.get_limit import get_limit
from wmsAdapterV2.utils.filter_by_field import filter_by_field
from wmsAdapterV2.utils.get_fields_filter import get_fields_filter
from wmsAdapterV2.utils.get_sort import get_sort
from wmsAdapterV2.utils.validate_fields import validate_fields
from wmsBase.models.TInsBodega import TInsBodega

def read_cellars(request, db_name):
    # Initialize query
    query = Q()

    # Get the parameters
    params = dict(request.GET)

    try:
        default_limit, params = get_limit(params)
        fields, params = get_fields_filter(params)
        sort, params = get_sort(TInsBodega, params)
        fields = validate_fields(fields, TInsBodega)
        query, params = filter_by_field(TInsBodega, query, params)
    except Exception as e:
        raise ValueError(e)

    
    try:    
        json_query_orm = {
            'db_name': db_name, 
            'model': TInsBodega, 
            'query': query, 
            'fields': fields,
            'default_limit': default_limit, 
            'sort': sort,
        }
        
        articles, query, _ = exec_query_orm(json_query_orm)
        
        return articles, query

    # If there is an error
    except Exception as e:
        raise ValueError(e)