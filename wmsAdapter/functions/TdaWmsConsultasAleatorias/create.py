import json
from django.utils import timezone
from wmsAdapter.models import TdaWmsConsultasDinamicas
from django.http.response import JsonResponse
from wmsAdapter.utils.reserved_words import get_reserved_words


def create_consultas_dinamicas(request, db_name, request_data=None):
        
        if  request_data:
            request_data = dict(request_data)
        else:
    
            if(request.body):
                request_data = json.loads(request.body)
            else:
                return 'No data to create'

        fields = [field.name for field in TdaWmsConsultasDinamicas._meta.get_fields()]

        reserved_words = get_reserved_words()

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
            if f != "tdawmsconsultasDinamicas":
                if f == "fecharegistro":
                    final_fields[f] = timezone.now()
                else:
                    if f == "query":
                        query = new_request_data.get(f,None)
                        for r in reserved_words:
                            if str(r).lower() in str(query).lower():
                                raise ValueError(f"The field {f} contains a reserved word: {r}")
                        
                    final_fields[f] = new_request_data.get(f,None)

        try:    
            try:
                TdaWmsConsultasDinamicas.objects.using(db_name).create(**final_fields)
                register = list(TdaWmsConsultasDinamicas.objects.using(db_name).values().filter(codigo=final_fields['codigo']))[0]
                return register
            except Exception as e:
                return str(e)
        except Exception as e:
            return str(e)