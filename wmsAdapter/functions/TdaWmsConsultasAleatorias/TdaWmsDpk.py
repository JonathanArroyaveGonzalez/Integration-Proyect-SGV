""" Models and functions  """
from wmsAdapter.models.TdaWmsDpk import TdaWmsDpk
from wmsAdapter.functions.TdaWmsDpk.create import create_dpk
from wmsAdapter.models.TdaWmsEpk import TdaWmsEpk

def create_TdaWmsDpk_from_dynamic_queries(to_create,db_name) -> dict:
    '''
    Function to create articles from dynamic queries
    @params:
        to_create: list of articles to create
        db_name: name of the database
    '''

    unique_key = []

    try:
        wms_dpk = list(TdaWmsDpk.objects.using(db_name).distinct().filter(estadodetransferencia=0).values('tipodocto', 'doctoerp', 'numpedido', 'productoean', 'lineaidpicking', 'estadodetransferencia').order_by('-id')[:8000])
        for e in wms_dpk:
            unique_key.append(str(e['tipodocto']) + str(e['doctoerp']) + str(e['numpedido']) + str(e['productoean']) + str(e['lineaidpicking'])  + str(e['estadodetransferencia']))

    except Exception as e:
        wms_dpk = []
    
    try:
        dpk_to_create = []        

        for p in to_create:
            if str(str(p['tipodocto'])
                + str(p['doctoerp'])
                + str(p['numpedido'])
                + str(p['productoean'])
                + str(p['lineaidpicking'])
                + str(p['estadodetransferencia'])) not in unique_key:

                dpk_to_create.append(p)

        print('dpk_to_create')
        print(len(dpk_to_create))

        dpk_created = []
        dpk_with_error = []
        if len(dpk_to_create) > 0:
            for dpk in dpk_to_create:
                try:
                    print(dpk)

                    dpk['picking'] = TdaWmsEpk.objects.using(db_name).filter(tipodocto=dpk['tipodocto'],
                                                                       doctoerp=dpk['doctoerp'],
                                                                       numpedido=dpk['numpedido'])[0].picking

                    
                    print(dpk)
                    response = create_dpk(None, db_name, request_data= dpk)
                    if response == 'created successfully':
                        dpk_created.append(str(str(dpk['tipodocto']) + ' ' + str(dpk['doctoerp']) + ' ' +str(dpk['numpedido']) + ' ' + str(dpk['productoean'])))
                    else:
                        print(response)
                        dpk_with_error.append(str(str(dpk['tipodocto']) + ' ' + str(dpk['doctoerp']) + ' ' +str(dpk['numpedido']) + ' ' + str(dpk['productoean'])))
                        print('Error creating dpk %s' % str(str(dpk['tipodocto']) + ' ' + str(dpk['doctoerp']) + ' ' +str(dpk['numpedido']) + ' ' + str(dpk['productoean'])))

                except Exception as e:
                    print(e)
                    dpk_with_error.append(str(str(dpk['tipodocto']) + ' ' + str(dpk['doctoerp']) + ' ' +str(dpk['numpedido']) + ' ' + str(dpk['productoean'])))
                    print('Error creating dpk %s' % str(str(dpk['tipodocto']) + ' ' + str(dpk['doctoerp']) + ' ' +str(dpk['numpedido']) + ' ' + str(dpk['productoean'])))
                    continue
        else:
            print('No Dpk to create')
            return {"message" : "No dpk to create"}
        
        return {
            'Dpk_created': dpk_created,
            'Dpk_with_error': dpk_with_error
        }
    except Exception as e:
        print(e)
        return {"message" : "Error creating item"}