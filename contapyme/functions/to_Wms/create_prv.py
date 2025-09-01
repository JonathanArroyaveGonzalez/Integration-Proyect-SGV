from django.utils import timezone

from contapyme.functions.tercero.list import list_thirdparty
from contapyme.functions.tercero.read import read_thirdparty
from wmsAdapter.functions.TdaWmsPrv.create import create_prv
from wmsAdapter.models import TdaWmsPrv


def create_supplier(db_name, init):
    try:
        tercero = read_thirdparty(db_name, init)
        if not tercero:
            raise ValueError(f'Supplier {init} does not exist in ContaPyme')
    except Exception as e:
        raise ValueError(e)
    
    ntercero = tercero.get('ntercero', '')
    napellido = tercero.get('napellido', '')
    email = tercero.get('semail', '')
    direccion = tercero.get('tdireccion', '')
    ipais = tercero.get('ipais', '')
    nombre = ntercero + " " + napellido
    
    fechaactual = timezone.now().isoformat()

    newprv = {
        "nit": init,
        "nombrecliente": nombre,
        "direccion": direccion,
        "isactivoproveedor": 1,
        "condicionescompra": "",
        "codigopais": ipais,
        "monedadefacturacion": "",
        "item": init,
        "activocliente": 1,
        "fecharegistro": fechaactual,
        "estadotransferencia": 0,
        "sucursal": "01",
        "email": email,
        "beneficiario": 0,
        "item_sucursal": "",
        "codigoter": ""
    }
    
    
    response = create_prv(None, db_name, newprv)
    if response == 'created successfully':
        prv = list(TdaWmsPrv.objects.using(db_name).filter(item=init).values())
        return prv[0]
    else:
        raise ValueError('Creating supplier error')
    

def create_list_supplier(db_name):
    try:
        terceros = list_thirdparty(db_name)
        if not terceros:
            raise ValueError('Error getting ContaPyme suppliers')
    
    except Exception as e:
        raise ValueError(e)
    

    prv = list(TdaWmsPrv.objects.using(db_name).values('item'))
    prv_wms = []
    for p in prv:
        item = p["item"]
        if item not in prv_wms:
            prv_wms.append(item)

    prv_to_created = []
    for t in terceros:
        init = t["init"]
        if init not in prv_wms:
            prv_to_created.append(t)

    prv_created = []
    prv_error = []
    for p in prv_to_created:
        init = p.get('init', '')
        ntercero = p.get('ntercero', '')
        napellido = p.get('napellido', '')
        email = p.get('semail', '')
        direccion = p.get('tdireccion', '')
        ipais = p.get('ipais', '')

        if napellido != "" and napellido:
            nombre = ntercero + " " + napellido
        else:
            nombre = ntercero

        fechaactual = timezone.now().isoformat()

        newprv = {
            "nit": init,
            "nombrecliente": nombre,
            "direccion": direccion,
            "isactivoproveedor": 1,
            "condicionescompra": "",
            "codigopais": ipais,
            "monedadefacturacion": "",
            "item": init,
            "activocliente": 1,
            "fecharegistro": fechaactual,
            "estadotransferencia": 0,
            "sucursal": "01",
            "email": email,
            "beneficiario": 0,
            "item_sucursal": "",
            "codigoter": ""
        }
        
        
        response = create_prv(None, db_name, newprv)
        if response == 'created successfully':
            prv_created.append(init)
        else:
            prv_error.append(init)

    return {'prv_created': prv_created,
            'prv_with_error': prv_error}