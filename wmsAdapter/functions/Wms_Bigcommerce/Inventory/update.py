from wmsAdapter.models import *

def update_inv_wms_bigcommerce(db_name: str , sku = None):
    if sku is None:
        