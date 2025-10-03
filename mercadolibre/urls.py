from django.urls import re_path, path

from mercadolibre.views.Auth import auth
from mercadolibre.views.Customer import MeliCustomerSyncView
from mercadolibre.views.Product import MeliProductSyncView
from mercadolibre.views.Supplier import SupplierSyncView
from mercadolibre.views.inventory import MeliInventoryView
from mercadolibre.views.order import MeliOrderSyncView


mercadolibre_endpoints = [
    # Autenticación
    # re_path(r"^auth/refresh$", auth),
    path("auth/", auth, name="meli-auth-refresh"),
    # Clientes - Sincronización unificada
    path("customer/", MeliCustomerSyncView.as_view(), name="meli-customer-sync"),
    # Productos - Sincronización unificada
    path("product/", MeliProductSyncView.as_view(), name="meli-sync"),
    # Inventario - Gestión unificada
    path("inventory/", MeliInventoryView.as_view(), name="meli-inventory"),
    # Pedidos - Sincronización unificada
    path("order/", MeliOrderSyncView.as_view(), name="meli_order_sync"),
]
