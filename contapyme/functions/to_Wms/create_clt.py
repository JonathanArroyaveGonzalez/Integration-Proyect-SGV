from contapyme.functions.tercero.read import read_thirdparty
from wmsAdapter.models import TdaWmsClt
from wmsAdapter.functions.TdaWmsClt.create import create_clt

def create_client(db_name, init):
    try:
        cliente = read_thirdparty(db_name, init)
        if not cliente:
            raise ValueError(f'Client {init} does not exist in ContaPyme')
    except Exception as e:
        raise ValueError(e)
    
    ntercero = cliente.get('ntercero', '')
    napellido = cliente.get('napellido', '')
    email = cliente.get('semail', '')
    contacto = cliente.get('ttelefono', '')
    direccion = cliente.get('tdireccion', '')
    pais = cliente.get('npais', '')
    departamento = cliente.get('ndep', '')
    ciudad = cliente.get('nmun', '')
    ipais = cliente.get('ipais', '')
    idepartamento = cliente.get('idep', '')
    iciudad = cliente.get('imun', '')
    notas = cliente.get('sobservaciones', '')
    nombre = ntercero + " " + napellido

    if contacto == '':
        contacto = cliente.get('tcelular', '')
    
    newclt = {
        "nit": init,
        "nombrecliente": nombre,
        "direccion": direccion,
        "isactivoproveedor": None,
        "condicionescompra": None,
        "codigopais": None,
        "monedadefacturacion": None,
        "item": init,
        "activocliente": 1,
        "ciudaddestino": ciudad,
        "dptodestino": departamento,
        "paisdestino": pais,
        "codciudaddestino": iciudad,
        "coddptodestino": idepartamento,
        "codpaisdestino": ipais,
        "fecharegistro": None,
        "telefono": contacto,
        "cuidad": ciudad,
        "cuidaddespacho": None,
        "notas": notas,
        "contacto": contacto,
        "email": email,
        "paisdespacho": "Colombia",
        "departamentodespacho": None,
        "sucursaldespacho": None,
        "idsucursal": None,
        "isactivocliente": 1,
        "isactivoproveed": 1,
        "estadotransferencia": 0,
        "vendedor": None,
        "zip_code": None,
        "licencia": None,
        "compania": None
    }
    
    
    response = create_clt(None, db_name, newclt)
    if response == 'created successfully':
        clt = list(TdaWmsClt.objects.using(db_name).filter(item=init).values())
        return clt[0]
    else:
        raise ValueError('Creating client error')