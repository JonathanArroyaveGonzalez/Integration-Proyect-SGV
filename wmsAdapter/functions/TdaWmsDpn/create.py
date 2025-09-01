import json
from django.utils import timezone
from wmsAdapter.models import TdaWmsDpn
from django.http.response import JsonResponse
from django.db.models import Max


def create_dpn(request, db_name, request_data=None):
    
        if  request_data:
            request_data = dict(request_data)
        else:
    
            if(request.body):
                request_data = json.loads(request.body)
            else:
                return 'No data to create'
            return 'No data to create'

        fields = [field.name for field in TdaWmsDpn._meta.get_fields()]

        # Check the fields 
        for r in request_data: 
            if r not in fields: 
                return "Field {} not found".format(r)

        final_fields = {}
        for f in fields:
            if f == "fecharegistro":
                final_fields[f] = timezone.now()

            elif f == "tipodocto":
                tipodocto = request_data.get(f,None)
                final_fields[f] = tipodocto
                if tipodocto == None:
                    return "Field {} is required".format(f)

            elif f == "doctoerp":
                doctoerp = request_data.get(f,None)
                final_fields[f] = doctoerp
                if doctoerp == None:
                    return "Field {} is required".format(f)

            elif f == "lineaidop":
                maxl = TdaWmsDpn.objects.using(db_name).aggregate(Max('lineaidop'))
                # print(maxl)
                final_fields[f] = int(maxl["lineaidop__max"]) + 1
            else:
                final_fields[f] = request_data.get(f,None)

        try:    
            try:
                TdaWmsDpn.objects.using(db_name).create(**final_fields)

                return 'created successfully'
            except Exception as e:
                print(e)
                return str(e.__cause__).lower()
        except Exception as e:
            print(e)
            return str(e.__cause__).lower()