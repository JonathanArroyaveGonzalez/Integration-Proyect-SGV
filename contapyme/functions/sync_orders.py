from datetime import datetime, timedelta
import re

from contapyme.functions.compra.update import update_purchase_order
from contapyme.functions.factura.read import read_invoices
from contapyme.functions.operaciones.charging_document import create_charging_document
from contapyme.functions.operaciones.read import read_operations
from contapyme.functions.to_Wms.order import create_order
from contapyme.functions.to_Wms.purchase_order import create_purchase_order
from wmsAdapter.models import TdaWmsDpk, TdaWmsDuk, TdaWmsEpk, TdaWmsEuk


def sync_purchase_orders(db_name):
    snumsops = read_operations(db_name, "ORD5")
    contapyme_req_orders = []
    for ope in snumsops:
        snumsop = ope["snumsop"]
        if "ORC" in snumsop:
            contapyme_req_orders.append(snumsop)

    doctoerps = list(
        TdaWmsEuk.objects.using(db_name).values("doctoerp").order_by("-fecharegistro")
    )
    wms_req_orders = []
    for de in doctoerps:
        doctoerp = de["doctoerp"]
        if doctoerp not in wms_req_orders:
            wms_req_orders.append(doctoerp)

    req_orders_to_create = []
    for cpo in contapyme_req_orders:
        if cpo not in wms_req_orders:
            req_orders_to_create.append(cpo)

    # print(req_orders_to_create)
    responses = {}
    for sotc in req_orders_to_create:
        try:
            response = create_purchase_order(db_name, sotc)
            responses[sotc] = response
        except Exception as e:
            responses[sotc] = str(e)

    return responses


def sync_sales_orders(db_name, quantity=None):
    order_type = "ORD1"
    snumsops = read_operations(db_name, order_type, quantity)
    contapyme_req_orders = []
    for ope in snumsops:
        snumsop = ope["snumsop"]
        if "PED" in snumsop:
            contapyme_req_orders.append(snumsop)

    doctoerps = list(
        TdaWmsEpk.objects.using(db_name)
        .filter(tipodocto="FLT")
        .values("doctoerp")
        .order_by("-fecharegistro")
    )
    wms_req_orders = []
    for de in doctoerps:
        doctoerp = de["doctoerp"]
        if doctoerp not in wms_req_orders:
            wms_req_orders.append(doctoerp)

    req_orders_to_create = []
    for cpo in contapyme_req_orders:
        if cpo not in wms_req_orders:
            req_orders_to_create.append(cpo)

    # print(req_orders_to_create)
    responses = {}
    for sotc in req_orders_to_create:
        try:
            response = create_order(db_name, order_type, sotc)
            responses[sotc] = response
        except Exception as e:
            responses[sotc] = str(e)

    return responses


def sync_req_orders(db_name):
    order_type = "ORD3"
    snumsops = read_operations(db_name, order_type)
    contapyme_req_orders = []
    for ope in snumsops:
        snumsop = ope["snumsop"]
        if "REQ" in snumsop:
            contapyme_req_orders.append(snumsop)

    doctoerps = list(
        TdaWmsEpk.objects.using(db_name)
        .filter(tipodocto="REQ")
        .values("doctoerp")
        .order_by("-fecharegistro")
    )
    wms_req_orders = []
    for de in doctoerps:
        doctoerp = de["doctoerp"]
        if doctoerp not in wms_req_orders:
            wms_req_orders.append(doctoerp)

    req_orders_to_create = []
    for cpo in contapyme_req_orders:
        if cpo not in wms_req_orders:
            req_orders_to_create.append(cpo)

    # print(req_orders_to_create)
    responses = {}
    for rotc in req_orders_to_create:
        try:
            response = create_order(db_name, order_type, rotc)
            responses[rotc] = response
        except Exception as e:
            responses[rotc] = str(e)

    return responses


