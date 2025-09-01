import json

from wmsAdapter.functions.TdaWmsRelacionSeriales.read import read_relacion_seriales
from wmsAdapter.models import TdaWmsRelacionSeriales


def update_relacion_seriales(request, db_name):

    if(request.body):
        request_data = json.loads(request.body)
    else:
        return 'No data to update'

    if len(request_data) == 0:
        return 'No data to update'

    fields = [field.name for field in TdaWmsRelacionSeriales._meta.get_fields()]


    # Check the fields 
    for r in request_data: 
        if r not in fields: 
            return "Field {} not found in the body".format(r)

    final_fields = {}
    for f in fields:
        if f == "documento":
            if request_data.get(f,None) != None:
                return "The documento field cannot be updated"
        if f == "productoean":
            if request_data.get(f,None) != None:
                return "The productoean field cannot be updated"
        if f == "numserial":
            if request_data.get(f,None) != None:
                return "The numserial field cannot be updated"

        final_fields[f] = request_data.get(f,None)
        if final_fields[f] == None:
            final_fields.pop(f) 
    
    try:    
        seriales = read_relacion_seriales(request, db_name=db_name)
        if type(seriales) == str:
            return seriales
        else:
            if len(list(seriales)) == 1:
                serial = seriales[0]
                # dpk.update(**final_fields)

                for key, value in final_fields.items():
                    setattr(serial, key, value)
                serial.save(using=db_name)
            
                return "Updated successfully"

            elif len(list(seriales)) == 0:
                return "No register found"
            else:
                return "Only one serial can be updated at a time"
    except Exception as e:
        print(e)
        return str(e.__cause__)