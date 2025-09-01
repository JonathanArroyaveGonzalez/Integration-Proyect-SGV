from django.urls import re_path

from contapyme.views.factura import factura
from contapyme.views.compra import compra
from contapyme.views.ddc import ddc
from contapyme.views.operaciones import operaciones
from contapyme.views.pedido import pedido
from contapyme.views.producto import producto
from contapyme.views.authentication import authentication
from contapyme.views.tercero import tercero
from contapyme.views.to_Wms import to_wms

contapyme_endpoints = [
    re_path(r'^authentication$', authentication), 
    re_path(r'^tercero$', tercero),
    re_path(r'^producto$', producto), 
    re_path(r'^pedido$', pedido), 
    re_path(r'^compra$', compra), 
    re_path(r'^operaciones$', operaciones), 
    re_path(r'^to_wms$', to_wms), 
    re_path(r'^create_ddc$', ddc),
    re_path(r'^factura$', factura) 
]