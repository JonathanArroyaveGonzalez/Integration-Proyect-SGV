from settings.models import *


def get_plantillas(db_name, table, plantilla):

    try:
        # db_name = 'pmc'
        c = config(db_name, 'csv_import')

        if table:
            config_array = []
            table = table.upper()
            table_config = c.get_config()['csv_import'][str(table)]

            if plantilla:
                index = [i for i, d in enumerate(
                    table_config) if str(plantilla) in d.keys()]
                plantilla = plantilla.upper()
                table_config = table_config[index[0]][str(plantilla)]

        else:
            table_config = c.get_config()['csv_import']

        return table_config

    except Exception as e:
        print(e)
        return str(e)
