""" Models and functions  """
from wmsAdapter.models.TdaWmsArt import TdaWmsArt 
from wmsAdapter.functions.TdaWmsArt.create import create_articles

def create_TdaWmsArt_from_dynamic_queries(to_create,db_name) -> dict:
    '''
    Function to create articles from dynamic queries
    @params:
        to_create: list of articles to create
        db_name: name of the database
    '''
    try:
        wms_articles = list(TdaWmsArt.objects.using(db_name).all().values_list('productoean', flat=True))
    except Exception as e:
        wms_articles = []
    
    try:
        products_to_create = []
        
        # breakpoint()

        for product in to_create:
            if str(product['productoean']) not in wms_articles:
                products_to_create.append(product)

        print('products_to_create')
        print(len(products_to_create))

        products_created = []
        products_with_error = []
        if len(products_to_create) > 0:
            for product in products_to_create:
                try:
                    # breakpoint()
                    response = create_articles(None, db_name, request_data= product)
                    if response == 'created successfully':
                        products_created.append(product['productoean'])
                    
                    else:
                        products_with_error.append(product['productoean'])
                        print('Error creating product %s' % product['productoean'])

                except Exception as e:
                    print(e)
                    products_with_error.append(product['productoean'])
                    print('Error creating product %s' % product['productoean'])
                    continue
        else:
            print('No products to create')
            return {"message" : "No products to create"}
        
        return {
            'products_created': products_created,
            'products_with_error': products_with_error
        }
    except Exception as e:
        print(e)
        return {"message" : "Error creating products"}