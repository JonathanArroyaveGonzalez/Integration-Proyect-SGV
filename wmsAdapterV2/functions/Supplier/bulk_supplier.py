from wmsAdapterV2.models import TdaWmsPrv
from wmsAdapterV2.utils.convert_field_to_string import convert_to_string
from wmsAdapterV2.utils.get_time_by_timezone import get_time_by_timezone
from wmsAdapterV2.utils.validate_request_data import validate_request_data


def create_list_suppliers(request, db_name, request_data=None):
    # Convert request data to a list of dictionaries
    try:
        request_data = validate_request_data(request, list, request_data)
        time_record = get_time_by_timezone(db_name)
    except Exception as e:
        raise ValueError(e)

    # Initialize lists to hold valid and invalid data
    valid_suppliers = []
    errors = []

    # Check if the record already exists
    prv_keys = list(TdaWmsPrv.objects.using(db_name).values_list("item", flat=True))

    for rd in request_data:
        prv_key = convert_to_string(rd["item"])

        valid_prv = validate_prv_data(rd)
        if valid_prv:
            errors.append(f"error: {prv_key} {valid_prv}")
            continue

        prv_keys, valid_suppliers, errors = format_prv_object(
            rd, prv_keys, prv_key, valid_suppliers, errors, time_record
        )

    created_suppliers, errors = create_prvs(db_name, valid_suppliers, errors)
    return created_suppliers, errors


def validate_prv_data(rd):
    if not isinstance(rd, dict):
        return "Each register in the provided data should be a dictionary"

    if "item" not in rd or not rd["item"]:
        return "The item field is mandatory"

    if "nombrecliente" not in rd or not rd["nombrecliente"]:
        return "The nombrecliente field is mandatory"

    return None


def format_prv_object(rd, prv_keys, key_prv, valid_suppliers, errors, time_record):
    prv_fields = [field.name for field in TdaWmsPrv._meta.get_fields()]

    if key_prv not in prv_keys:
        filtered_supplier = {
            key: value for key, value in rd.items() if key in prv_fields
        }

        filtered_supplier["fecharegistro"] = time_record

        filtered_supplier["nit"] = (
            filtered_supplier.get("nit") or filtered_supplier["item"]
        )

        filtered_supplier["isactivoproveedor"] = 1

        valid_suppliers.append(TdaWmsPrv(**filtered_supplier))

        prv_keys.append(key_prv)

    else:
        errors.append(f"error: Supplier {key_prv} record already exists")

    return prv_keys, valid_suppliers, errors


def create_prvs(db_name, valid_suppliers, errors):
    created_suppliers = []
    bulk_size = 50

    for i in range(0, len(valid_suppliers), bulk_size):
        try:
            created_supplier_instances = TdaWmsPrv.objects.using(db_name).bulk_create(
                valid_suppliers[i : i + bulk_size]
            )
            for coi in created_supplier_instances:
                created_suppliers.append(str(coi.item) + " " + str(coi.nombrecliente))

        except Exception as e:
            for r in valid_suppliers[i : i + bulk_size]:
                try:
                    r_dict = r.__dict__
                    r_dict.pop("_state", None)
                    TdaWmsPrv.objects.using(db_name).create(**r_dict)
                    created_suppliers.append(str(r.item) + " " + str(r.nombrecliente))
                except Exception as e:
                    errors.append(
                        f"error: {str(r.item)} {str(r.nombrecliente)} - {str(e)}"
                    )

    return created_suppliers, errors
