from django.db.models import Q

from wmsAdapter.models import TdaWmsEuk

def read_euk(request, db_name):

        params = dict(request.GET)

        fields = [field.name for field in TdaWmsEuk._meta.get_fields()]

        # Check the fields 
        for p in params: 
            if p not in fields: 
                return "Field {} not found".format(p)

        final_fields = {}
        for f in fields:
            if  f != "tdawmsdpk":  #Foreign keys
                final_fields[f] = request.GET.get(f,'')

        # print(fields)
        # print(final_fields)

        query = Q()
        for key, value in final_fields.items():
            if value != '':
                query &= Q(**{key: value})
        
        # print(query)
        
        try:    

            response = TdaWmsEuk.objects.using(db_name).filter(query).order_by('-fecharegistro')[:500]
            return response

        except Exception as e:
            print(e)
            return None