import json
from django.db import connections


def get_non_existent_records(db_name, table, json_string):
    # Ejecutar el procedimiento almacenado usando la base de datos específica
    with connections[db_name].cursor() as cursor:
        cursor.execute(f"EXEC dbo.sp_VerificarDatosNoExistentes{table} @jsonArray = %s", [json_string])
        # Obtener resultado
        result = cursor.fetchone()[0]  # El resultado es un string JSON
    
    # Convertir el resultado de vuelta a un objeto Python
    registros_no_existentes = json.loads(result)

    registros_a_crear = []
    for reg in registros_no_existentes:
        # print(type(reg['JsonData']))
        registros_a_crear.append(json.loads(reg['JsonData']))

    return registros_a_crear
