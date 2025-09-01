""" Models and functions  """
from wmsAdapter.models.TdaWmsPrv import TdaWmsPrv
from wmsAdapter.functions.TdaWmsPrv.create import create_prv

def create_TdaWmsPrv_from_dynamic_queries(to_create,db_name) -> dict:
    '''
    Function to create articles from dynamic queries
    @params:
        to_create: list of articles to create
        db_name: name of the database
    '''
    try:
        wms_prv = list(TdaWmsPrv.objects.using(db_name).all().values_list('item', flat=True))
    except Exception as e:
        wms_prv = []
    
    try:
        prv_to_create = []        

        for prv in to_create:
            if str(prv['item']) not in wms_prv:
                prv_to_create.append(prv)

        print('products_to_create')
        print(len(prv_to_create))

        prv_created = []
        prv_with_error = []
        if len(prv_to_create) > 0:
            for prv in prv_to_create:
                try:
                    response = create_prv(None, db_name, request_data= prv)
                    if response == 'created successfully':
                        prv_created.append(prv['item'])
                    else:
                        print(response)
                        prv_with_error.append(prv['item'])
                        print('Error creating prv %s' % prv['item'])

                except Exception as e:
                    print(e)
                    prv_with_error.append(prv['item'])
                    print('Error creating prv %s' % prv['item'])
                    continue
        else:
            print('No Prv to create')
            return {"message" : "No prv to create"}
        
        return {
            'Prv_created': prv_created,
            'Prv_with_error': prv_with_error
        }
    except Exception as e:
        return {"message" : "Error creating item"}