from django.urls import re_path
from mercadolibre.views import (
    auth, products, orders, inventory
)

mercadolibre_endpoints = [
    re_path(r'^auth/login$', auth.login),
    re_path(r'^auth/refresh$', auth.refresh_token),
    # re_path(r'^products/sync$', products.sync),
    re_path(r'^products/update$', products.update),
    re_path(r'^orders/sync$', orders.sync),
    re_path(r'^orders/update$', orders.update),
    re_path(r'^inventory/update$', inventory.update),
]
