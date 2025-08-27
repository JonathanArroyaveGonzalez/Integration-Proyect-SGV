from wmsAdapterV2.models import TdaWmsArt
from wmsAdapterV2.utils.convert_field_to_string import convert_to_string
from wmsAdapterV2.utils.get_time_by_timezone import get_time_by_timezone
from wmsAdapterV2.utils.validate_request_data import validate_request_data


def create_list_articles(request, db_name, request_data=None):
    # Convert request data to a list of dictionaries
    try:
        request_data = validate_request_data(request, list, request_data)
        time_record = get_time_by_timezone(db_name)
    except Exception as e:
        raise ValueError(e)

    # Initialize lists to hold valid and invalid data
    valid_products = []
    errors = []

    unique_eans = {convert_to_string(p["productoean"]) for p in request_data}

    # Consultar registros existentes
    art_keys = list(
        TdaWmsArt.objects.using(db_name)
        .filter(productoean__in=unique_eans)
        .values_list("productoean", flat=True)
    )

    for rd in request_data:
        art_key = convert_to_string(rd["productoean"])

        valid_art = validate_art_data(rd)
        if valid_art:
            errors.append("error: " + str(art_key) + " " + str(valid_art))
            continue

        art_keys, valid_products, errors = format_art_object(
            rd, art_keys, art_key, valid_products, errors, time_record
        )

    created_products, errors = create_arts(db_name, valid_products, errors)
    return created_products, errors


def validate_art_data(rd):
    if not isinstance(rd, dict):
        return "Each register in the provided data should be a dictionary"

    if "productoean" not in rd or not rd["productoean"]:
        return "The productoean field is mandatory"

    if "descripcion" not in rd or not rd["descripcion"]:
        return "The descripcion field is mandatory"

    # if 'bodega' not in rd or not rd['bodega']:
    #     return 'The bodega field is mandatory'

    return None


def format_art_object(rd, art_keys, key_art, valid_products, errors, time_record):
    art_fields = [field.name for field in TdaWmsArt._meta.get_fields()]

    if key_art not in art_keys:
        filtered_product = {
            key: value for key, value in rd.items() if key in art_fields
        }

        if "id" in rd:
            del rd["id"]

        filtered_product["fecharegistro"] = time_record

        filtered_product["referencia"] = (
            filtered_product.get("referencia") or filtered_product["productoean"]
        )
        filtered_product["referenciamdc"] = (
            filtered_product.get("referenciamdc") or filtered_product["productoean"]
        )
        filtered_product["nuevoean"] = (
            filtered_product.get("nuevoean") or filtered_product["productoean"]
        )
        filtered_product["item"] = (
            filtered_product.get("item") or filtered_product["productoean"]
        )

        filtered_product["descripcioningles"] = (
            filtered_product.get("descripcioningles") or filtered_product["descripcion"]
        )

        filtered_product["factor"] = filtered_product.get("factor") or 1

        filtered_product["um1"] = filtered_product.get("um1") or "UND"
        filtered_product["presentacion"] = (
            filtered_product.get("presentacion") or filtered_product["um1"]
        )
        filtered_product["u_inv"] = (
            filtered_product.get("u_inv") or filtered_product["um1"]
        )
        filtered_product["u_inv_p"] = (
            filtered_product.get("u_inv_p") or filtered_product["um1"]
        )

        filtered_product["factor"] = filtered_product.get("factor") or 1
        filtered_product["inventariable"] = filtered_product.get("inventariable") or 1
        filtered_product["qtyequivalente"] = filtered_product.get("qtyequivalente") or 1
        filtered_product["estado"] = filtered_product.get("estado") or 1

        valid_products.append(TdaWmsArt(**filtered_product))

        art_keys.append(key_art)

    else:
        errors.append("error: " + str(key_art) + " Product record already exists")

    return art_keys, valid_products, errors


def create_arts(db_name, valid_products, errors):
    created_products = []
    bulk_size = 50

    for i in range(0, len(valid_products), bulk_size):
        try:
            created_customer_instances = TdaWmsArt.objects.using(db_name).bulk_create(
                valid_products[i : i + bulk_size]
            )
            for coi in created_customer_instances:
                created_products.append(
                    str(coi.productoean) + " " + str(coi.descripcion)
                )

        except Exception as e:
            for r in valid_products[i : i + bulk_size]:
                try:
                    r_dict = r.__dict__
                    r_dict.pop("_state", None)
                    TdaWmsArt.objects.using(db_name).create(**r_dict)
                    created_products.append(
                        str(r.productoean) + " " + str(r.descripcion)
                    )
                except Exception as e:
                    errors.append(
                        f"error: {str(r.productoean)} {str(r.descripcion)} - {str(e)}"
                    )

    return created_products, errors
