from django.db.models import Q

from wmsAdapter.models import TdaWmsConsultasDinamicas

def read_consultas_dinamicas(request, db_name):

        params = dict(request.GET)

        fields = [field.name for field in TdaWmsConsultasDinamicas._meta.get_fields()]

        print(fields)

        # Check the fields 
        for p in params: 
            if p not in fields: 
                return "Field {} not found".format(p)

        final_fields = {}
        for f in fields:
            if  f != "tdawmsconsultasDinamicas":  #Foreign keys
                final_fields[f] = request.GET.get(f,'')


        query = Q()
        for key, value in final_fields.items():
            if value != '':
                query &= Q(**{key: value})
        
        # print(query)
        
        try:    

            response = TdaWmsConsultasDinamicas.objects.using(db_name).filter(query).order_by('-id')[:500]
            return  response
        except Exception as e:
            raise ValueError(str(e))