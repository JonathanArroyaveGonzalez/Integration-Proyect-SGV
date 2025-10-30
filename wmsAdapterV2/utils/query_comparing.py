from django.db.models import Q

def query_comparing(q1: Q, q2: Q) -> bool:
    def make_hashable(value):
        if isinstance(value, list):
            return tuple(value)
        elif isinstance(value, dict):
            return tuple(value.items())
        return value


    def normalize_condition(condition):
        field, value = condition
        return (field, make_hashable(value))


    def extract_conditions(q_obj):
        conditions = set()
        
        if hasattr(q_obj, 'children'):
            for child in q_obj.children:
                if isinstance(child, tuple):
                    conditions.add(normalize_condition(child))
                elif isinstance(child, Q):
                    conditions.update(extract_conditions(child))
        
        return conditions

    q1_conditions = extract_conditions(q1)
    q2_conditions = extract_conditions(q2)
    
    return q2_conditions.issubset(q1_conditions)
