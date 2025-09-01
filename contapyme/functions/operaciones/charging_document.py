from datetime import datetime
import requests

from contapyme.functions.login.login import login
from contapyme.functions.pedido.read import read_orders
from settings.models.config import Config
from wmsAdapter.models import TdaWmsDpk, TdaWmsEpk

def create_charging_document(db_name, docerp):
    try:
        # Authenticate to obtain a token
        keyagent = login(db_name)

        # Check the token
        if not keyagent:
            raise ValueError('User authentication failed')
        
        c = Config()
        config_data = c.get_config(db_name, 'contapyme')['contapyme']

        iapp = config_data["iapp"]
        url = config_data["url"]
        
        endpoint = '/TCatOperaciones/"DoExecuteOprAction"/'
        
        # URL for the POST request
        url = url + endpoint
        
    # If there is a authentication error
    except Exception as e:
        raise ValueError(e)
    
    # Extracting parameters from the request
    pendiente = docerp.split('.')

    try:
        if len(pendiente) > 1:
            pendiente = pendiente[0]
        else:
            pendiente = docerp

        order = read_orders(db_name, 'ORD1', pendiente)
        if not order:
            raise ValueError('Error getting the order')
        
    except Exception as e:
        raise ValueError(e)
    
    try:
        epk = list(TdaWmsEpk.objects.using(db_name).filter(doctoerp=docerp).values())
    except Exception as e:
        raise ValueError(e)

    if len(epk) > 0:
        epk = epk[0]
    else:
        raise ValueError('Error getting epk')
    
    item = epk["item"]
    estadoerp = epk["estadoerp"]
    notas = epk["notas"]
    picking = epk["picking"]
    
    # Extracting data from the order       
    header = order["encabezado"]
    imoneda = header["imoneda"]
    banulada = header["banulada"]
    iemp = header["iemp"]
    iclasifop = header["iclasifop"]
    inumoper = header["inumoper"]
    bniif = header["bniif"]
    blocal = header["blocal"]
    bconfirmaenviofe = header["bconfirmaenviofe"]
    bespadre = header["bespadre"]
    
    principal_data = order["datosprincipales"]
    bregvrunit = principal_data["bregvrunit"]
    ilistaprecios = principal_data["ilistaprecios"]
    bregvrtotal = principal_data["bregvrtotal"]
    qporcdescuento = principal_data["qporcdescuento"]
    blistaconiva = principal_data["blistaconiva"]
    bcerrarref = principal_data["bcerrarref"]
    isucursalcliente = principal_data["isucursalcliente"]

    fecha_actual = datetime.now().strftime("%m-%d-%Y")
    
    item_list = order["listaproductos"]
    costototal = 0
    pedidos = []
    productoeans = []       
    for product in item_list:
        # Extracting data from the item
        productoean = product["irecurso"]
        itiporec = product["itiporec"]
        icc = product["icc"]
        preciounitario = product["mprecio"]
        qporciva = product["qporciva"]
        qporcdescuento = product["qporcdescuento"]

        # Creating a new GET request object for fetching DPK data
        dpks = list(TdaWmsDpk.objects.using(db_name).filter(doctoerp=docerp, productoean=productoean, estadodetransferencia=5).values())
        
        if len(dpks) > 0:
            for dpk in dpks:
                estadotransferencia = dpk["estadodetransferencia"]
                qtypicking = dpk["qtyenpicking"]
                descripcion = dpk["descripcion"]
                iddpk = dpk["id"]

                if float(qtypicking) > 0 and str(estadotransferencia) == "5":
                    costo = float(preciounitario) * float(qtypicking)
                    costototal += costo
                    productoeans.append((productoean, iddpk))

                    pedido_detalle = {
                        "irecurso": productoean,
                        "itiporec": itiporec,
                        "icc": icc,
                        "sobserv": descripcion,
                        "iinventario": "10",
                        "qrecurso": float(qtypicking),
                        "mprecio": preciounitario,
                        "qporcdescuento": qporcdescuento,
                        "qporciva": qporciva,
                        "mvrtotal": str(costo),
                    }
                
                    pedidos.append(pedido_detalle)

    # Creating charging document dictionary
    datajson = {
        "accion": "CREATE",
        "operaciones": [
            {
                "itdoper": "ORD2"
            }
        ],
        "oprdata": {
            "datosprincipales": {
                "init": item,
                "inittransportador": "",
                "sobserv": notas,
                "blistaconiva": blistaconiva,
                "blistaconprecios": "T",
                "bregvrunit": bregvrunit,
                "bregvrtotal": bregvrtotal,
                "ireferencia": pendiente,
                "bcerrarref": bcerrarref,
                "iinventario": "10",
                "ilistaprecios": ilistaprecios,
                "ireferenciabasadaen": "7005",
                "isucursalcliente": isucursalcliente,
                "qregseriesproductos": "0",
        },
        "encabezado": {
            "iemp": iemp,
            "itdsop": "430",
            "fsoport": fecha_actual,
            "iclasifop": iclasifop,
            "imoneda": imoneda,
            "fprocesam": fecha_actual,
            "iprocess": "2",
            "banulada": banulada,
            "blocal": blocal,
            "bniif": bniif, 
            "inumoper": inumoper, 
            "bespadre": bespadre,
            "bconfirmaenviofe": False, # Autorizacion del documento de carga
            "tdetalle": "DOCUMENTO DE CARGA",
            "mtotaloperacion": str(costototal)
        },
        "listaproductos": pedidos,
        "series": [],
        "qoprsok": "0"
    }}    

    if len(productoeans) > 0:
        # Constructs the URL for the POST request
        jsonsend = {
            '_parameters': [datajson, keyagent, iapp, "0"],
        }

        try:
            # Sending POST request to the specified URL
            response = requests.post(url, json=jsonsend)

            if response.status_code == 200:
                for ean in productoeans:    
                    prodean = ean[0]
                    lineaid = ean[1]
                    
                    TdaWmsDpk.objects.using(db_name).filter(picking=picking, productoean=prodean, id=lineaid, doctoerp=docerp , estadodetransferencia = 5).update(estadodetransferencia = 9)
            else:
                for ean in productoeans:    
                    prodean = ean[0]
                    lineaid = ean[1]
                    TdaWmsDpk.objects.using(db_name).filter(picking=picking, productoean=prodean, id=lineaid, doctoerp=docerp , estadodetransferencia = 5).update(estadodetransferencia = 8)
            
            return response.json()
            
        
        # Handling errors
        except Exception as e:
            raise ValueError(e)
    # Handling errors
    else:
        raise ValueError('No lines for the charging document')