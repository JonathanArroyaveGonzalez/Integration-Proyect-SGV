""" Models and functions  """
from wmsAdapter.models.TdaWmsEpk import TdaWmsEpk
from wmsAdapter.functions.TdaWmsEpk.create import create_epk

def create_TdaWmsEpk_from_dynamic_queries(to_create,db_name) -> dict:
    '''
    Function to create articles from dynamic queries
    @params:
        to_create: list of articles to create
        db_name: name of the database
    '''

    unique_key = []

    try:
        wms_epk =  list(TdaWmsEpk.objects.using(db_name).all().order_by('-picking')[:8000])
        for e in wms_epk:
            unique_key.append(str(e.tipodocto) + str(e.doctoerp) + str(e.numpedido))

    except Exception as e:
        wms_epk = []
    
    try:
        epk_to_create = []        

        for epk in to_create:
            if str(str(epk['tipodocto'])  + str(epk['doctoerp']) + str(epk['numpedido'])) not in unique_key:
                epk_to_create.append(epk)

        print('products_to_create')
        print(len(epk_to_create))

        epk_created = []
        epk_with_error = []
        if len(epk_to_create) > 0:
            for epk in epk_to_create:
                try:
                    response = create_epk(None, db_name, request_data= epk)
                    if response == 'created successfully':
                        epk_created.append(str(str(epk['tipodocto']) + ' ' + str(epk['doctoerp']) + ' ' +str(epk['numpedido'])))
                    else:
                        print(response)
                        epk_with_error.append(str(str(epk['tipodocto']) + ' ' + str(epk['doctoerp']) + ' ' +str(epk['numpedido'])))
                        print('Error creating epk %s' % str(str(epk['tipodocto']) + ' ' + str(epk['doctoerp']) + ' ' +str(epk['numpedido'])))

                except Exception as e:
                    print(e)
                    epk_with_error.append(str(str(epk['tipodocto']) + ' ' + str(epk['doctoerp']) + ' ' +str(epk['numpedido'])))
                    print('Error creating epk %s' % str(str(epk['tipodocto']) + ' ' + str(epk['doctoerp']) + ' ' +str(epk['numpedido'])))
                    continue
        else:
            print('No Epk to create')
            return {"message" : "No epk to create"}
        
        return {
            'Epk_created': epk_created,
            'Epk_with_error': epk_with_error
        }
    except Exception as e:
        return {"message" : "Error creating item"}