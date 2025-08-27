from datetime import datetime
from dateutil import parser

def parse_date_string(date_string):
    """
    Parse different date string formats into datetime objects.
    
    Args:
        date_string (str): Date string to parse
        
    Returns:
        datetime: Parsed datetime object
        
    Raises:
        ValueError: If the date string cannot be parsed
    """
    # Lista de formatos posibles
    date_formats = [
        # Formatos con hora parcial
        '%Y-%m-%d %H',              # Formato que causaba el error (2024-10-28 12)
        '%Y-%m-%dT%H',              # Variante ISO con solo hora
        
        # Formatos ISO
        '%Y-%m-%dT%H:%M:%SZ',       # UTC ISO
        '%Y-%m-%dT%H:%M:%S',        # ISO sin zona horaria
        '%Y-%m-%dT%H:%M',           # ISO hasta minutos
        '%Y-%m-%d',                 # Solo fecha (ISO)
        '%Y%m%d',                   # Solo fecha compacto
        
        # Formatos RFC
        '%a, %d %b %Y %H:%M:%S %z', # RFC 2822 completo
        '%d %b %Y %H:%M:%S %z',     # RFC 2822 sin día
        
        # Formatos comunes
        '%Y-%m-%d %H:%M:%S',        # Común con segundos
        '%Y-%m-%d %H:%M',           # Común con minutos
        '%Y/%m/%d %H:%M:%S',        # Variantes con "/"
        '%Y/%m/%d %H:%M',
        '%Y/%m/%d',
        '%m/%d/%Y',                 # Formato EE.UU.
    ]

    # Primero intentar con los formatos específicos
    for date_format in date_formats:
        try:
            parsed_date = datetime.strptime(date_string, date_format)
            # Completar campos faltantes según el formato
            if date_format in ['%Y-%m-%d %H', '%Y-%m-%dT%H']:
                parsed_date = parsed_date.replace(minute=0, second=0, microsecond=0)
            elif date_format in ['%Y-%m-%d %H:%M', '%Y-%m-%dT%H:%M']:
                parsed_date = parsed_date.replace(second=0, microsecond=0)
            elif '%S' not in date_format:
                parsed_date = parsed_date.replace(second=0, microsecond=0)
                
            return parsed_date
        except ValueError:
            continue

    # Si ningún formato coincide, intentar con dateutil.parser
    try:
        parsed_date = parser.parse(date_string)
        
        # Ajustar precisión si solo se especifica la hora
        if parsed_date.second == 0 and parsed_date.microsecond == 0:
            parsed_date = parsed_date.replace(second=0, microsecond=0)
            
        return parsed_date
    except (ValueError, TypeError):
        raise ValueError(f"The date cannot be formatted: {date_string}")
