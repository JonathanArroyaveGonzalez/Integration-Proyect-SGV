from wmsAdapterV2.models import TdaWmsEpn, TdaWmsDpn
from wmsAdapterV2.utils.convert_field_to_string import convert_to_string
from wmsAdapterV2.utils.get_next_lineaidpicking import get_next_lineaidop, get_sequence
from wmsAdapterV2.utils.get_time_by_timezone import get_time_by_timezone
from wmsAdapterV2.utils.validate_request_data import validate_request_data
from wmsAdapterV2.utils.verify_datetime_field import verify_datetime_field


def create_list_production_order(request, db_name, request_data=None):

    try:
        next_lineaidop = get_next_lineaidop(db_name)
        next_picking = get_sequence("secuencia_picking", db_name)
        request_data = validate_request_data(request, list, request_data)
        time_record = get_time_by_timezone(db_name)
    except Exception as e:
        raise ValueError(e)

    # Initialize lists to hold valid and invalid data
    valid_orders = []
    order_details = []
    pickings = {}
    dpn_keys = set()
    dpn_keys_id = set()
    errors = []
    start_date = get_time_by_timezone(db_name, 'days', -15)

    epn_list = list(
        TdaWmsEpn.objects.using(db_name)
        .filter(fecharegistro__gte=start_date)
        .values("tipodocto", "doctoerp", "numpedido", "productoean", "picking")
    )
    epn_keys = {
        str(epn["tipodocto"])
        + " "
        + str(epn["doctoerp"])
        + " "
        + str(epn["numpedido"])
        + " "
        + str(epn["productoean"])
        for epn in epn_list
    }

    for e in epn_list:
        pickings[
            str(e["tipodocto"])
            + str(e["doctoerp"])
            + str(e["numpedido"])
            + str(e["productoean"])
        ] = e["picking"]

    dpn_list = list(
        TdaWmsDpn.objects.using(db_name)
        .filter(fecharegistro__gte=start_date)
        .values(
            "tipodocto", "doctoerp", "numpedido", "productoean", "picking", "lineaidop"
        )
    )
    for dpn in dpn_list:
        for epn in epn_list:
            if (
                dpn["picking"] == epn["picking"]
                and dpn["tipodocto"] == epn["tipodocto"]
                and dpn["doctoerp"] == epn["doctoerp"]
                and dpn["numpedido"] == epn["numpedido"]
            ):

                dpn_keys.add(
                    str(dpn["tipodocto"])
                    + " "
                    + str(dpn["doctoerp"])
                    + " "
                    + str(dpn["numpedido"])
                    + " "
                    + str(epn["productoean"])
                    + " "
                    + str(dpn["productoean"])
                )
                dpn_keys_id.add(
                    str(dpn["tipodocto"])
                    + " "
                    + str(dpn["doctoerp"])
                    + " "
                    + str(dpn["numpedido"])
                    + " "
                    + str(epn["productoean"])
                    + " "
                    + str(dpn["productoean"])
                    + " "
                    + str(dpn["lineaidop"])
                )

    for rd in request_data:

        key_epn = (
            convert_to_string(rd["tipodocto"])
            + " "
            + convert_to_string(rd["doctoerp"])
            + " "
            + convert_to_string(rd["numpedido"])
            + " "
            + convert_to_string(rd["productoean"])
        )

        valid_epn = validate_epn_data(rd)
        if valid_epn:
            errors.append(f"error: {key_epn} {valid_epn}")
            continue

        epn_keys, valid_orders, errors = format_epn_object(
            rd, epn_keys, key_epn, valid_orders, errors, next_picking, time_record
        )

        if "order_detail" in rd:
            order_detail = rd["order_detail"]

            for od in order_detail:
                key_dpn = key_epn + " " + convert_to_string(od["productoean"])

                valid_dpn = validate_dpn_data(od)
                if valid_dpn:
                    errors.append(f"error: {key_dpn} {valid_dpn}")
                    continue

                if (
                    "lineaidop" in od
                    and od["lineaidop"]
                    and od["lineaidop"] != ""
                    and od["lineaidop"] != 0
                ):
                    key_dpn = key_dpn + " " + convert_to_string(od["lineaidop"])
                    dpn_keys_id, order_details, errors, next_lineaidop = (
                        format_dpn_object(
                            rd,
                            od,
                            dpn_keys_id,
                            key_dpn,
                            order_details,
                            errors,
                            next_lineaidop,
                            time_record,
                        )
                    )
                else:
                    dpn_keys, order_details, errors, next_lineaidop = format_dpn_object(
                        rd,
                        od,
                        dpn_keys,
                        key_dpn,
                        order_details,
                        errors,
                        next_lineaidop,
                        time_record,
                    )

        next_picking = get_sequence("secuencia_picking", db_name)

    created_orders, pickings, errors = create_epns(
        db_name, valid_orders, errors, pickings
    )

    created_order_details, errors = create_dpns(
        db_name, order_details, pickings, errors
    )

    return created_orders, created_order_details, errors


