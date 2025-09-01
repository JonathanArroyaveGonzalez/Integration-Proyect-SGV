from wmsAdapter.functions.TdaWmsConsultasAleatorias.read import read_consultas_dinamicas


def delete_consultas_dinamicas(request, db_name):
    try:
        register = read_consultas_dinamicas(request, db_name=db_name)

        if len(list(register)) == 1:
            register = register[0]
            register.delete(using=db_name)  # type: ignore
            return 'Deleted successfully' 
        elif len(list(register)) == 0:
            return 'register not found'
        else:
            return 'More than one register found'
    except Exception as e:
        print(e)
        return str(e.__cause__)