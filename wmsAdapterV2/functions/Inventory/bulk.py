from wmsAdapterV2.models import TdaWmsInv
from wmsAdapterV2.utils.convert_field_to_string import convert_to_string
from wmsAdapterV2.utils.get_time_by_timezone import get_time_by_timezone
from wmsAdapterV2.utils.validate_request_data import validate_request_data


def create_list_inventory(request, db_name, request_data=None):
    # Convert request data to a list of dictionaries
    try:
        request_data = validate_request_data(request, list, request_data)
        time_record = get_time_by_timezone(db_name)
    except Exception as e:
        raise ValueError(e)  

    # Initialize lists to hold valid and invalid data
    valid_inventory = []
    errors = []
    
    # Check if the record already exists
    inv_list = list(TdaWmsInv.objects.using(db_name).values('productoean', 'bod', 'ubicacion'))
    inv_keys = {convert_to_string(inv["bod"]) + ' ' + convert_to_string(inv["ubicacion"]) + ' ' + convert_to_string(inv["productoean"]) for inv in inv_list}

    for rd in request_data:
        inv_key = convert_to_string(rd["bod"]) + ' ' + convert_to_string(rd["ubicacion"]) + ' ' + convert_to_string(rd["productoean"])
        
        valid_inv = validate_inv_data(rd)
        if valid_inv:
            errors.append('error: ' + str(inv_key) + ' ' + str(valid_inv))
            continue
        
        inv_keys, valid_inventory, errors = format_inv_object(rd, inv_keys, inv_key, valid_inventory, errors, time_record)
        

    created_inventory, errors = create_invs(db_name, valid_inventory, errors)
    return created_inventory, errors


def validate_inv_data(rd):
    if not isinstance(rd, dict):
        return 'Each register in the provided data should be a dictionary'

    if 'productoean' not in rd or not rd['productoean']:
        return 'The productoean field is mandatory'

    if 'bod' not in rd or not rd['bod']:
        return 'The bod field is mandatory'
    
    # if 'ubicacion' not in rd or not rd['ubicacion']:
    #     return 'The ubicacion field is mandatory'

    return None


def format_inv_object(rd, inv_keys, key_inv, valid_inventory, errors, time_record):
    inv_fields = [field.name for field in TdaWmsInv._meta.get_fields()]

    if key_inv not in inv_keys:
        filtered_product = {key: value for key, value in rd.items() if key in inv_fields}

        if 'id' in rd:
            del rd['id']

        filtered_product['fecharegistro'] = time_record
        filtered_product['fecha_ultima_actualizacion'] = time_record
        
        filtered_product['codigoalmacen'] = filtered_product.get('codigoalmacen') or filtered_product["bod"]
        
        valid_inventory.append(TdaWmsInv(**filtered_product))

        inv_keys.add(key_inv)
            
    else:
        errors.append('error: ' + str(key_inv) + ' Inventory record already exists')
    
    return inv_keys, valid_inventory, errors


def create_invs(db_name, valid_inventory, errors):
    created_inventory = []
    bulk_size = 50

    for i in range(0, len(valid_inventory), bulk_size):
        try:
            created_customer_instances = TdaWmsInv.objects.using(db_name).bulk_create(valid_inventory[i : i+bulk_size])
            for coi in created_customer_instances:
                created_inventory.append(str(coi.productoean) + ' ' + str(coi.descripcion))

        except Exception as e:
            for r in valid_inventory[i : i+bulk_size]:
                try:
                    r_dict = r.__dict__
                    r_dict.pop('_state', None)
                    TdaWmsInv.objects.using(db_name).create(**r_dict)
                    created_inventory.append(str(r.productoean) + ' ' + str(r.descripcion))
                except Exception as e:
                    errors.append(f'error: {str(r.productoean)} {str(r.descripcion)} - {str(e)}')

    return created_inventory, errors