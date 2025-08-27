from wmsAdapterV2.models import TdaWmsDpn
from django.db import connections


def get_next_lineaidpicking(db_name, model):
    last_lineaidpicking = model.objects.using(db_name).order_by('-lineaidpicking').values_list('lineaidpicking', flat=True).first()

    # Si necesitas incrementar este valor para generar el siguiente:
    if last_lineaidpicking is not None:
        next_lineaidpicking = last_lineaidpicking + 1
    else:
        next_lineaidpicking = 1

    return next_lineaidpicking

def get_next_lineaidop(db_name):
    last_lineaidop = TdaWmsDpn.objects.using(db_name).order_by('-lineaidop').values_list('lineaidop', flat=True).first()

    # Si necesitas incrementar este valor para generar el siguiente:
    if last_lineaidop is not None:
        next_lineaidop = last_lineaidop + 1
    else:
        next_lineaidop = 1

    return next_lineaidop

def get_next_picking(db_name, model):
    resultado = model.objects.raw('SELECT * FROM mi_tabla ')
    next_picking = model.objects.using(db_name).order_by('-picking').values_list('picking', flat=True).first()

    # Si necesitas incrementar este valor para generar el siguiente:
    if next_picking is not None:
        next_picking = next_picking + 1
    else:
        next_picking = 1

    return next_picking



def get_sequence(sequence, db_name):
    try:
        with connections[db_name].cursor() as cursor:
            cursor.execute(f"SELECT NEXT VALUE FOR {sequence}")
            
            result = cursor.fetchone()
            
            if result is None:
                raise ValueError(f'Error getting sequence {sequence}')
            
            return result[0] if result else 1
            
    except Exception as e:
        raise ValueError(f"Error getting sequence of {db_name}: {e}")
