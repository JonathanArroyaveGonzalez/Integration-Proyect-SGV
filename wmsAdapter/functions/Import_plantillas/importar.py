 
from .create import *

def importar(request_data=None):

    if not request_data:
        return "No data"
    else:
        request_data = dict(request_data)

    database = request_data['database']

    try:

        table = list(request_data.keys())[0]
        table_list = table.replace("'", '')
        table_list = table_list.split('-')

        for t in table_list:
            print(t)
            try:
                print(database)
                plantilla = list(request_data[str(table)].keys())[0]
                print(plantilla)

                data = request_data[str(table)][str(plantilla)]

            except Exception as e:
                print(e)
                print(e.__cause__)
                return str(e)

            print("CREATING " + str(t) + " " + str(plantilla))
            response = create_from_plantilla(database, t, plantilla, data)

            if len(response['error']) > 0:
                print(response['error'])
                raise Exception(response['error'])

        if len(response['lines']) > 0:
            return response
        else:
            raise Exception(response)

    except Exception as e:
        print(e)
        return str(e)