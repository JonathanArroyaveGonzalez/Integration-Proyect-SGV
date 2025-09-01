import json
from wmsAdapter.functions.TdaWmsArt.read import read_articles

from wmsAdapter.models import TdaWmsArt

def update_articles(request, db_name, request_data=None):

    if request_data == None:
        if(request.body):
            request_data = json.loads(request.body)
        else:
            return 'No data to update'
    
    if len(request_data) == 0:
        return 'No data to update'

    fields = [field.name for field in TdaWmsArt._meta.get_fields()]

    # Check the fields 
    for r in request_data: 
        if r not in fields: 
            return "Field {} not found in the body".format(r)

    final_fields = {}
    for f in fields:
        if f != "tdawmsduk" and f != "tdawmsdpk":
            if f == "productoean":
                if request_data.get(f,None) != None:
                    return "The productoean field cannot be updated"
            final_fields[f] = request_data.get(f,None)
            if final_fields[f] == None:
                final_fields.pop(f)

    try:   
        product = read_articles(request, db_name=db_name)
        if type(product) == str:
            return product
        else:
            if len(list(product)) == 1:
                product = product[0]
                for key, value in final_fields.items():
                    setattr(product, key, value)
                product.save(using=db_name)
            
                return "Updated successfully"

            elif len(list(product)) == 0:
                return "No product found"
            else:
                return "Only one product can be updated at a time"
    except Exception as e:
        print(e)
        return str(e.__cause__)