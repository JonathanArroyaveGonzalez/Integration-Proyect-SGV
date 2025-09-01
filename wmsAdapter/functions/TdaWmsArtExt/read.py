""" Dependencies """
from django.db.models import Q

""" Models and functions """
from wmsAdapter.models import TdaWmsArtExt

def read_articles_extended(request, db_name):

        '''
            This function get the articles extended from the database
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

        if 'since_id' in params:
            try:
                since_id = int(params['since_id'][0])
                query &= Q(id__gte=since_id)
            except Exception as e:
                raise ValueError('Since_id must be an integer')
            del params['since_id']

        if 'limit' in params:
            try: 
                default_limit = int(params['limit'][0])
                if default_limit > 500:
                    raise ValueError('Limit must be less than 500')
            except Exception as e:
                 raise ValueError('Limit must be an integer')
            del params['limit']

        fields = [field.name for field in TdaWmsArtExt._meta.get_fields()]

        # Check the fields 
        for p in params: 
            if p not in fields: 
                return "Field {} not found".format(p)

        # Get the final fields
        final_fields = {}
        for f in fields:
                final_fields[f] = request.GET.get(f,'')

        for key, value in final_fields.items():
            if value != '':
                query &= Q(**{key: value})

        try:    

            response = TdaWmsArtExt.objects.using(db_name).filter(query).order_by('id')[:default_limit]
            return response

        except Exception as e:
            print(e)
            return None