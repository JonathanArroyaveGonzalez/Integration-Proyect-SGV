from contapyme.functions.compra.read import read_purchase_orders
from contapyme.functions.login.login import login
from contapyme.functions.operaciones.save import save_operation
from settings.models.config import Config
from wmsAdapter.models import TdaWmsDuk


def update_purchase_order(db_name, doctoerp):
    try:
        purchase_order = read_purchase_orders(db_name, doctoerp)
        
        if not purchase_order:
            raise ValueError('Error getting the purchase_order')
        inumoper = purchase_order['encabezado']['inumoper']
        itdoper = purchase_order['encabezado']['itdoper']
        listaproductos = purchase_order['listaproductos']
        
        duks = list(TdaWmsDuk.objects.using(db_name).filter(doctoerp=doctoerp, tipodocto='ORC', estadodetransferencia__in=[3,8]).values('productoean', 'qtyenpicking'))
        lines_received = {}
        if len(duks) == 0:
            raise ValueError('There are no products received to be sent')

        TdaWmsDuk.objects.using(db_name).filter(doctoerp=doctoerp, tipodocto='ORC', estadodetransferencia__in=[3,8]).update(estadodetransferencia=5)
        for duk in duks:
            lines_received[duk['productoean']] = str(float(duk['qtyenpicking']))

    except Exception as e:
        raise ValueError(e)
    
    products_received = []
    for product in listaproductos:
        irecurso = product['irecurso']

        if irecurso in lines_received and lines_received[irecurso] is not None:
            product['qrecurso'] = lines_received[irecurso]
            products_received.append(product)
    
    purchase_order['listaproductos'] = products_received
    #listaproductos = {'listaproductos': products_received}

    try:
        response = save_operation(db_name, inumoper, itdoper, purchase_order)
        
        if response:
            TdaWmsDuk.objects.using(db_name).filter(doctoerp=doctoerp, tipodocto='ORC', estadodetransferencia=5).update(estadodetransferencia=9)
            return {'doctoerp': doctoerp, 'lines': products_received}
        else:
            TdaWmsDuk.objects.using(db_name).filter(doctoerp=doctoerp, tipodocto='ORC', estadodetransferencia=5).update(estadodetransferencia=8)
            return {'doctoerp': doctoerp, 'error': 'The purchase order could not be updated in ContaPyme.', 'json': purchase_order}
    
    except Exception as e:
        TdaWmsDuk.objects.using(db_name).filter(doctoerp=doctoerp, tipodocto='ORC', estadodetransferencia__in=5).update(estadodetransferencia=8)
        raise ValueError(e)
        

    
