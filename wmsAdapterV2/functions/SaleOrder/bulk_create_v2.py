import json

from wmsAdapterV2.models import TdaWmsEpk, TdaWmsDpk
from wmsAdapterV2.utils.convert_field_to_string import convert_to_string
from wmsAdapterV2.utils.get_next_lineaidpicking import (
    get_next_lineaidpicking,
    get_sequence,
)
from wmsAdapterV2.utils.get_non_existent_records import get_non_existent_records
from wmsAdapterV2.utils.get_time_by_timezone import get_time_by_timezone
from wmsAdapterV2.utils.serializer import serializer
from wmsAdapterV2.utils.validate_request_data import validate_request_data
from wmsAdapterV2.utils.verify_datetime_field import verify_datetime_field


def create_list_sale_order_without_orm_validation(request, db_name, request_data=None):
    try:
        request_data = validate_request_data(request, list, request_data)
        time_record = get_time_by_timezone(db_name)
    except Exception as e:
        raise ValueError(e)

    # Initialize lists to hold valid and invalid data
    epk_keys = []
    dpk_keys = []
    dpk_keys_id = []
    errors = []
    formatted_orders = []
    formatted_details = []
    orders_to_create = []
    details_to_create = []
    pickings = {}
    valid_orders = []
    valid_details = []
    created_orders = []
    created_details = []

    for rd in request_data:
        key_epk = (
            convert_to_string(rd["tipodocto"])
            + " "
            + convert_to_string(rd["doctoerp"])
            + " "
            + convert_to_string(rd["numpedido"])
        )

        valid_epk = validate_epk_data(rd)
        if valid_epk:
            errors.append(f"error: {key_epk} {valid_epk}")
            continue

        epk_keys, formatted_orders, errors = format_epk_object(
            rd, epk_keys, key_epk, formatted_orders, errors, time_record
        )

        order_detail = rd["order_detail"]

        for od in order_detail:

            key_dpk = key_epk + " " + convert_to_string(od["productoean"])

            valid_dpk = validate_dpk_data(od)
            if valid_dpk:
                errors.append(f"error: {key_dpk} {valid_dpk}")
                continue

            if (
                "lineaidpicking" in od
                and od["lineaidpicking"]
                and od["lineaidpicking"] != ""
                and od["lineaidpicking"] != 0
            ):
                key_dpk = key_dpk + " " + convert_to_string(od["lineaidpicking"])
                dpk_keys_id, formatted_details, errors = format_dpk_object(
                    rd, od, dpk_keys_id, key_dpk, formatted_details, errors, time_record
                )
            else:
                dpk_keys, formatted_details, errors = format_dpk_object(
                    rd, od, dpk_keys, key_dpk, formatted_details, errors, time_record
                )

    try:
        orders_string = json.dumps(formatted_orders, default=serializer, indent=4)
    except Exception as e:
        errors.append(f"error: formatting the sales order dictionary - {e}")
        return [], [], errors

    try:
        details_string = json.dumps(formatted_details, default=serializer, indent=4)
    except Exception as e:
        errors.append(f"error: formatting the sales order detail dictionary - {e}")
        return [], [], errors

    try:
        orders_to_create = get_non_existent_records(db_name, "EPK", orders_string)
        details_to_create = get_non_existent_records(db_name, "DPK", details_string)
    except Exception as e:
        errors.append(f"error: Searching for existing records - {e}")
        return [], [], errors

    try:
        valid_orders, pickings, errors = clean_epk_object(
            db_name, orders_to_create, pickings, errors
        )
        valid_details, errors = clean_dpk_object(
            db_name, details_to_create, pickings, errors
        )
    except Exception as e:
        errors.append(f"error: Creating instances of the table type - {e}")
        return [], [], errors

    try:
        created_orders, errors = create_epks(db_name, valid_orders, errors)
        created_details, errors = create_dpks(db_name, valid_details, errors)
    except Exception as e:
        errors.append(f"error: Creating records - {e}")
        return created_orders, created_details, errors

    return created_orders, created_details, errors


def validate_epk_data(rd):
    if not isinstance(rd, dict):
        return "Each register in the provided data should be a dictionary"

    if "order_detail" not in rd or not rd["order_detail"]:
        return "The order does not include product details"

    if not isinstance(rd["order_detail"], list):
        return "order_detail should be a list."

    if "doctoerp" not in rd or not rd["doctoerp"]:
        return "The doctoerp field is mandatory"

    if "tipodocto" not in rd or not rd["tipodocto"]:
        return "The tipodocto field is mandatory"

    if "item" not in rd or not rd["item"]:
        return "The item field is mandatory"

    if "bodega" not in rd or not rd["bodega"]:
        return "The bodega field is mandatory"

    return None


