""" Dependencies """
from django.db.models import Q
from datetime import datetime, timedelta

from wmsAdapterV2.utils.filter_by_field import filter_by_field
from wmsAdapterV2.utils.get_data import exec_query_orm
from wmsAdapterV2.utils.get_date_range import get_date_range
from wmsAdapterV2.utils.get_fields_filter import get_fields_filter
from wmsAdapterV2.utils.get_limit import get_limit
from wmsAdapterV2.utils.get_since_identifier import get_since_identifier
from wmsAdapterV2.utils.get_sort import get_sort
from wmsAdapterV2.utils.validate_fields import validate_fields

""" Models and functions """
from wmsAdapterV2.models import TdaWmsArt

def read_articles(request, db_name):

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
            sort, params = get_sort(TdaWmsArt, params)
            fields = validate_fields(fields, TdaWmsArt)
            query, params = filter_by_field(TdaWmsArt, query, params)
            query, params = get_date_range(query, Q(), params)
        except Exception as e:
            raise ValueError(e)


        try:
            json_query_orm = {
                'db_name': db_name, 
                'model': TdaWmsArt, 
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
        


def read_articles_obj(request, db_name):

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

        # Initialize limit
        default_limit = 50

        # Initialize ids
        ids = []

        # Check if limit is in params
        if 'ids' in params:
            ids = str(params['ids']).replace('[','').replace(']','').replace("'","").split(',')
            if len(ids) > 0:
                query &= Q(id__in=ids)
            del params['ids']

        if 'start_date' in params:
            start_date = params['start_date'][0] 
            params.pop('start_date')
        else:
            start_date = '2000-01-01'

        if 'end_date' in params:
            current_date = datetime.strptime(params['end_date'][0], '%Y-%m-%d')
            current_date = current_date + timedelta(days=1)
            end_date = current_date.strftime('%Y-%m-%d')
            params.pop('end_date')
        else:
            current_date = datetime.today().strftime('%Y-%m-%d')
            current_date = datetime.strptime(current_date, '%Y-%m-%d')
            current_date = current_date + timedelta(days=1)
            end_date = current_date.strftime('%Y-%m-%d')

        # Check if since_id is in params	
        if 'since_id' in params:
            try:
                since_id = int(params['since_id'][0])
                query &= Q(id__gte=since_id)
            except Exception as e:
                raise ValueError('Since_id must be an integer')
            del params['since_id']

        # Check if limit is in params
        if 'limit' in params:
            try: 
                default_limit = int(params['limit'][0])
                if default_limit > 500:
                    raise ValueError('Limit must be less than 500')
            except Exception as e:
                 raise ValueError('Limit must be an integer')
            del params['limit']

        # Get the fields
        fields = [field.name for field in TdaWmsArt._meta.get_fields()]

        # Check the fields 
        for p in params: 
            if p not in fields: 
                return "Field {} not found".format(p)

        # Get the final fields
        final_fields = {}
        for f in fields:
                final_fields[f] = request.GET.get(f,'')

        # Check if the fields are empty
        for key, value in final_fields.items():
            if value != '':
                query &= Q(**{key: value})

        try:    
            # Get the response
            response = TdaWmsArt.objects.using(db_name).filter(query, fecharegistro__range=[start_date, end_date]).order_by('id')[:default_limit]
            return response

        # If there is an error
        except Exception as e:
            raise ValueError(e)