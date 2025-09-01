from wmsAdapter.functions.TdaWmsDpn.read import read_dpn


def delete_dpn(request, db_name):
    try:
        dpn = read_dpn(request, db_name=db_name)
        if type(dpn) == str:
            return dpn
        else:
            if len(list(dpn)) == 1:
                dpn = dpn[0]
                dpn.delete(using=db_name)
                return 'Deleted successfully'
            elif len(list(dpn)) == 0:
                return 'Dpn not found'
            else:
                return 'More than one dpn found'
    except Exception as e:
        print(e)
        return str(e.__cause__)