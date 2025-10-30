import json
from django.utils import timezone
from wmsAdapterV2.models import TdaWmsClt
from django.http.response import JsonResponse


def create_clt(request, db_name, request_data=None):
    
        if  request_data:
            request_data = dict(request_data)
        else:
    
            if(request.body):
                request_data = json.loads(request.body)
            else:
                return 'No data to create'

        fields = [field.name for field in TdaWmsClt._meta.get_fields()]

        # Make all keys on request_data lowercase
        new_request_data = {}
        for key in request_data.keys():
            new_request_data[key.lower()] = request_data[key]


        # Check the fields 
        for r in new_request_data: 
            if r not in fields: 
                return "Field {} not found".format(r)


        final_fields = {}
        for f in fields:
            if f == "fechaplaneacion":
                final_fields[f] = timezone.now()
            elif f == "fechapedido":
                final_fields[f] = timezone.now()
            else:
                final_fields[f] = new_request_data.get(f,None)

        try:    
            try:
                TdaWmsClt.objects.using(db_name).create(**final_fields)

                return 'created successfully'
            except Exception as e:
                print(e)
                return str(e.__cause__).lower()
        except Exception as e:
            print(e)
            return str(e.__cause__).lower()