def return_ddc_orders(db_name):
    date_now = datetime.now().date()
    date_yesterday = date_now - timedelta(days=1)

    try:
        TdaWmsDpk.objects.using(db_name).filter(
            tipodocto="FLT",
            estadodetransferencia=5,
            fecharegistro__date__range=(date_yesterday, date_now),
        ).update(estadodetransferencia=3)

        wms_dpk = (
            TdaWmsDpk.objects.using(db_name)
            .filter(
                tipodocto="FLT",
                estadodetransferencia__in=[3, 8],
                fecharegistro__date__range=(date_yesterday, date_now),
            )
            .all()
        )
    except Exception as e:
        return str(e)

    orders_to_return = []

    for d in wms_dpk:
        doctoerp = d.doctoerp
        if doctoerp not in orders_to_return:
            if int(d.estadodetransferencia) == 3 or int(d.estadodetransferencia) == 8:

                wms_dpk_9 = list(
                    TdaWmsDpk.objects.using(db_name)
                    .filter(doctoerp=doctoerp, tipodocto="FLT", estadodetransferencia=9, lineaidpicking=d.lineaidpicking, productoean=d.productoean)
                    .values("productoean")
                )

                if len(wms_dpk_9) > 0:
                    TdaWmsDpk.objects.using(db_name).filter(
                        doctoerp=doctoerp,
                        tipodocto="FLT",
                        estadodetransferencia__in=[3, 8],
                        lineaidpicking=d.lineaidpicking, 
                        productoean=d.productoean
                    ).update(estadodetransferencia=-8)
                else:
                    TdaWmsDpk.objects.using(db_name).filter(
                        doctoerp=doctoerp,
                        tipodocto="FLT",
                        estadodetransferencia__in=[3, 8]
                    ).update(estadodetransferencia=5)
                    orders_to_return.append(doctoerp)

    # print(f'Pending ddc: {orders_to_return}')
    responses = {}
    if len(orders_to_return) > 0:
        for order in orders_to_return:
            try:
                response = create_charging_document(db_name, order)
                responses[order] = response
            except Exception as e:
                responses[order] = str(e)
                TdaWmsDpk.objects.using(db_name).filter(
                    tipodocto="FLT", doctoerp=order, estadodetransferencia=5
                ).update(estadodetransferencia=8)

    return responses


def return_purchase_orders(db_name):
    date_now = datetime.now().date()
    date_yesterday = date_now - timedelta(days=1)

    try:
        wms_duk = (
            TdaWmsDuk.objects.using(db_name)
            .filter(
                tipodocto="ORC",
                estadodetransferencia__in=[3, 8],
                fecharegistro__date__range=(date_yesterday, date_now),
            )
            .all()
        )
    except Exception as e:
        return str(e)

    orders_to_return = []

    for d in wms_duk:
        doctoerp = d.doctoerp
        if doctoerp not in orders_to_return:
            if int(d.estadodetransferencia) == 3 or int(d.estadodetransferencia) == 8:

                wms_dpk_9 = list(
                    TdaWmsDuk.objects.using(db_name)
                    .filter(doctoerp=doctoerp, tipodocto="ORC", estadodetransferencia=9)
                    .values("productoean")
                )
                if len(wms_dpk_9) > 0:
                    TdaWmsDuk.objects.using(db_name).filter(
                        doctoerp=doctoerp,
                        tipodocto="ORC",
                        estadodetransferencia__in=[3, 8],
                    ).update(estadodetransferencia=-8)
                else:
                    if doctoerp not in orders_to_return:
                        orders_to_return.append(doctoerp)

    # print(f'Pending ddc: {orders_to_return}')
    responses = {}
    if len(orders_to_return) > 0:
        for order in orders_to_return:
            try:
                response = update_purchase_order(db_name, order)
                responses[order] = response
            except Exception as e:
                responses[order] = str(e)
                TdaWmsDuk.objects.using(db_name).filter(
                    tipodocto="ORC", doctoerp=order, estadodetransferencia=5
                ).update(estadodetransferencia=8)

    return responses
