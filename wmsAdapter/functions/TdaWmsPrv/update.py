import json
from wmsAdapter.functions.TdaWmsPrv.read import read_prv

from wmsAdapter.models import TdaWmsPrv

def update_prv(request, db_name):

    if(request.body):
        request_data = json.loads(request.body)
    else:
        return 'No data to update'

    if len(request_data) == 0:
        return 'No data to update'

    fields = [field.name for field in TdaWmsPrv._meta.get_fields()]


    # Check the fields 
    for r in request_data: 
        if r not in fields: 
            return "Field {} not found in the body".format(r)

    final_fields = {}
    for f in fields:
        if f == "item":
            if request_data.get(f,None) != None:
                return "The item field cannot be updated"
                
        final_fields[f] = request_data.get(f,None)
        if final_fields[f] == None:
            final_fields.pop(f) 
    
    try:    
        prv = read_prv(request, db_name=db_name)
        if type(prv) == str:
            return prv
        else:
            if len(list(prv)) == 1:
                prv = prv[0]
                for key, value in final_fields.items():
                    setattr(prv, key, value)
                prv.save(using=db_name)
            
                return "Updated successfully"

            elif len(list(prv)) == 0:
                return "No register found"
            else:
                return "Only one product can be updated at a time"
    except Exception as e:
        print(e)
        return str(e.__cause__)