def validate_dpk_data(od):
    if not isinstance(od, dict):
        return "Each register in the provided data should be a dictionary"

    if "productoean" not in od or not od["productoean"]:
        return "The productoean field is mandatory"

    if "descripcion" not in od or not od["descripcion"]:
        return "The descripcion field is mandatory"

    if "qtypedido" not in od or not od["qtypedido"]:
        return "The qtypedido field is mandatory"

    return None


def format_epk_object(rd, epk_keys, key_epk, formatted_orders, errors, time_record):
    epk_fields = [field.name for field in TdaWmsEpk._meta.get_fields()]

    if key_epk not in epk_keys:
        try:
            filtered_order = {
                key: value for key, value in rd.items() if key in epk_fields
            }

            if "id" in filtered_order:
                del filtered_order["id"]

            filtered_order["fecharegistro"] = time_record
            filtered_order["f_ultima_actualizacion"] = time_record

            filtered_order["fechaplaneacion"] = (
                filtered_order.get("fechaplaneacion") or time_record
            )
            filtered_order["fechtrans"] = filtered_order.get("fechtrans") or None
            filtered_order["f_pedido"] = filtered_order.get("f_pedido") or time_record
            filtered_order["fpedido"] = filtered_order.get("fpedido") or time_record

            filtered_order["numpedido"] = (
                filtered_order.get("numpedido") or filtered_order["doctoerp"]
            )
            filtered_order["nit"] = filtered_order.get("nit") or filtered_order["item"]

            filtered_order["bodegaerp"] = (
                filtered_order.get("bodegaerp") or filtered_order["bodega"]
            )
            filtered_order["centrooperacion"] = (
                filtered_order.get("centrooperacion") or filtered_order["bodega"]
            )

            filtered_order["estadoerp"] = filtered_order.get("estadoerp") or 1
            filtered_order["estadopicking"] = 0
            filtered_order["picking"] = None

            formatted_orders.append(filtered_order)
            epk_keys.append(key_epk)

        except Exception as e:
            errors.append(f"error: Order {key_epk} - {str(e)}")
    else:
        errors.append(f"error: Order {key_epk} record already exists in the request")

    return epk_keys, formatted_orders, errors


def format_dpk_object(
    rd, od, dpk_keys, key_dpk, formatted_details, errors, time_record
):
    dpk_fields = [field.name for field in TdaWmsDpk._meta.get_fields()]

    if key_dpk not in dpk_keys:
        try:
            filtered_detail = {
                key: value for key, value in od.items() if key in dpk_fields
            }

            if "id" in filtered_detail:
                del filtered_detail["id"]

            filtered_detail["lineaidpicking"] = (
                filtered_detail.get("lineaidpicking") or 0
            )
            filtered_detail["referencia"] = filtered_detail.get(
                "referencia"
            ) or filtered_detail.get("productoean")
            filtered_detail["refpadre"] = (
                filtered_detail.get("refpadre") or filtered_detail["productoean"]
            )
            filtered_detail["descripcionco"] = (
                filtered_detail.get("descripcionco") or filtered_detail["descripcion"][:80]
            )

            filtered_detail["qtyreservado"] = (
                filtered_detail.get("qtyreservado") or filtered_detail["qtypedido"]
            )

            filtered_detail["tipodocto"] = rd["tipodocto"]
            filtered_detail["doctoerp"] = rd["doctoerp"]
            filtered_detail["numpedido"] = rd.get("numpedido") or rd["doctoerp"]
            filtered_detail["item"] = rd["item"]
            filtered_detail["bodega"] = rd["bodega"]

            filtered_detail["idco"] = filtered_detail.get("idco") or rd["bodega"]

            filtered_detail["fecharegistro"] = time_record
            filtered_detail["f_ultima_actualizacion"] = time_record
            filtered_detail["picking"] = None
            filtered_detail["estadodetransferencia"] = 0
            filtered_detail["qtyenpicking"] = 0
            filtered_detail["field_qtypedidabase"] = filtered_detail["qtyreservado"]

            filtered_detail["descripcionco"] = filtered_detail["descripcionco"][:80]

            formatted_details.append(filtered_detail)
            dpk_keys.append(key_dpk)

        except Exception as e:
            errors.append(f"error: Detail {key_dpk} - {str(e)}")

    else:
        errors.append(f"error: Detail {key_dpk} record already exists in the request")

    return dpk_keys, formatted_details, errors


