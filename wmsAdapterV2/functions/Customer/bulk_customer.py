from wmsAdapterV2.models import TdaWmsClt
from wmsAdapterV2.utils.convert_field_to_string import convert_to_string
from wmsAdapterV2.utils.get_time_by_timezone import get_time_by_timezone
from wmsAdapterV2.utils.validate_request_data import validate_request_data


def create_list_customers(request, db_name, request_data=None):
    # Convert request data to a list of dictionaries
    try:
        request_data = validate_request_data(request, list, request_data)
        time_record = get_time_by_timezone(db_name)
    except Exception as e:
        raise ValueError(e)

    # Initialize lists to hold valid and invalid data
    valid_customers = []
    errors = []

    # Check if the record already exists
    clt_keys = list(TdaWmsClt.objects.using(db_name).values_list("item", flat=True))

    for rd in request_data:
        clt_key = convert_to_string(rd["item"])

        valid_clt = validate_clt_data(rd)
        if valid_clt:
            errors.append(f"error: {clt_key} {valid_clt}")
            continue

        clt_keys, valid_customers, errors = format_clt_object(
            rd, clt_keys, clt_key, valid_customers, errors, time_record
        )

    created_customers, errors = create_clts(db_name, valid_customers, errors)
    return created_customers, errors


def validate_clt_data(rd):
    if not isinstance(rd, dict):
        return "Each register in the provided data should be a dictionary"

    if "item" not in rd or not rd["item"]:
        return "The item field is mandatory"

    if "nombrecliente" not in rd or not rd["nombrecliente"]:
        return "The nombrecliente field is mandatory"

    return None


def format_clt_object(rd, clt_keys, key_clt, valid_customers, errors, time_record):
    clt_fields = [field.name for field in TdaWmsClt._meta.get_fields()]

    if key_clt not in clt_keys:
        filtered_customer = {
            key: value for key, value in rd.items() if key in clt_fields
        }

        filtered_customer["fecharegistro"] = str(time_record)

        filtered_customer["nit"] = (
            filtered_customer.get("nit") or filtered_customer["item"]
        )

        filtered_customer["activocliente"] = 1
        filtered_customer["isactivocliente"] = 1

        valid_customers.append(TdaWmsClt(**filtered_customer))

        clt_keys.append(key_clt)

    else:
        errors.append(f"error: Customer {key_clt} record already exists")

    return clt_keys, valid_customers, errors


def create_clts(db_name, valid_customers, errors):
    created_customers = []
    bulk_size = 50

    for i in range(0, len(valid_customers), bulk_size):
        try:
            created_customer_instances = TdaWmsClt.objects.using(db_name).bulk_create(
                valid_customers[i : i + bulk_size]
            )
            for coi in created_customer_instances:
                created_customers.append(str(coi.item) + " " + str(coi.nombrecliente))

        except Exception as e:
            for r in valid_customers[i : i + bulk_size]:
                try:
                    r_dict = r.__dict__
                    r_dict.pop("_state", None)
                    TdaWmsClt.objects.using(db_name).create(**r_dict)
                    created_customers.append(str(r.item) + " " + str(r.nombrecliente))
                except Exception as e:
                    errors.append(
                        f"error: {str(r.item)} {str(r.nombrecliente)} - {str(e)}"
                    )

    return created_customers, errors
