from django.urls import re_path, path

from mercadolibre.views.Auth import auth
from mercadolibre.views.Customer import MeliCustomerSyncView
from mercadolibre.views.Product import MeliProductSyncView


mercadolibre_endpoints = [
    # Autenticación
    re_path(r"^auth/refresh$", auth),
    # Clientes - Sincronización unificada
    path("customer/", MeliCustomerSyncView.as_view(), name="meli-customer-sync"),
    # Productos - Sincronización unificada
    path("product/", MeliProductSyncView.as_view(), name="meli-sync"),
]