def validate_epn_data(rd):
    if not isinstance(rd, dict):
        return "Each register in the provided data should be a dictionary"

    if "doctoerp" not in rd or not rd["doctoerp"]:
        return "The doctoerp field is mandatory"

    if "tipodocto" not in rd or not rd["tipodocto"]:
        return "The tipodocto field is mandatory"

    if "item" not in rd or not rd["item"]:
        return "The item field is mandatory"

    if "bodega" not in rd or not rd["bodega"]:
        return "The bodega field is mandatory"

    if "productoean" not in rd or not rd["productoean"]:
        return "The productoean field is mandatory"

    if "cantidad" not in rd or not rd["cantidad"]:
        return "The cantidad field is mandatory"

    return None


def format_epn_object(rd, epn_keys, key_epn, valid_orders, errors, next, time_record):
    epn_fields = [field.name for field in TdaWmsEpn._meta.get_fields()]

    if key_epn not in epn_keys:
        filtered_order = {key: value for key, value in rd.items() if key in epn_fields}

        filtered_order["picking"] = next

        filtered_order["fecharegistro"] = time_record
        filtered_order["f_ultima_actualizacion"] = time_record
        filtered_order["fechapedido"] = filtered_order.get("fechapedido") or time_record
        filtered_order["fechatransferencia"] = (
            filtered_order.get("fechatransferencia") or None
        )
        filtered_order["fechaplaneacion"] = (
            filtered_order.get("fechaplaneacion") or time_record
        )
        filtered_order["fechavence"] = filtered_order.get("fechavence") or None

        filtered_order["cantidad"] = float(filtered_order["cantidad"])

        filtered_order["numpedido"] = (
            filtered_order.get("numpedido") or filtered_order["doctoerp"]
        )

        filtered_order["referencia"] = (
            filtered_order.get("referencia") or filtered_order["productoean"]
        )
        filtered_order["item_art"] = (
            filtered_order.get("item_art") or filtered_order["productoean"]
        )

        filtered_order["bodegaerp"] = (
            filtered_order.get("bodegaerp") or filtered_order["bodega"]
        )

        filtered_order["cantidadempaque"] = (
            filtered_order.get("cantidadempaque") or filtered_order["cantidad"]
        )

        filtered_order["estadoerp"] = filtered_order.get("estadoerp") or 1

        filtered_order = verify_datetime_field(TdaWmsEpn, filtered_order)

        valid_orders.append(TdaWmsEpn(**filtered_order))

        epn_keys.add(key_epn)

    else:
        errors.append(f"error: Order record {key_epn} already exists")

    return epn_keys, valid_orders, errors


def validate_dpn_data(od):
    if not isinstance(od, dict):
        return "Each register in the provided data should be a dictionary"

    if "productoean" not in od or not od["productoean"]:
        return "The productoean field is mandatory"

    if "qtypedido" not in od or not od["qtypedido"]:
        return "The qtypedido field is mandatory"

    return None


