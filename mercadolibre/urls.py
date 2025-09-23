from django.urls import re_path, path

from mercadolibre.views.Auth import auth
from mercadolibre.views.Customer import create_customer, update_customer
from mercadolibre.views.Product import art
from mercadolibre.views.UpdateProduct import update_product, update_product_post
from mercadolibre.views.sync_products import (
    sync_products_view,
    sync_status_view,
    sync_specific_products_view,
)

# from mercadolibre.views.Customer import clt
# from mercadolibre.views.Barcode import codbarras


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
    
    # Endpoints comentados para referencia futura
    # path("customer/view/", view_ml_user, name="view_ml_user"),
    # re_path(r'^Codbarras$', codbarras),
    # re_path(r'^clt$', clt),
]
