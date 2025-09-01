from wmsAdapter.functions.TdaWmsDuk.read import read_duk


def delete_duk(request, db_name):
    try:
        duk = read_duk(request, db_name=db_name)
        if type(duk) == str:
            return duk
        else:
            if len(list(duk)) == 1:
                duk = duk[0]
                duk.delete(using=db_name)
                return 'Deleted successfully'
            elif len(list(duk)) == 0:
                return 'Duk not found'
            else:
                return 'More than one duk found'
    except Exception as e:
        print(e)
        return str(e.__cause__)