""" Models and functions  """
from wmsAdapter.models.TdaWmsClt import TdaWmsClt
from wmsAdapter.functions.TdaWmsClt.create import create_clt

def create_TdaWmsClt_from_dynamic_queries(to_create,db_name) -> dict:
    '''
    Function to create articles from dynamic queries
    @params:
        to_create: list of articles to create
        db_name: name of the database
    '''
    try:
        wms_clt = list(TdaWmsClt.objects.using(db_name).all().values_list('item', flat=True))
    except Exception as e:
        wms_clt = []
    
    try:
        clt_to_create = []        

        for clt in to_create:
            if str(clt['item']) not in wms_clt:
                clt_to_create.append(clt)

        print('products_to_create')
        print(len(clt_to_create))

        clt_created = []
        clt_with_error = []
        if len(clt_to_create) > 0:
            for clt in clt_to_create:
                try:
                    # breakpoint()
                    response = create_clt(None, db_name, request_data= clt)
                    if response == 'created successfully':
                        clt_created.append(clt['item'])
                    
                    else:
                        print(response)
                        clt_with_error.append(clt['item'])
                        print('Error creating product %s' % clt['item'])

                except Exception as e:
                    print(e)
                    clt_with_error.append(clt['item'])
                    print('Error creating clt %s' % clt['item'])
                    continue
        else:
            print('No clt to create')
            return {"message" : "No clt to create"}
        
        return {
            'clt_created': clt_created,
            'clt_with_error': clt_with_error
        }
    except Exception as e:
        print(e)
        return {"message" : "Error creating item"}