from wmsAdapter.functions.TdaWmsDpk.read import read_dpk


def delete_dpk(request, db_name):
    try:
        dpk = read_dpk(request, db_name=db_name)
        if type(dpk) == str:
            return dpk
        else:
            if len(list(dpk)) == 1:
                dpk = dpk[0]
                dpk.delete(using=db_name)
                return 'Deleted successfully'
            elif len(list(dpk)) == 0:
                return 'Dpk not found'
            else:
                return 'More than one dpk found'
    except Exception as e:
        print(e)
        return str(e.__cause__)