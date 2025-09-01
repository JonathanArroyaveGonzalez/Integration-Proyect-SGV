import json
from django.utils import timezone
from wmsAdapter.models import TdaWmsEuk
from django.http.response import JsonResponse


def create_euk(request, db_name, request_data=None):

        if  request_data:
            request_data = dict(request_data)
        else:
            if(request.body):
                request_data = json.loads(request.body)
            else:
                return 'No data to create'
            
        fields = [field.name for field in TdaWmsEuk._meta.get_fields()]

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
            if f != "tdawmsduk":

                # Date fields
                if f == "fecharegistro":
                    final_fields[f] = timezone.now()
                elif f == "fecha":
                    final_fields[f] = timezone.now()
                elif f == "f_ultima_actualizacion":
                    final_fields[f] = timezone.now()

                # required fields    
                elif f == "numdocumento":
                    numdocumento = new_request_data.get(f,None)
                    final_fields[f] = numdocumento
                    if numdocumento == None:
                        return "Field {} is required".format(f)

                elif f == "tipodocto":
                    tipodocto = new_request_data.get(f,None)
                    final_fields[f] = tipodocto
                    if tipodocto == None:
                        return "Field {} is required".format(f)

                elif f == "doctoerp":
                    doctoerp = new_request_data.get(f,None)
                    final_fields[f] = doctoerp
                    if doctoerp == None:
                        return "Field {} is required".format(f)

                elif f == "item":
                    item = new_request_data.get(f,None)
                    final_fields[f] = item
                    if doctoerp == None: # type: ignore
                        return "Field {} is required".format(f)

                else:
                    final_fields[f] = new_request_data.get(f,None)

        try:    
            try:
                TdaWmsEuk.objects.using(db_name).create(**final_fields)

                return 'created successfully'
            except Exception as e:
                print(e)
                return str(e.__cause__).lower()
        except Exception as e:
            print(e)
            return str(e.__cause__).lower()