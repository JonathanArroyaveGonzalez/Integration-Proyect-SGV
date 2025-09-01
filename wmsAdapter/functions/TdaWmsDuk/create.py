import json
from django.utils import timezone
from wmsAdapter.models import TdaWmsDuk
from django.http.response import JsonResponse


def create_duk(request, db_name, request_data=None):
    
        if  request_data:
            request_data = dict(request_data)
        else:
            if(request.body):
                request_data = json.loads(request.body)
            else:
                return 'No data to create'

        fields = [field.name for field in TdaWmsDuk._meta.get_fields()]

        new_request_data = {}
        for key in request_data.keys():
            new_request_data[key.lower()] = request_data[key]

        #print(new_request_data)

        # Check the fields 
        for r in new_request_data: 
            if r not in fields: 
                return "Field {} not found".format(r)

        final_fields = {}
        for f in fields:
            if f == "fecharegistro":
                final_fields[f] = timezone.now()
            elif f == "eta":
                final_fields[f] = timezone.now()
            elif f == "f_ultima_actualizacion":
                final_fields[f] = timezone.now()
            elif f == "fechaestadoalmdirigido":
                final_fields[f] = timezone.now()
            else:
                final_fields[f] = new_request_data.get(f,None)

        try:    
            try:
                TdaWmsDuk.objects.using(db_name).create(**final_fields)

                return 'created successfully'
            except Exception as e:
                print(e)
                return str(e.__cause__).lower()
        except Exception as e:
            print(e)
            return str(e.__cause__).lower()