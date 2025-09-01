from contapyme.functions.pedido.read import read_orders
from contapyme.functions.to_Wms.create_art import create_article
from contapyme.functions.to_Wms.create_clt import create_client
from contapyme.functions.to_Wms.create_dpk import create_detail_order
from contapyme.functions.to_Wms.create_epk import create_header_order
from wmsAdapter.models import TdaWmsArt, TdaWmsClt, TdaWmsDpk, TdaWmsEpk


def create_order(db_name, type_order, doctoerp):
    response = {}
    try:
        order = read_orders(db_name, type_order, doctoerp)
        if not order:
            raise ValueError('Error getting the order')
    except Exception as e:
        raise ValueError(e)
    
    principal_data = order["datosprincipales"]
    header = order["encabezado"]
    
    # Check if the order is cancelled
    canceled = header["banulada"]
    if canceled == "T" or canceled == True:
        return ValueError(f'The order {doctoerp} was cancelled')

    # Check if the order is approved
    approved = header["bconfirmaenviofe"]
    if approved == False or approved == "F":
        raise ValueError(f'The order {doctoerp} is not approved')
    
    # Check if the order belongs to the correct warehouse
    cellar = principal_data["iinventario"]
    if cellar != '10':
        raise ValueError(f'The order {doctoerp} belongs to another store') 
    
    try:
        epk = list(TdaWmsEpk.objects.using(db_name).filter(doctoerp=doctoerp).values())
    except Exception as e:
        raise ValueError(e)
    
    if len(epk) > 0:
        epk = epk[0]
    else:
        item = principal_data["init"]
        try:  
            clt = list(TdaWmsClt.objects.using(db_name).filter(item=item).values())
        except Exception as e:
            raise ValueError(e)
        
        if len(clt) > 0:
            clt = clt[0]
        else:
            clt = create_client(db_name, item)
        
        epk = create_header_order(db_name, order, clt)
        
    lista_productos = order["listaproductos"]
    dpks = []
    for producto in lista_productos:
        irecurso = producto["irecurso"]
        try:
            art = list(TdaWmsArt.objects.using(db_name).filter(productoean=irecurso).values())
            
            if len(art) > 0:
                art = art[0]
            else:
                art = create_article(db_name, irecurso)
            
            dpk = list(TdaWmsDpk.objects.using(db_name).filter(doctoerp=doctoerp, productoean=irecurso).values())
            
            if len(dpk) == 0:
                dpk = create_detail_order(db_name, epk, producto, art)
                dpks.append({"productoean": dpk["productoean"], "lineaidpicking": dpk["lineaidpicking"]})
        except Exception as e:
            dpks.append({"productoean": irecurso, 'error': str(e)})

    response['dpk'] = dpks
    return {
        'picking': epk["picking"],
        'detail': dpks
    }