def clean_epk_object(db_name, orders_to_create, pickings, errors):
    valid_orders = []
    for order in orders_to_create:
        try:
            next_picking = get_sequence("secuencia_picking", db_name)
            order["picking"] = next_picking
            order = verify_datetime_field(TdaWmsEpk, order)

            pickings[
                f'{order["tipodocto"]} {order["doctoerp"]} {order["numpedido"]}'
            ] = next_picking
            valid_orders.append(TdaWmsEpk(**order))
        except Exception as e:
            errors.append(
                f'error: Order {order["tipodocto"]} {order["doctoerp"]} {order["numpedido"]} - {str(e)}'
            )

    return valid_orders, pickings, errors


def clean_dpk_object(db_name, details_to_create, pickings, errors):
    valid_details = []
    next_lineaidpicking = get_next_lineaidpicking(db_name, TdaWmsDpk)

    for det in details_to_create:
        try:
            key_epk = f'{det["tipodocto"]} {det["doctoerp"]} {det["numpedido"]}'

            if key_epk in pickings:
                det["picking"] = pickings[key_epk]
            else:
                try:
                    picking = (
                        TdaWmsEpk.objects.using(db_name)
                        .filter(
                            tipodocto=det["tipodocto"],
                            doctoerp=det["doctoerp"],
                            numpedido=det["numpedido"],
                        )[0]
                        .picking
                    )
                    det["picking"] = picking
                    pickings[key_epk] = picking
                except Exception as e:
                    errors.append(f"error: {key_epk} order header not found")
                    continue

            if det["lineaidpicking"] == 0:
                det["lineaidpicking"] = next_lineaidpicking
                next_lineaidpicking += 1

            det = verify_datetime_field(TdaWmsDpk, det)

            valid_details.append(TdaWmsDpk(**det))
        except Exception as e:
            errors.append(
                f'error: Detail {det["tipodocto"]} {det["doctoerp"]} {det["numpedido"]} {det["productoean"]} {det["lineaidpicking"]} - {str(e)}'
            )

    return valid_details, errors


def create_epks(db_name, valid_orders, errors):
    created_orders = []
    bulk_size = 50

    for i in range(0, len(valid_orders), bulk_size):
        try:
            created_order_instances = TdaWmsEpk.objects.using(db_name).bulk_create(
                valid_orders[i : i + bulk_size]
            )
            for coi in created_order_instances:
                created_orders.append(
                    str(coi.tipodocto)
                    + " "
                    + str(coi.doctoerp)
                    + " "
                    + str(coi.numpedido)
                )

        except Exception as e:
            for r in valid_orders[i : i + bulk_size]:
                try:
                    r_dict = r.__dict__
                    r_dict.pop("_state", None)
                    TdaWmsEpk.objects.using(db_name).create(**r_dict)
                    created_orders.append(
                        str(r.tipodocto)
                        + " "
                        + str(r.doctoerp)
                        + " "
                        + str(r.numpedido)
                    )
                except Exception as e:
                    errors.append(
                        f"error: {str(r.tipodocto)} {str(r.doctoerp)} {str(r.numpedido)} - {str(e)}"
                    )

    return created_orders, errors


def create_dpks(db_name, valid_order_details, errors):
    created_order_details = []
    bulk_size = 50

    for i in range(0, len(valid_order_details), bulk_size):
        try:
            created_order_detail_instances = TdaWmsDpk.objects.using(
                db_name
            ).bulk_create(valid_order_details[i : i + bulk_size])
            for codi in created_order_detail_instances:
                created_order_details.append(
                    str(codi.tipodocto)
                    + " "
                    + str(codi.doctoerp)
                    + " "
                    + str(codi.numpedido)
                    + " "
                    + str(codi.productoean)
                )

        except Exception as e:
            for r in valid_order_details[i : i + bulk_size]:
                try:
                    r_dict = r.__dict__
                    r_dict.pop("_state", None)
                    TdaWmsDpk.objects.using(db_name).create(**r_dict)
                    created_order_details.append(
                        str(r.productoean)
                        + " "
                        + str(r.referencia)
                        + " "
                        + str(r.descripcion)
                    )
                except Exception as e:
                    errors.append(
                        f"error: {str(r.doctoerp)} {str(r.productoean)} - {str(e)}"
                    )

    return created_order_details, errors
