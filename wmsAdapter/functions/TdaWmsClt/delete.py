from wmsAdapter.functions.TdaWmsClt.read import read_clt


def delete_clt(request, db_name):
    try:
        clt = read_clt(request, db_name=db_name)
        if type(clt) == str:
            return clt
        else:
            if len(list(clt)) == 1:
                clt = clt[0]
                clt.delete(using=db_name)
                return 'Deleted successfully'
            elif len(list(clt)) == 0:
                return 'Clt not found'
            else:
                return 'More than one clt found'
    except Exception as e:
        print(e)
        return str(e.__cause__)