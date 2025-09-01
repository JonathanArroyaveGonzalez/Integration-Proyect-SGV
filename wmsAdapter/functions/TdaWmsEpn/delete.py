from wmsAdapter.functions.TdaWmsEpn.read import read_epn


def delete_epn(request, db_name):
    try:
        epn = read_epn(request, db_name=db_name)
        if type(epn) == str:
            return epn
        else:
            if len(list(epn)) == 1:
                epn = epn[0]
                epn.delete(using=db_name)
                return 'Deleted successfully'
            elif len(list(epn)) == 0:
                return 'Epn not found'
            else:
                return 'More than one epn found'
    except Exception as e:
        print(e)
        return str(e.__cause__)