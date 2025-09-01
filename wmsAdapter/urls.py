from .views import *
from django.urls import re_path
from settings import *

wms_endpoints = [
    re_path(r'^art$', art),   # type: ignore  
    re_path(r'^epk$', epk),  # type: ignore  
    re_path(r'^dpk$', dpk),  # type: ignore  
    re_path(r'^euk$', euk),  # type: ignore  
    re_path(r'^duk$', duk),  # type: ignore  
    re_path(r'^epn$', epn),  # type: ignore  
    re_path(r'^dpn$', dpn),  # type: ignore  
    re_path(r'^clt$', clt),  # type: ignore  
    re_path(r'^prv$', prv),  # type: ignore  
    re_path(r'^art_ext$', art_ext),   # type: ignore 
    re_path(r'^relacion_seriales$', relacion_seriales),   # type: ignore 
    re_path(r'^dynamic_queries$', consultasDinamicas),  # type: ignore
    re_path(r'^execute/dynamic_queries$', execute_consultas_dinamicas),  # type: ignore
    re_path(r'^execute/origin/dynamic_queries$', execute_consultas_dinamicas_from_origen),  # type: ignore
    re_path(r'^execute$', executeSp),  # type: ignore  
    re_path(r'^execute/picking$', picking),  # type: ignore  

    # re_path(r'^get-apikey$', get_apikey),  # type: ignore  
    # re_path(r'^create-apikey$', create_apikey),
    re_path(r'^history$', vtggtpicmp),  # type: ignore  
    re_path(r'^location$', vtpicmp),  # type: ignore  
    re_path(r'^detallePrepack$', vtggtdprepack),  # type: ignore  
    re_path(r'^insert/inv$', insertinv),  # type: ignore  
    #re_path(r'^update/inv$', updatetinv),   # type: ignore  
    re_path(r'^update/euk$', updateEuk), # type: ignore 

    re_path(r'^inv$', vVTInvPic),  # type: ignore  
    re_path(r'^vempleados$', vempleados),  # type: ignore  

    re_path(r'^execute/dynamic/query$', executeSp),  # type: ignore  
]

     