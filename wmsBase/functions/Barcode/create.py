""" Dependencies """
import json
from django.utils import timezone

""" Models and functions """
from wmsBase.models.TRelacionCodbarras import TRelacionCodbarras

def create_t_relacion_codbarras(request, db_name, request_data=None):
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

        fields = [field.name for field in TRelacionCodbarras._meta.get_fields()]

        # Check the fields 
        for r in request_data: 
            if r not in fields: 
                raise ValueError("Field {} not found".format(r))

        # Get the final fields
        final_fields = {}

        # Iterate over the fields
        for f in fields:

         # Check if the field is in the request_data. This is for required fields
            # if fechacrea is in request_data
            if f == "fechacrea":
                final_fields[f] = timezone.now()

            # if codbarrasasignado is in request_data
            elif f == "codbarrasasignado":
                codbarrasasignado = request_data.get(f, None)
                final_fields[f] = codbarrasasignado
                if codbarrasasignado == None:
                    raise ValueError(response_required(f))
                else:
                    final_fields[f] = request_data.get(f, None)
            
            # if idinternoean is in request_data
            elif f == "idinternoean":
                idinternoean = request_data.get(f, None)
                final_fields[f] = idinternoean
                if idinternoean == None:
                    raise ValueError(response_required(f))
                else:
                    final_fields[f] = request_data.get(f, None)

            # if cantidad is in request_data
            elif f == "cantidad":
                cantidad = request_data.get(f, None)
                final_fields[f] = cantidad
                if cantidad == None:
                    raise ValueError(response_required(f))
                else:
                    final_fields[f] = request_data.get(f, None)
            
            else:
                final_fields[f] = request_data.get(f, None)

        try:  

            # get t_relacion_codbarras
            product = TRelacionCodbarras.objects.using(db_name).filter(codbarrasasignado=final_fields['codbarrasasignado'], idinternoean=final_fields['idinternoean'])

            # Check if the register exists
            if len(list(product)) >= 1:
                raise ValueError('The register with codbarrasasignado %s already exists' % final_fields['codbarrasasignado'])
            
            # Create the register
            else:
                try:
                    TRelacionCodbarras.objects.using(db_name).create(**final_fields) #kwargs

                    # Get the register
                    register = list(TRelacionCodbarras.objects.using(db_name).values().filter(codbarrasasignado=final_fields['codbarrasasignado'], idinternoean=final_fields['idinternoean']))[0]

                    # Return the product
                    return register

                except Exception as e:
                    raise ValueError(e)
        except Exception as e:
            raise ValueError(e)
        
def response_required(field:str) -> str:
    '''
        This function returns a message if the field is required
        @params:
            field: field to check
        @return:
            message: message to return
    '''
    return "Field {} is required".format(field)