""" This function deletes an article from the database """
from wmsAdapterV2.functions.Product.read import read_articles_obj

def delete_articles(request, db_name):
    '''
    Delete an article from the database
    @params:
        request: request object
        db_name: name of the database
    '''
    try:
        product = read_articles_obj(request, db_name=db_name)

        # Check the product 
        # If there is more than one product
        if len(list(product)) > 1:
            raise ValueError("Only one product can be updated at a time")
        
        # If there is no product	
        if len(list(product)) == 0:
            raise ValueError("No product found")

        # If there is only one product
        else:
            # Get the product
            product_obj = product[0]

            # Delete the product
            product_obj.delete(using=db_name)  # type: ignore
            return 'Deleted successfully'
    
    # If there is an error
    except Exception as e:
        raise ValueError(str(e))