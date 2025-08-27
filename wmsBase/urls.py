from django.urls import re_path
from wmsBase.views.LogisticVariables import logistic_variables
from wmsBase.views.Barcode import t_relacion_codbarras
from wmsBase.views.Warehouse import bod

wms_base_endpoints = [ 
    re_path(r'^tRelacionCodbarras$', t_relacion_codbarras),  
    re_path(r'^bod$', bod),  
    re_path(r"^tdetallerefenciacv", logistic_variables),
]