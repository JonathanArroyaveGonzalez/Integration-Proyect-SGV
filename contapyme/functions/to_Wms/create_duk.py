from django.utils import timezone

from wmsAdapter.functions.TdaWmsDuk.create import create_duk
from wmsAdapter.models import TdaWmsDuk


def create_detail_purchase_order(db_name, euk, producto, art):
    d = list(TdaWmsDuk.objects.using(db_name).order_by("-fecharegistro").values()[:1])[0]
    lineaidpicking = int(d["lineaidpicking"]) + 1

    cantidad = producto["qrecurso"]
    valor_total = producto["mvrtotal"]
    
    productoean = art["productoean"]
    descripcion = art["descripcion"]

    item = euk["item"]
    fecharegistro = euk["fecharegistro"]
    tipodocto = euk["tipodocto"]
    doctoerp = euk["doctoerp"]
    numdocumento = euk["numdocumento"]
    unido = euk["unido"]

    fecha_actual = timezone.now().isoformat()

    newduk = {
        "referencia": productoean,
        "refpadre": productoean,
        "descripcion": descripcion,
        "qtypedido": cantidad,
        "qtyreservado": cantidad,
        "productoean": productoean,
        "lineaidpicking": lineaidpicking,
        "costo": valor_total,
        "bodega": "01",
        "tipodocto": tipodocto,
        "doctoerp": doctoerp,
        "qtyenpicking": 0,
        "estadodetransferencia": 0,
        "fecharegistro": fecharegistro,
        "ubicacion": None,
        "numdocumento": numdocumento,
        "item": item,
        "ubicacion_sale": None,
        "origen": None,
        "caja_destino": None,
        "fechaestadoalmdirigido": None,
        "unido": unido,
        "etd": None,
        "eta": None,
        "pedproveedor": None,
        "ord_no": None,
        "loteproveedor": None,
        "codigoarticulo": None,
        "cantidadempaque": None,
        "f_ultima_actualizacion": fecha_actual
    }

    response = create_duk(None, db_name, newduk)
    if response == 'created successfully':
        duk = list(TdaWmsDuk.objects.using(db_name).filter(doctoerp=doctoerp, productoean=productoean).values())
        return duk[0]
    else:
        raise ValueError('Creating detail purchase order error')