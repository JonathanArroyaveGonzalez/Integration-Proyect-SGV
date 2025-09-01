from django.utils import timezone

from wmsAdapter.functions.TdaWmsDpk.create import create_dpk
from wmsAdapter.models import TdaWmsDpk

def create_detail_order(db_name, epk, producto, art):
    d = list(TdaWmsDpk.objects.using(db_name).order_by("-fecharegistro").values()[:1])[0]
    lineaidpicking = d["lineaidpicking"]
    productoean = art["productoean"]
    descripcion = art["descripcion"]
    observacion = art["observacion"]

    qrecurso = producto["qrecurso"]
    mprecio = producto["mprecio"]
    mvrtotal = producto["mvrtotal"]

    picking = epk["picking"]
    tipodocto = epk["tipodocto"]
    numpedido = epk["numpedido"]
    doctoerp = epk["doctoerp"]
    fecharegistro = epk["fecharegistro"]
    item = epk["item"]
    fecha_actual = timezone.now().isoformat()

    newdpk = {
        "referencia": productoean,
        "refpadre": productoean,
        "descripcion": descripcion,
        "qtypedido": qrecurso,
        "qtyreservado": qrecurso,
        "productoean": productoean,
        "picking": picking,
        "lineaidpicking": int(lineaidpicking) + 1,
        "costo": mvrtotal,
        "bodega": "01",
        "tipodocto": tipodocto,
        "doctoerp": doctoerp,
        "qtyenpicking": 0,
        "estadodetransferencia": 0,
        "fecharegistro": fecharegistro,
        "ubicacion_plan": None,
        "fechatransferencia": None,
        "clasifart": None,
        "serial": None,
        "item": item,
        "idco": None,
        "qtyremisionado": None,
        "qtyfacturado": None,
        "preciounitario": mprecio,
        "notasitem": observacion,
        "descripcionco": descripcion,
        "factor": 0,
        "numpedido": numpedido,
        "pedproveedor": "NA",
        "loteproveedor": "NA",
        "field_qtypedidabase": None,
        "f_ultima_actualizacion": fecha_actual
    }

    response = create_dpk(None, db_name, newdpk)
    if response == 'created successfully':
        dpk = list(TdaWmsDpk.objects.using(db_name).filter(doctoerp=doctoerp, productoean=productoean).values())
        return dpk[0]
    else:
        raise ValueError('Creating detail order error')