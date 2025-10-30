from wmsAdapterV2.models import TdaWmsDuk, TdaWmsEuk
from wmsAdapterV2.utils.convert_field_to_string import convert_to_string
from wmsAdapterV2.utils.get_next_lineaidpicking import get_next_lineaidpicking
from wmsAdapterV2.utils.get_time_by_timezone import get_time_by_timezone
from wmsAdapterV2.utils.validate_request_data import validate_request_data
from wmsAdapterV2.utils.verify_datetime_field import verify_datetime_field


def create_list_purchase_order(request, db_name, request_data=None):
    try:
        next_lineaidpicking = get_next_lineaidpicking(db_name, TdaWmsDuk)
        request_data = validate_request_data(request, list, request_data)
        time_record = get_time_by_timezone(db_name)
    except Exception as e:
        raise ValueError(e)

    # Initialize lists to hold valid and invalid data
    valid_orders = []
    order_details = []
    duk_keys = set()
    duk_keys_id = set()
    errors = []
    start_date = get_time_by_timezone(db_name, 'days', -15)

    euk_list = list(
        TdaWmsEuk.objects.using(db_name)
        .filter(fecharegistro__gte=start_date)
        .values("tipodocto", "doctoerp", "numdocumento")
    )
    euk_keys = {
        str(euk["tipodocto"])
        + " "
        + str(euk["doctoerp"])
        + " "
        + str(euk["numdocumento"])
        for euk in euk_list
    }

    duk_list = list(
        TdaWmsDuk.objects.using(db_name)
        .filter(fecharegistro__gte=start_date)
        .values(
            "tipodocto", "doctoerp", "numdocumento", "productoean", "lineaidpicking"
        )
    )

    for duk in duk_list:
        duk_keys.add(
            str(duk["tipodocto"])
            + " "
            + str(duk["doctoerp"])
            + " "
            + str(duk["numdocumento"])
            + " "
            + str(duk["productoean"])
        )
        duk_keys_id.add(
            str(duk["tipodocto"])
            + " "
            + str(duk["doctoerp"])
            + " "
            + str(duk["numdocumento"])
            + " "
            + str(duk["productoean"])
            + " "
            + str(duk["lineaidpicking"])
        )

    for rd in request_data:

        key_euk = (
            convert_to_string(rd["tipodocto"])
            + " "
            + convert_to_string(rd["doctoerp"])
            + " "
            + convert_to_string(rd["numdocumento"])
        )

        valid_euk = validate_euk_data(rd)
        if valid_euk:
            errors.append(f"error: {key_euk} {valid_euk}")
            continue

        euk_keys, valid_orders, errors = format_euk_object(
            rd, euk_keys, key_euk, valid_orders, errors, time_record
        )

        order_detail = rd["order_detail"]

        for od in order_detail:
            key_duk = key_euk + " " + convert_to_string(od["productoean"])

            valid_duk = validate_duk_data(od)
            if valid_duk:
                errors.append(f"error: {key_duk} {valid_duk}")
                continue

            if (
                "lineaidpicking" in od
                and od["lineaidpicking"]
                and od["lineaidpicking"] != ""
                and od["lineaidpicking"] != 0
            ):
                key_duk = key_duk + " " + convert_to_string(od["lineaidpicking"])
                duk_keys_id, order_details, errors, next_lineaidpicking = (
                    format_duk_object(
                        rd,
                        od,
                        duk_keys_id,
                        key_duk,
                        order_details,
                        errors,
                        next_lineaidpicking,
                        time_record
                    )
                )
            else:
                duk_keys, order_details, errors, next_lineaidpicking = (
                    format_duk_object(
                        rd,
                        od,
                        duk_keys,
                        key_duk,
                        order_details,
                        errors,
                        next_lineaidpicking,
                        time_record
                    )
                )

    created_orders, errors = create_euks(db_name, valid_orders, errors)

    created_order_details, errors = create_duks(db_name, order_details, errors)

    return created_orders, created_order_details, errors


def validate_euk_data(rd):
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


def validate_duk_data(od):
    if not isinstance(od, dict):
        return "Each register in the provided data should be a dictionary"

    if "productoean" not in od or not od["productoean"]:
        return "The productoean field is mandatory"

    if "qtypedido" not in od or not od["qtypedido"]:
        return "The qtypedido field is mandatory"

    return None


def format_euk_object(rd, euk_keys, key_euk, valid_orders, errors, time_record):
    euk_fields = [field.name for field in TdaWmsEuk._meta.get_fields()]

    if key_euk not in euk_keys:
        filtered_order = {key: value for key, value in rd.items() if key in euk_fields}

        filtered_order["fecharegistro"] = time_record
        filtered_order["f_ultima_actualizacion"] = time_record
        filtered_order["fecha"] = filtered_order.get("fecha") or time_record
        filtered_order["etd"] = filtered_order.get("etd") or None
        filtered_order["eta"] = filtered_order.get("eta") or None

        filtered_order["numdocumento"] = (
            filtered_order.get("numdocumento") or filtered_order["doctoerp"]
        )
        filtered_order["unido"] = filtered_order.get("unido") or str(
            filtered_order["doctoerp"]
        ) + "-" + str(filtered_order["numdocumento"])
        filtered_order["nit"] = filtered_order.get("nit") or filtered_order["item"]
        filtered_order["fecha"] = filtered_order.get("fecha") or time_record
        filtered_order["bodegaerp"] = (
            filtered_order.get("bodegaerp") or filtered_order["bodega"]
        )
        filtered_order["estadodocumentoubicacion"] = (
            filtered_order.get("estadodocumentoubicacion") or 1
        )

        filtered_order = verify_datetime_field(TdaWmsEuk, filtered_order)
        valid_orders.append(TdaWmsEuk(**filtered_order))

        euk_keys.add(key_euk)

    else:
        errors.append(f"error: Order {key_euk} record already exists")

    return euk_keys, valid_orders, errors


