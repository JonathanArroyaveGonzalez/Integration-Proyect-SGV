from wmsAdapter.functions.TdaWmsEpk.read import read_epk


def delete_epk(request, db_name):
    try:
        epk = read_epk(request, db_name=db_name)
        if type(epk) == str:
            return epk
        else:
            if len(list(epk)) == 1:
                epk = epk[0]
                epk.delete(using=db_name)
                return 'Deleted successfully'
            elif len(list(epk)) == 0:
                return 'Epk not found'
            else:
                return 'More than one epk found'
    except Exception as e:
        print(e)
        return str(e.__cause__)