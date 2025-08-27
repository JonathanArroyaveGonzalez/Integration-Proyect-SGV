""" Dependencies """
from django.db.models import Q

from wmsAdapterV2.models import TdaWmsDpk, TdaWmsEpk
from wmsAdapterV2.utils.filter_by_field import filter_by_field
from wmsAdapterV2.utils.get_data import exec_query_orm
from wmsAdapterV2.utils.get_date_range import get_date_range
from wmsAdapterV2.utils.get_fields_filter import get_fields_filter
from wmsAdapterV2.utils.get_include_filter import get_include_filter
from wmsAdapterV2.utils.get_limit import get_limit
from wmsAdapterV2.utils.get_since_identifier import get_since_identifier
from wmsAdapterV2.utils.get_sort import get_sort
from wmsAdapterV2.utils.search_params_in_body import search_params_in_body
from wmsAdapterV2.utils.validate_fields import validate_fields
from wmsAdapterV2.utils.validate_fields_model_and_detail import validate_field_model_and_detail

""" Models and functions """


def read_sale_orders(request, db_name):

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
            
            params = search_params_in_body(request, params)
            default_limit, params = get_limit(params)
            query, params = get_since_identifier(query, params)
            fields, params = get_fields_filter(params)
            sort, params = get_sort(TdaWmsEpk, params)
            fields = validate_fields(fields, TdaWmsEpk)
            include, params = get_include_filter(TdaWmsDpk, params)
            query, params = filter_by_field(TdaWmsEpk, query, params)
            query_detail, params = validate_field_model_and_detail(query, params)
            query_detail, params = filter_by_field(TdaWmsDpk, query_detail, params)
            query, params = get_date_range(query, query_detail, params)

        except Exception as e:
            raise ValueError(e)
        
        try:    
            # Get the response
            json_query_orm = {
                'db_name': db_name, 
                'model': TdaWmsEpk, 
                'model_detail': TdaWmsDpk, 
                'query': query, 
                'query_detail': query_detail,
                'fields': fields,
                'include': include,
                'default_limit': default_limit, 
                'sort': sort,
                'field_join': 'picking'
            }

            orders, query, query_detail = exec_query_orm(json_query_orm)

            return orders, query, query_detail

        # If there is an error
        except Exception as e:
            raise ValueError(e)