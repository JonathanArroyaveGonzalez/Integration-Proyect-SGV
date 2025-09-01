from wmsAdapter.functions.TdaWmsEuk.read import read_euk


def delete_euk(request, db_name):
    try:
        euk = read_euk(request, db_name=db_name)
        if type(euk) == str:
            return euk
        else:
            if len(list(euk)) == 1:
                euk = euk[0]
                euk.delete(using=db_name)
                return 'Deleted successfully'
            elif len(list(euk)) == 0:
                return 'Euk not found'
            else:
                return 'More than one euk found'
    except Exception as e:
        print(e)
        return str(e.__cause__)