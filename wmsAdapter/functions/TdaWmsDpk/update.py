import json
from wmsAdapter.functions.TdaWmsDpk.read import read_dpk

from wmsAdapter.models import TdaWmsDpk

def update_dpk(request, db_name):

    if(request.body):
        request_data = json.loads(request.body)
    else:
        return 'No data to update'

    if len(request_data) == 0:
        return 'No data to update'

    fields = [field.name for field in TdaWmsDpk._meta.get_fields()]


    # Check the fields 
    for r in request_data: 
        if r not in fields: 
            return "Field {} not found in the body".format(r)

    final_fields = {}
    for f in fields:
        if f == "picking":
            if request_data.get(f,None) != None:
                return "The picking field cannot be updated"
        if f == "lineaidpicking":
            if request_data.get(f,None) != None:
                return "The lineaidpicking field cannot be updated"
        if f == "doctoerp":
            if request_data.get(f,None) != None:
                return "The doctoerp field cannot be updated"
        if f == "tipodocto":
            if request_data.get(f,None) != None:
                return "The tipodocto field cannot be updated"
        final_fields[f] = request_data.get(f,None)
        if final_fields[f] == None:
            final_fields.pop(f) 
    
    try:    
        dpk = read_dpk(request, db_name=db_name)
        if type(dpk) == str:
            return dpk
        else:
            if len(list(dpk)) == 1:
                dpk = dpk[0]
                # dpk.update(**final_fields)

                for key, value in final_fields.items():
                    setattr(dpk, key, value)
                dpk.save(using=db_name)
            
                return "Updated successfully"

            elif len(list(dpk)) == 0:
                return "No register found"
            else:
                return "Only one product can be updated at a time"
    except Exception as e:
        print(e)
        return str(e.__cause__)