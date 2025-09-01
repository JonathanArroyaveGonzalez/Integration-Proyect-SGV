""" Dependencies """
import json

""" Functions and Models """
from wmsAdapter.models import TdaWmsConsultasDinamicas
from wmsAdapter.functions.TdaWmsConsultasAleatorias.read import read_consultas_dinamicas


def update_consultas_dinamicas(request, db_name):
    ''' 
    Function to update a register in the table TdaWmsConsultasDinamicas
    params: 
        request: request object
        db_name: database name
    '''

    if(request.body):
        request_data = json.loads(request.body)
    else:
        return 'No data to update'

    if len(request_data) == 0:
        return 'No data to update'

    fields = [field.name for field in TdaWmsConsultasDinamicas._meta.get_fields()]


    # Check the fields 
    for r in request_data: 
        if r not in fields: 
            return "Field {} not found in the body".format(r)

    final_fields = {}
    for f in fields:
 
        final_fields[f] = request_data.get(f,None)
        if final_fields[f] == None:
            final_fields.pop(f) 
    
    try:    
        register = read_consultas_dinamicas(request, db_name=db_name)
        if len(list(register)) == 1:
                        register = register[0]
                        for key, value in final_fields.items():
                            setattr(register, key, value)
                        register.save(using=db_name)  # type: ignore
                    
                        return "Updated successfully"

        elif len(list(register)) == 0:
            return "No register found"
        else:
            return "Only one product can be updated at a time"
    except Exception as e:
        return str(e)
            