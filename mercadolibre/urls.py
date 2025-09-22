from django.urls import re_path

from mercadolibre.views.Auth import auth
from mercadolibre.views.Product import art

# from mercadolibre.views.Customer import clt
# from mercadolibre.views.Barcode import codbarras

mercadolibre_endpoints = [
    re_path(r"^auth/refresh$", auth),
    re_path(r"^products$", art),
    re_path(r"^customer$", art),
    re_path(r"^products$", art),
    # re_path(r'^Codbarras$', codbarras),
    # re_path(r'^clt$', clt),
]
