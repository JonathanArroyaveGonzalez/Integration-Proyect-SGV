from django.db.models import Q

def validate_field_model_and_detail(query, params):
    parameters = {}
    keys_to_remove = ["productoean", "estadodetransferencia", "descripcion", "loteproveedor", "pedproveedor", "id", "estadopicking", "estadoerp"]

    filtered_conditions = []
    for condition in query.children:
        if isinstance(condition, tuple):
            field_name, field_value = condition
            
            # Extraer solo el nombre base del campo sin importar los sufijos (e.g., '__in')
            base_field_name = field_name.split('__')[0]
            
            # Solo añadimos la condición si el nombre base no está en keys_to_remove
            if base_field_name not in keys_to_remove:
                filtered_conditions.append(condition)
        else:
            # Si la condición no es un simple campo-valor (puede ser otra Q anidada)
            filtered_conditions.append(condition)

    # Procesar los parámetros para eliminar el prefijo "detail_"
    for key, value in params.items():
        if "detail_" in key:
            key_new = key.replace("detail_", "")
            parameters[key_new] = value
        else:
            parameters[key] = value

    # Reconstruir la nueva query con las condiciones filtradas
    new_query = Q()
    for condition in filtered_conditions:
        if isinstance(condition, tuple):
            field_name, field_value = condition
            new_query &= Q(**{field_name: field_value})
        else:
            # Si es una condición compuesta (como otra Q), la añadimos tal cual
            new_query &= condition

    return new_query, parameters
