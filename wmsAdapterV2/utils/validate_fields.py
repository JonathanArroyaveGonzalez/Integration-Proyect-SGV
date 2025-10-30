def validate_fields(fields, model):
    """Validate that the provided fields exist in the model."""
    model_fields = [field.name for field in model._meta.get_fields()]
    
    if fields:
        for field in fields:
            if field not in model_fields:
                raise ValueError(f"Field {field} not found")
    else:
        fields = model_fields
    
    return fields


def get_update_date_field(model):
    """Validate that the provided fields exist in the model."""
    model_fields = [field.name for field in model._meta.get_fields()]
    
    update_field = ''
    for field in model_fields:
        if 'ultima_actualizacion' in field:
            update_field = field
            break
    
    if update_field:
        return update_field
    
    return None



def get_transfer_state_field(model):
    """Validate that the provided fields exist in the model."""
    model_fields = [field.name for field in model._meta.get_fields()]
    
    state_field = ''
    for field in model_fields:
        if "estadotransferencia" in field or "estadodetransferencia" in field:
            state_field = field
            break
    
    if state_field:
        return state_field
    
    return None