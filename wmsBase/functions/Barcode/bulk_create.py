from wmsAdapterV2.utils.convert_field_to_string import convert_to_string
from wmsAdapterV2.utils.get_time_by_timezone import get_time_by_timezone
from wmsAdapterV2.utils.validate_request_data import validate_request_data
from wmsBase.models.TRelacionCodbarras import TRelacionCodbarras


def create_list_cod_barras(request, db_name, request_data=None):
    # Convert request data to a list of dictionaries
    try:
        request_data = validate_request_data(request, list, request_data)
        time_record = get_time_by_timezone(db_name)
    except Exception as e:
        raise ValueError(e)

    # Initialize lists to hold valid and invalid data
    valid_barcodes = []
    errors = []

    # Check if the record already exists
    cod_barras_keys = list(
        TRelacionCodbarras.objects.using(db_name).values_list(
            "codbarrasasignado", flat=True
        )
    )

    for rd in request_data:
        cod_barras_key = convert_to_string(rd["codbarrasasignado"])

        valid_cod_barras = validate_cod_barras_data(rd)
        if valid_cod_barras:
            errors.append("error: " + str(cod_barras_key) + " " + str(valid_cod_barras))
            continue

        cod_barras_keys, valid_barcodes, errors = format_cod_barras_object(
            rd, cod_barras_keys, cod_barras_key, valid_barcodes, errors, time_record
        )

    created_barcodes, errors = create_cod_barras(db_name, valid_barcodes, errors)
    return created_barcodes, errors


def validate_cod_barras_data(rd):
    if not isinstance(rd, dict):
        return "Each register in the provided data should be a dictionary"

    if "idinternoean" not in rd or not rd["idinternoean"]:
        return "The idinternoean field is mandatory"

    if "codbarrasasignado" not in rd or not rd["codbarrasasignado"]:
        return "The codbarrasasignado field is mandatory"

    return None


def format_cod_barras_object(
    rd, cod_barras_keys, key_cod_barras, valid_barcodes, errors, time_record
):
    cod_barras_fields = [field.name for field in TRelacionCodbarras._meta.get_fields()]

    if key_cod_barras not in cod_barras_keys:
        filtered_barcode = {
            key: value for key, value in rd.items() if key in cod_barras_fields
        }

        if "id" in rd:
            del rd["id"]

        filtered_barcode["fechacrea"] = time_record
        filtered_barcode["cantidad"] = filtered_barcode.get("cantidad") or 1

        valid_barcodes.append(TRelacionCodbarras(**filtered_barcode))

        cod_barras_keys.append(key_cod_barras)

    else:
        errors.append(
            "error: " + str(key_cod_barras) + " barcode record already exists"
        )

    return cod_barras_keys, valid_barcodes, errors


def create_cod_barras(db_name, valid_barcodes, errors):
    created_barcodes = []
    bulk_size = 50

    for i in range(0, len(valid_barcodes), bulk_size):
        try:
            created_customer_instances = TRelacionCodbarras.objects.using(
                db_name
            ).bulk_create(valid_barcodes[i : i + bulk_size])
            for coi in created_customer_instances:
                created_barcodes.append(
                    str(coi.idinternoean) + " " + str(coi.codbarrasasignado)
                )

        except Exception as e:
            for r in valid_barcodes[i : i + bulk_size]:
                try:
                    r_dict = r.__dict__
                    r_dict.pop("_state", None)
                    TRelacionCodbarras.objects.using(db_name).create(**r_dict)
                    created_barcodes.append(
                        str(r.idinternoean) + " " + str(r.codbarrasasignado)
                    )
                except Exception as e:
                    errors.append(
                        f"error: {str(r.idinternoean)} {str(r.codbarrasasignado)} - {str(e)}"
                    )

    return created_barcodes, errors
