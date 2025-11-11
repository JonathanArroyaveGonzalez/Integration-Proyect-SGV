# urls.py  (de la app de integración)

from django.urls import path
from transprensa.views.remesaView import  procesar_guia

transprensa_endpoints = [
    # Endpoint Procesar Guía
    path("guide/", procesar_guia, name="procesar_guia"),
]
