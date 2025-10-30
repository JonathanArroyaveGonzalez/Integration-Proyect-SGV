from datetime import datetime
from decimal import Decimal 


def serializer(data):
    if isinstance(data, datetime):
        return data.isoformat()  # Convertir datetime a string ISO
    elif isinstance(data, Decimal):
        return float(data)  # Convertir Decimal a float
    raise TypeError(f"Type {type(data)} not serializable")

    