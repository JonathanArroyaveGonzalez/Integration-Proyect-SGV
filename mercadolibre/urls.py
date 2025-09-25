from django.urls import re_path, path

from mercadolibre.views.Auth import auth
from mercadolibre.api.v1.customers import (
    create as create_customer,
    update as update_customer,
)
from mercadolibre.api.v1.products import (
    products as art,
    update_product,
    update_product_post,
    sync_products_view,
    sync_status_view,
    sync_specific_products_view,
)

# from mercadolibre.views.Customer import clt
from mercadolibre.api.v1.barcodes import (
    get_barcode as get_barcode_view,
    sync_from_meli_items as sync_barcodes_view,
)


mercadolibre_endpoints = [
    # Autenticación
    re_path(r"^auth/refresh$", auth),
    
    # Productos - CRUD básico
    re_path(r"^products$", art),
    
    # Productos - Sincronización
    path("products/sync/", sync_products_view, name="sync_products"),
    path("products/sync/status/", sync_status_view, name="sync_status"),
    path(
        "products/sync/specific/",
        sync_specific_products_view,
        name="sync_specific_products",
    ),
    
    # Productos - Actualización
    re_path(
        r"^products/update/(?P<product_id>[^/]+)/?$",
        update_product,
        name="update_product",
    ),
    path("products/update/", update_product_post, name="update_product_post"),
    
    # Clientes
    path("customer/sync/", create_customer, name="sync_customers"),
    path("customer/update/", update_customer, name="update_customers"),
    
    # Barcodes (opcional)
    re_path(r"^barcodes/(?P<ean>[^/]+)/?$", get_barcode_view, name="get_barcode"),
    path("barcodes/sync_from_meli", sync_barcodes_view, name="sync_barcodes_from_meli"),
]