def format_duk_object(rd, od, duk_keys, key_duk, order_details, errors, next, time_record):
    duk_fields = [field.name for field in TdaWmsDuk._meta.get_fields()]

    if key_duk not in duk_keys:
        filtered_detail = {key: value for key, value in od.items() if key in duk_fields}

        if "id" in filtered_detail:
            del filtered_detail["id"]

        filtered_detail["referencia"] = (
            filtered_detail.get("referencia") or filtered_detail["productoean"]
        )
        filtered_detail["refpadre"] = (
            filtered_detail.get("refpadre") or filtered_detail["productoean"]
        )

        filtered_detail["tipodocto"] = rd["tipodocto"]
        filtered_detail["numdocumento"] = rd.get("numdocumento") or rd["doctoerp"]
        filtered_detail["doctoerp"] = rd["doctoerp"]
        filtered_detail["unido"] = rd.get("unido") or str(rd["doctoerp"]) + "-" + str(
            rd["numdocumento"]
        )

        filtered_detail["item"] = rd["item"]

        filtered_detail["bodega"] = rd["bodega"]

        filtered_detail["lineaidpicking"] = (
            filtered_detail.get("lineaidpicking") or next
        )

        filtered_detail["fecharegistro"] = time_record
        filtered_detail["f_ultima_actualizacion"] = time_record
        filtered_detail["fechaestadoalmdirigido"] = (
            filtered_detail.get("fechaestadoalmdirigido") or time_record
        )
        filtered_detail["etd"] = filtered_detail.get("etd") or None
        filtered_detail["eta"] = filtered_detail.get("eta") or None
        filtered_detail["estadodetransferencia"] = (
            filtered_detail.get("estadodetransferencia") or 0
        )

        filtered_detail["pesoreservado"] = filtered_detail.get("pesoreservado") or 0
        filtered_detail["pesoenpicking"] = filtered_detail.get("pesoenpicking") or 0
        filtered_detail["qtyenpicking"] = filtered_detail.get("qtyenpicking") or 0
        filtered_detail["caja_destino"] = filtered_detail.get("caja_destino") or None

        filtered_detail = verify_datetime_field(TdaWmsDuk, filtered_detail)
        print(filtered_detail)
        order_details.append(TdaWmsDuk(**filtered_detail))
        duk_keys.add(key_duk)

        if filtered_detail["lineaidpicking"] == next:
            next += 1
    else:
        errors.append(f"error: Detail {key_duk} record already exists")

    return duk_keys, order_details, errors, next


def create_euks(db_name, valid_orders, errors):
    created_orders = []
    bulk_size = 50

    for i in range(0, len(valid_orders), bulk_size):
        try:
            created_order_instances = TdaWmsEuk.objects.using(db_name).bulk_create(
                valid_orders[i : i + bulk_size]
            )
            for coi in created_order_instances:
                created_orders.append(
                    str(coi.tipodocto)
                    + " "
                    + str(coi.doctoerp)
                    + " "
                    + str(coi.numdocumento)
                )

        except Exception as e:
            for r in valid_orders[i : i + bulk_size]:
                try:
                    r_dict = r.__dict__
                    r_dict.pop("_state", None)
                    TdaWmsEuk.objects.using(db_name).create(**r_dict)
                    created_orders.append(
                        str(r.tipodocto)
                        + " "
                        + str(r.doctoerp)
                        + " "
                        + str(r.numdocumento)
                    )
                except Exception as e:
                    errors.append(
                        f"error: {str(r.tipodocto)} {str(r.doctoerp)} {str(r.numdocumento)} - {str(e)}"
                    )

    return created_orders, errors


def create_duks(db_name, valid_order_details, errors):
    created_order_details = []
    bulk_size = 50

    for i in range(0, len(valid_order_details), bulk_size):
        try:
            created_order_detail_instances = TdaWmsDuk.objects.using(
                db_name
            ).bulk_create(valid_order_details[i : i + bulk_size])
            for codi in created_order_detail_instances:
                created_order_details.append(
                    str(codi.tipodocto)
                    + " "
                    + str(codi.doctoerp)
                    + " "
                    + str(codi.numdocumento)
                    + " "
                    + str(codi.productoean)
                )

        except Exception as e:
            for r in valid_order_details[i : i + bulk_size]:
                try:
                    r_dict = r.__dict__
                    r_dict.pop("_state", None)
                    TdaWmsDuk.objects.using(db_name).create(**r_dict)
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