def format_dpn_object(rd, od, dpn_keys, key_dpn, order_details, errors, next, time_record):
    dpn_fields = [field.name for field in TdaWmsDpn._meta.get_fields()]

    if key_dpn not in dpn_keys:
        filtered_detail = {key: value for key, value in od.items() if key in dpn_fields}

        filtered_detail["lineaidop"] = filtered_detail.get("lineaidop") or next
        filtered_detail["ref"] = filtered_detail.get("ref") or filtered_detail.get(
            "productoean"
        )

        filtered_detail["qtyreservado"] = (
            filtered_detail.get("qtyreservado") or filtered_detail["qtypedido"]
        )

        filtered_detail["tipodocto"] = rd["tipodocto"]
        filtered_detail["doctoerp"] = rd["doctoerp"]
        filtered_detail["numpedido"] = rd.get("numpedido") or rd["doctoerp"]
        filtered_detail["bodega"] = rd["bodega"]

        filtered_detail["fecharegistro"] = time_record
        filtered_detail["f_ultima_actualizacion"] = time_record
        filtered_detail["fechatransferencia"] = rd.get("fechatransferencia") or None

        filtered_detail["picking"] = None
        filtered_detail["estadotransferencia"] = 0

        filtered_detail["productoean_epn"] = rd["productoean"]

        filtered_detail = verify_datetime_field(TdaWmsDpn, filtered_detail)
        order_details.append(filtered_detail)
        dpn_keys.add(key_dpn)
        if filtered_detail["lineaidop"] == next:
            next += 1
    else:
        errors.append(f"error: Detail {key_dpn} record already exists")

    return dpn_keys, order_details, errors, next


def create_epns(db_name, valid_orders, errors, pickings):
    created_orders = []
    bulk_size = 50

    for i in range(0, len(valid_orders), bulk_size):
        try:
            created_order_instances = TdaWmsEpn.objects.using(db_name).bulk_create(
                valid_orders[i : i + bulk_size]
            )
            for coi in created_order_instances:
                created_orders.append(
                    str(coi.tipodocto)
                    + " "
                    + str(coi.doctoerp)
                    + " "
                    + str(coi.numpedido)
                    + " "
                    + str(coi.productoean)
                )
                pickings[
                    str(coi.tipodocto)
                    + str(coi.doctoerp)
                    + str(coi.numpedido)
                    + str(coi.productoean)
                ] = coi.picking

        except Exception as e:
            for r in valid_orders[i : i + bulk_size]:
                try:
                    r_dict = r.__dict__
                    r_dict.pop("_state", None)
                    TdaWmsEpn.objects.using(db_name).create(**r_dict)
                    created_orders.append(
                        str(r.tipodocto)
                        + " "
                        + str(r.doctoerp)
                        + " "
                        + str(r.numpedido)
                        + " "
                        + str(r.productoean)
                    )
                    pickings[
                        str(r.tipodocto)
                        + str(r.doctoerp)
                        + str(r.numpedido)
                        + str(r.productoean)
                    ] = r.picking
                except Exception as e:
                    errors.append(
                        f"error: {str(r.tipodocto)} {str(r.doctoerp)} {str(r.numpedido)} {str(r.productoean)} - {str(e)}"
                    )

    return created_orders, pickings, errors


def create_dpns(db_name, order_details, pickings, errors):
    valid_order_details = []
    created_order_details = []
    bulk_size = 50

    for detail in order_details:
        detail_key = (
            str(detail["tipodocto"])
            + str(detail["doctoerp"])
            + str(detail["numpedido"])
            + str(detail["productoean_epn"])
        )
        if detail_key in pickings:
            detail["picking"] = pickings[detail_key]
            del detail["productoean_epn"]
            valid_order_details.append(TdaWmsDpn(**detail))

    for i in range(0, len(valid_order_details), bulk_size):
        try:
            created_order_detail_instances = TdaWmsDpn.objects.using(
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
                    + " "
                    + str(codi.picking)
                )

        except Exception as e:
            for r in valid_order_details[i : i + bulk_size]:
                try:
                    r_dict = r.__dict__
                    r_dict.pop("_state", None)
                    TdaWmsDpn.objects.using(db_name).create(**r_dict)
                    created_order_details.append(
                        str(r.tipodocto)
                        + " "
                        + str(r.doctoerp)
                        + " "
                        + str(r.numpedido)
                        + " "
                        + str(r.productoean)
                        + " "
                        + str(r.picking)
                    )
                except Exception as e:
                    errors.append(
                        f"error: {str(r.picking)} {str(r.productoean)} - {str(e)}"
                    )

    return created_order_details, errors
