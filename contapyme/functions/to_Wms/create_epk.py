from wmsAdapter.functions.TdaWmsEpk.create import create_epk
from wmsAdapter.models import TdaWmsEpk


def create_header_order(db_name, order, client):
    header = order["encabezado"]
    principal_data = order["datosprincipales"]
    
    doctoerp = header["snumsop"]
    if 'PED' in doctoerp:
        tipodocto = 'FLT'
    elif 'REQ' in doctoerp:
        tipodocto = 'REQ'

    # Extracting order information
    fecharegistro = header["fprocesam"]
    sobserv = principal_data["sobserv"]
    #sucursal = principal_data["isucursalcliente"]
    inumoper = header["inumoper"]
    iprocess = header["iprocess"]

    # Extracting client information
    item = client["item"]
    nombre = client["nombrecliente"]
    contacto = client.get('contacto', '')
    email = client["email"]
    ciudad = client["cuidad"]
    pais = client["paisdestino"]
    departamento = client["dptodestino"]
    direccion = client["direccion"]

    if len(sobserv) > 500:
        sobserv = sobserv[:499]

    # Creating a new EPK object with provided information
    newepk = {
        "tipodocto": tipodocto,
        "doctoerp": doctoerp,
        "numpedido": doctoerp,
        "fechaplaneacion": None,
        "f_pedido": fecharegistro,
        "item": item,
        "nombrecliente": nombre,
        "contacto": contacto,
        "email": email,
        "notas": sobserv,
        "ciudad_despacho": ciudad,
        "pais_despacho": pais,
        "departamento_despacho": departamento,
        "sucursal_despacho": None,
        "direccion_despacho": direccion,
        "idsucursal": None,
        "ciudad": ciudad,
        "pedidorelacionado": doctoerp,
        "cargue": '',
        "nit": item,
        "estadopicking": 0,
        "fecharegistro": fecharegistro,
        "fpedido": fecharegistro,
        "fechtrans": None,
        "transportadora": None,
        "centrooperacion": None,
        "estadoerp": iprocess,
        "picking_batch": None,
        "field_condicionpago": None,
        "field_documentoreferencia": inumoper,
        "bodega": '01',
        "vendedor2": None,
        "numguia": None,
        "f_ultima_actualizacion": None,
        "bodegaerp": '10'
    }
    
    response = create_epk(None, db_name, newepk)
    if response == 'created successfully':
        epk = list(TdaWmsEpk.objects.using(db_name).filter(doctoerp=doctoerp).values())
        return epk[0]
    else:
        raise ValueError('Creating epk error')