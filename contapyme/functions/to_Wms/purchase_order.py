from contapyme.functions.compra.read import read_purchase_orders
from contapyme.functions.to_Wms.create_art import create_article
from contapyme.functions.to_Wms.create_duk import create_detail_purchase_order
from contapyme.functions.to_Wms.create_euk import create_header_purchase_order
from contapyme.functions.to_Wms.create_prv import create_supplier
from wmsAdapter.models import TdaWmsArt, TdaWmsDuk, TdaWmsEuk, TdaWmsPrv


def create_purchase_order(db_name, doctoerp):
    try:
        order = read_purchase_orders(db_name, doctoerp)
        if not order:
            raise ValueError('Error getting the purchase order')
    
        principal_data = order["datosprincipales"]
        header = order["encabezado"]
        lista_productos = order["listaproductos"]

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
        
        item = principal_data["init"]

        euk = list(TdaWmsEuk.objects.using(db_name).filter(doctoerp=doctoerp).values())

        if len(euk) > 0:
            euk = euk[0]
        else:
            prv = list(TdaWmsPrv.objects.using(db_name).filter(item=item).values())
            if len(prv) > 0:
                prv = prv[0]
            else:
                prv = create_supplier(db_name, item)

            euk = create_header_purchase_order(db_name, order, prv)
    
    except Exception as e:
        raise ValueError(e)

    duks = []
    for producto in lista_productos:
        irecurso = producto["irecurso"]

        try:
            art = list(TdaWmsArt.objects.using(db_name).filter(productoean=irecurso).values())
            if len(art) > 0:
                art = art[0]
            else:
                art = create_article(db_name, irecurso)

            duk = list(TdaWmsDuk.objects.using(db_name).filter(doctoerp=doctoerp, productoean=irecurso).values())
        
            if len(duk) == 0:
                duk = create_detail_purchase_order(db_name, euk, producto, art)
                duks.append({"productoean": duk["productoean"], "lineaidpicking": duk["lineaidpicking"]})

        except Exception as e:
            duks.append({"productoean": irecurso, 'error': str(e)})
        
    
    return {
        'unido': euk['unido'],
        'detail': duks
    }
    
    