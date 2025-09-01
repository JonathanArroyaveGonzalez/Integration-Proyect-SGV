from contapyme.functions.producto.read import read_items
from wmsAdapter.functions.TdaWmsArt.create import create_articles
from wmsAdapter.models import TdaWmsArt


def create_article(db_name, productoean):
    
    try:
        article = read_items(db_name, productoean)
        if not article:
            raise ValueError(f'Item {productoean} does not exist in ContaPyme')
    except Exception as e:
        raise ValueError(e)
    
    descripcion = article["nrecurso"]
    unidad = article["nunidad"]
    factor = article["qfactor"]
    observacion = article["sobservaciones"]

    if observacion and len(observacion) > 250:
        observacion = observacion[:249]

    newart = {
        "productoean": productoean,
        "descripcion": descripcion,
        "referencia": productoean,
        "inventariable": 1,
        "um1": unidad,
        "presentacion": "",
        "costo": None,
        "referenciamdc": productoean,
        "descripcioningles": descripcion,
        "item": productoean,
        "u_inv": unidad,
        "grupo": "",
        "subgrupo": "",
        "extension1": "",
        "extension2": "",
        "nuevoean": productoean,
        "qtyequivalente": None,
        "origencompra": None,
        "tipo": "",
        "factor": factor,
        "f120_tipo_item": "",
        "fecharegistro": None,
        "peso": None,
        "bodega": "01",
        "procedencia": "",
        "estadotransferencia": 0,
        "volumen": None,
        "proveedor": None,
        "preciounitario": None,
        "ingredientes": None,
        "instrucciones_de_uso": None,
        "u_inv_p": None,
        "observacion": observacion,
        "controla_status_calidad": None,
        "estado": 1
    }

    response = create_articles(None, db_name, newart)

    if response == 'created successfully':
        art = list(TdaWmsArt.objects.using(db_name).filter(productoean=productoean).values())
        return art[0]
    else:
        raise ValueError('Creating article error')