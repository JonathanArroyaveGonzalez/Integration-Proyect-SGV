import json
from django.db import connections

from wmsAdapter.utils.reserved_words import get_reserved_words

def execute_sp(db_name, sp, data=None, schema=None):
    if sp is None:
        raise ValueError('No stored procedure specified')

    if schema is None:
        schema = 'dbo'
    #print(sp)

    params = ''
    if data:
        try:
            request_data = json.loads(data)
        except json.JSONDecodeError:
            raise ValueError('Invalid JSON data')

        for key, value in request_data.items():
            params += f"{key} = '{value}', "
        
        params = params[:-2]  # Remueve la última coma y espacio
    
    reserved_words = list(get_reserved_words())
    try:
        with connections[db_name].cursor() as cursor:
            query = f"EXECUTE [{schema}].[{sp}] {params}" if params else f"EXECUTE [{schema}].[{sp}]"
            query_list = query.upper().split(' ')

            for r in reserved_words:
                if r in query_list:
                    # print(r)
                    raise ValueError('Invalid query')

            # print(query)
            cursor.execute(query)

            if cursor.description:
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                data = [dict(zip(columns, row)) for row in rows]
                return data
            else:
                return {sp: "Ejecución exitosa"}

    except Exception as e:
        print(e)
        raise ValueError(e)
