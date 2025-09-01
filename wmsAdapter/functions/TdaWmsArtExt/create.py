""" Dependencies """
import json
from django.utils import timezone
from django.http.response import JsonResponse

""" Models and functions """
from wmsAdapter.models import TdaWmsArtExt

def create_articles_extended(request, db_name, request_data=None):
        ''' 
            This function create a new article in the database
            @params:
                request: request object
                db_name: name of the database
                request_data: data to create the article
        '''

        # Check if request_data is previously defined
        if(request_data):
            # Convert request_data to dict
            request_data = dict(request_data)

        elif(request.body):
            # Convert request.body to dict
            request_data = json.loads(request.body)
        else:
            raise ValueError('No data to create')

        fields = [field.name for field in TdaWmsArtExt._meta.get_fields()]

        # Check the fields 
        for r in request_data: 
            if r not in fields: 
                return "Field {} not found".format(r)

        # Get the final fields
        final_fields = {}
        for f in fields:
            if f == "id":
                continue
            else:
                final_fields[f] = request_data.get(f, None)

        try:  
            product = TdaWmsArtExt.objects.using(db_name).filter(productoean=final_fields['productoean'])
            if len(list(product)) >= 1:
                return 'The product with productoean %s already exists' % final_fields['productoean']
            else:
                try:
                    print(final_fields)
                    TdaWmsArtExt.objects.using(db_name).create(**final_fields) #kwargs

                    return 'created successfully'
                except Exception as e:
                    print(e)
                    return str(e.__cause__).lower()
        except Exception as e:
            print(e)
            return str(e.__cause__).lower()