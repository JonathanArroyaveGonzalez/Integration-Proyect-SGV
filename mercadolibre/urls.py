from django.urls import re_path, path

from mercadolibre.views.Auth import auth
from mercadolibre.views.Customer import create_customer
from mercadolibre.views.Product import art
from mercadolibre.views.sync_products import (
    sync_products_view,
    sync_status_view,
    sync_specific_products_view,
)

# from mercadolibre.views.Customer import clt
# from mercadolibre.views.Barcode import codbarras


mercadolibre_endpoints = [
    re_path(r"^auth/refresh$", auth),
    re_path(r"^products$", art),
    # Endpoints de sincronización de productos
    path("products/sync/", sync_products_view, name="sync_products"),
    path("products/sync/status/", sync_status_view, name="sync_status"),
    path(
        "products/sync/specific/",
        sync_specific_products_view,
        name="sync_specific_products",
    ),
    # Endpoints de clientes
    path("customer/sync/", create_customer, name="sync_customers"),
    # Endpoint para ver usuario de MercadoLibre
    # path("customer/view/", view_ml_user, name="view_ml_user"),
]
