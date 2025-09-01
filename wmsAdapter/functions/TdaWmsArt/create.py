""" Dependencies """
import json
from django.utils import timezone
from django.http.response import JsonResponse

""" Models and functions """
from wmsAdapter.models import TdaWmsArt

def create_articles(request, db_name, request_data=None):
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

        fields = [field.name for field in TdaWmsArt._meta.get_fields()]
        
        # Check the fields 
        for r in request_data: 
            if r not in fields: 
                return "Field {} not found".format(r)

        # Get the final fields
        final_fields = {}
        for f in fields:
            if f == "fecharegistro":
                final_fields[f] = timezone.now()

            elif f == "referencia":
                referencia = request_data.get(f,None)
                final_fields[f] = referencia
                if referencia == None:
                    return "Field {} is required".format(f)

            elif f == "nuevoean":
                nuevoean = request_data.get(f,None)
                final_fields[f] = nuevoean
                if nuevoean == None:
                    return "Field {} is required".format(f)
                else:
                    final_fields[f] = request_data.get(f,None)

            elif f == "id":
                continue

            else:
                final_fields[f] = request_data.get(f, None)

        try:  
            product = list(TdaWmsArt.objects.using(db_name).filter(productoean=final_fields['productoean']))
            
            if len(product) >= 1:
                return 'The product with productoean %s already exists' % final_fields['productoean']
            else:
                try:
                    
                    TdaWmsArt.objects.using(db_name).create(**final_fields) #kwargs
                    return 'created successfully'
                except Exception as e:
                    return str(e.__cause__).lower()
        except Exception as e:
            return str(e.__cause__).lower()