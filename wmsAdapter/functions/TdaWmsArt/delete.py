from wmsAdapter.functions.TdaWmsArt.read import read_articles


def delete_articles(request, db_name):
    try:
        product = read_articles(request, db_name=db_name)
        if type(product) == str:
            return product
        else:
            if len(list(product)) == 1:
                product = product[0]
                product.delete(using=db_name)
                return 'Deleted successfully'
            elif len(list(product)) == 0:
                return 'Product not found'
            else:
                return 'More than one product found'
    except Exception as e:
        print(e)
        return str(e.__cause__)