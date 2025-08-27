from wmsAdapterV2.utils.validate_fields import validate_fields


def parse_include_param(include):
    """Parse the 'include' parameter to extract the key and values."""
    if ':' in include:
        key, values = include.split(':', 1) 
    else:
        key, values = include, ''
    return key, values


def extract_fields_from_values(values):
    """Extract and clean field names from the 'values' string."""
    return [field.strip() for field in values.replace('[', '').replace(']', '').replace("'", "").split(',') if field]

def get_include_filter(model, params):
    """Main function to process the 'include' parameter and return valid fields."""
    if 'include' not in params:
        return [], params

    include = str(params['include'][0])
    key, values = parse_include_param(include)
    
    params.pop('include')

    if key == 'order_detail':
        order_detail_fields = extract_fields_from_values(values)
        return validate_fields(order_detail_fields, model), params

    return [], params