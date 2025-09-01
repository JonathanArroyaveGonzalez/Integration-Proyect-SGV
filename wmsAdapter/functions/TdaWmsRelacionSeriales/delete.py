from wmsAdapter.functions.TdaWmsRelacionSeriales.read import read_relacion_seriales


def delete_relacion_seriales(request, db_name):
    try:
        serial = read_relacion_seriales(request, db_name=db_name)
        if type(serial) == str:
            return serial
        else:
            if len(list(serial)) == 1:
                serial = serial[0]
                serial.delete(using=db_name)
                return 'Deleted successfully'
            elif len(list(serial)) == 0:
                return 'Dpk not found'
            else:
                return 'More than one serial found'
    except Exception as e:
        print(e)
        return str(e.__cause__)