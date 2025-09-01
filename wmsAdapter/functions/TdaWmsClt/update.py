import json
from wmsAdapter.functions.TdaWmsClt.read import read_clt

from wmsAdapter.models import TdaWmsClt

def update_clt(request, db_name):

    if(request.body):
        request_data = json.loads(request.body)
    else:
        return 'No data to update'

    if len(request_data) == 0:
        return 'No data to update'

    fields = [field.name for field in TdaWmsClt._meta.get_fields()]


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
        clt = read_clt(request, db_name=db_name)
        if type(clt) == str:
            return clt
        else:
            if len(list(clt)) == 1:
                clt = clt[0]
                for key, value in final_fields.items():
                    setattr(clt, key, value)
                clt.save(using=db_name)
            
                return "Updated successfully"

            elif len(list(clt)) == 0:
                return "No register found"
            else:
                return "Only one product can be updated at a time"
    except Exception as e:
        print(e)
        return str(e.__cause__)