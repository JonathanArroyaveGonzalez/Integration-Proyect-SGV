# urls.py  (de la app de integración)

from django.urls import path
from transprensa.views.remesaView import procesar_remesa

transprensa_endpoints = [
    
    
    # Endpoint Procesar Remesa
    path("remesa/procesar/", procesar_remesa, name="procesar_remesa"),
]
