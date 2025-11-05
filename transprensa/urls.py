# urls.py  (de la app de integración)

from django.urls import path
from transprensa.views.createRemesa import crear_y_guardar_guia_view

transprensa_endpoints = [
    
    path("remesas/v2", crear_y_guardar_guia_view, name="crear_y_guardar_guia"),
]
