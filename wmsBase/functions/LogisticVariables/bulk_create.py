from django.utils import timezone

from wmsAdapterV2.utils.convert_field_to_string import convert_to_string
from wmsAdapterV2.utils.validate_request_data import validate_request_data
from wmsBase.models.TDetalleRefenciaCv import TDetalleRefenciaCv


def create_list_logistic_variables(request, db_name, request_data=None):
    # Convert request data to a list of dictionaries
    try:
        request_data = validate_request_data(request, list, request_data)
    except Exception as e:
        raise ValueError(e)  

    # Initialize lists to hold valid and invalid data
    valid_logistic_variables = []
    errors = []
    
    # Check if the record already exists
    logistic_variables_list = list(TDetalleRefenciaCv.objects.using(db_name).values('productoean', 'bodega'))
    logistic_variables_keys = {convert_to_string(log_var["bodega"]) + ' ' + convert_to_string(log_var["productoean"]) for log_var in logistic_variables_list}
    
    for rd in request_data:
        logistic_variables_key = convert_to_string(rd["bodega"]) + ' ' + convert_to_string(rd["productoean"])
        valid_logvar = validate_logistic_variables_data(rd)
        if valid_logvar:
            errors.append('error: ' + str(logistic_variables_key) + ' ' + str(valid_logvar))
            continue
    
        logistic_variables_keys, valid_logistic_variables, errors = format_logistic_variables_object(rd, logistic_variables_keys, logistic_variables_key, valid_logistic_variables, errors)
        
    created_logistic_variables, errors = create_logistic_variables(db_name, valid_logistic_variables, errors)
    
    return created_logistic_variables, errors


def validate_logistic_variables_data(rd):
    if not isinstance(rd, dict):
        return 'Each register in the provided data should be a dictionary'

    if 'productoean' not in rd or not rd['productoean']:
        return 'The productoean field is mandatory'

    if 'bodega' not in rd or not rd['bodega']:
        return 'The bodega field is mandatory'
    
    return None


def format_logistic_variables_object(rd, logistic_variables_keys, key_logistic_variables, valid_logistic_variables, errors):
    time_now = timezone.now()
    logistic_variables_fields = [field.name for field in TDetalleRefenciaCv._meta.get_fields()]

    if key_logistic_variables not in logistic_variables_keys:
        filtered_logistic_variables = {key: value for key, value in rd.items() if key in logistic_variables_fields}

        if 'id' in rd:
            del rd['id']
        
        filtered_logistic_variables['fechamodificacion'] = time_now
        filtered_logistic_variables['diasvigenciaproveedor'] = filtered_logistic_variables.get('diasvigenciaproveedor') or 0
        filtered_logistic_variables['diasvigenciacedi'] = filtered_logistic_variables.get('diasvigenciacedi') or 0
        filtered_logistic_variables['cantidadempaque'] = filtered_logistic_variables.get('cantidadempaque') or 0
        filtered_logistic_variables['peso'] = filtered_logistic_variables.get('peso') or 0
        filtered_logistic_variables['volumen'] = filtered_logistic_variables.get('volumen') or 0
        filtered_logistic_variables['stockmin'] = filtered_logistic_variables.get('stockmin') or 0
        filtered_logistic_variables['stockmax'] = filtered_logistic_variables.get('stockmax') or 0
        filtered_logistic_variables['codgrupoprm'] = filtered_logistic_variables.get('codgrupoprm') or '0'
        filtered_logistic_variables['controla_status_calidad'] = filtered_logistic_variables.get('controla_status_calidad') or 0
        filtered_logistic_variables['factor_estibado'] = filtered_logistic_variables.get('factor_estibado') or 0
        filtered_logistic_variables['controlafechavencimiento'] = filtered_logistic_variables.get('controlafechavencimiento') or 0
        filtered_logistic_variables['dim_x'] = filtered_logistic_variables.get('dim_x') or 0
        filtered_logistic_variables['dim_y'] = filtered_logistic_variables.get('dim_y') or 0
        filtered_logistic_variables['dim_z'] = filtered_logistic_variables.get('dim_z') or 0
        filtered_logistic_variables['doble_unidad_de_medida'] = filtered_logistic_variables.get('doble_unidad_de_medida') or 0
        filtered_logistic_variables['listavigencias'] = filtered_logistic_variables.get('listavigencias') or 1
        

        valid_logistic_variables.append(TDetalleRefenciaCv(**filtered_logistic_variables))
        logistic_variables_keys.add(key_logistic_variables)
            
    else:
        errors.append('error: ' + str(key_logistic_variables) + ' logistic variable record already exists')
    
    return logistic_variables_keys, valid_logistic_variables, errors


def create_logistic_variables(db_name, valid_logistic_variables, errors):
    created_logistic_variables = []
    bulk_size = 50

    for i in range(0, len(valid_logistic_variables), bulk_size):
        try:
            created_customer_instances = TDetalleRefenciaCv.objects.using(db_name).bulk_create(valid_logistic_variables[i : i+bulk_size])
            for coi in created_customer_instances:
                created_logistic_variables.append(str(coi.bodega) + ' ' + str(coi.productoean))

        except Exception as e:
            for r in valid_logistic_variables[i : i+bulk_size]:
                try:
                    r_dict = r.__dict__
                    r_dict.pop('_state', None)
                    TDetalleRefenciaCv.objects.using(db_name).create(**r_dict)
                    created_logistic_variables.append(str(r.bodega) + ' ' + str(r.productoean))
                except Exception as e:
                    errors.append(f'error: {str(r.bodega)} {str(r.productoean)} - {str(e)}')

    return created_logistic_variables, errors