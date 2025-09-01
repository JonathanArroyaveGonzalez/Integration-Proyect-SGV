from django.db import connections
import re
# from BackendApp.producer import PublishAMQP


def convert_array_records_to_array_json(array=[], descriptions=()) -> list:
    if len(array) == 0:
        return []
    if len(descriptions) == 0:
        return []

    columnNames = [column[0] for column in descriptions]
    response = []
    for record in array:
        response.append(dict(zip(columnNames, record)))
    return response

def exec_query(query='', params=(), database="default"):
    cursor = connections[database].cursor()
    print(query)
    print(params)
    try:
        cursor.execute(query, params)
        response = cursor.fetchall()
        descriptions = cursor.description
        response = convert_array_records_to_array_json(response, descriptions)
    # except Exception as e:
    except Exception as e:
        mensaje_error = obtener_mensaje_error(str(e))
        raise Exception(str(mensaje_error))
    cursor.close()
    return response

def obtener_mensaje_error(error):

    patron = r"\[SQL Server\](.*?)\s*\("
    match = re.search(patron, error)
    if match:
        mensaje = match.group(1).strip()
    else:
        mensaje = "Server error"
    return mensaje

def obtener_http_status_code(status_code):
        if status_code >= 500 and status_code < 600:
            if status_code == 500:
                return "Internal Server Error"
            elif status_code == 501:
                return "Not Implemented: The server does not support the functionality required to fulfill the request."
            elif status_code == 502:
                return "Bad Gateway"
            elif status_code == 503:
                return "Service Unavailable: The server is currently unable to handle the request due to a temporary overload or maintenance of the server."
            elif status_code == 504:
                return "Gateway Timeout"
            elif status_code == 505:
                return "HTTP Version Not Supported"
            else:
                return "Error de servidor desconocido"
        elif status_code >= 400 and status_code < 500:
            return "Error de cliente"
        elif status_code >= 300 and status_code < 400:
            return "Redirección"
        elif status_code >= 200 and status_code < 300:
            return "Éxito"
        else:
            return "Código de estado no reconocido"
