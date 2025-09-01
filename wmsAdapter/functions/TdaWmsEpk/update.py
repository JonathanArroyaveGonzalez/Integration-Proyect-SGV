import json
from wmsAdapter.functions.TdaWmsEpk.read import read_epk

from wmsAdapter.models import TdaWmsEpk

def update_epk(request, db_name):

    if(request.body):
        request_data = json.loads(request.body)
    else:
        return 'No data to update'

    if len(request_data) == 0:
        return 'No data to update'

    fields = [field.name for field in TdaWmsEpk._meta.get_fields()]

    # Check the fields 
    for r in request_data: 
        if r not in fields: 
            return "Field {} not found in the body".format(r)

    final_fields = {}
    for f in fields:
        if  f != "tdawmsdpk":
            if f == "picking":
                if request_data.get(f,None) != None:
                    return "The picking field cannot be updated"
            final_fields[f] = request_data.get(f,None)
            if final_fields[f] == None:
                final_fields.pop(f) 

    try:    
        epk = read_epk(request, db_name=db_name)
        if type(epk) == str:
            return epk
        else:
            if len(list(epk)) == 1:
                epk = epk[0]
                for key, value in final_fields.items():
                    setattr(epk, key, value)
                epk.save(using=db_name)
            
                return "Updated successfully"

            elif len(list(epk)) == 0:
                return "No register found"
            else:
                return "Only one product can be updated at a time"
    except Exception as e:
        print(e)
        return str(e.__cause__)