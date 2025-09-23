import pytz
from django.utils import timezone

from project.settings import TIME_ZONES_BD


# def get_time_by_timezone(db_name, delta_type=None, delta_value=None):
#     try:
#         time_now = timezone.now()
#         zona_horaria = TIME_ZONES_BD[db_name]
#         time_record = time_now.astimezone(pytz.timezone(zona_horaria))

#     except:
#         time_record = timezone.now()

#     try:
#         if delta_type and delta_value:
#             if delta_type == "days":
#                 time_record = time_record + timezone.timedelta(days=delta_value)
#             elif delta_type == "hours":
#                 time_record = time_record + timezone.timedelta(hours=delta_value)
#             else:
#                 time_record = time_record + timezone.timedelta(minutes=delta_value)

#         time_record = time_record.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
#     except:
#         pass

#     return time_record


def get_time_by_timezone(db_name, delta_type=None, delta_value=None):
    try:
        time_now = timezone.now()
        zona_horaria = TIME_ZONES_BD[db_name]
        time_record = time_now.astimezone(pytz.timezone(zona_horaria))
    except:
        time_record = timezone.now()
    try:
        if delta_type and delta_value:
            if delta_type == "days":
                time_record = time_record + timezone.timedelta(days=delta_value)
            elif delta_type == "hours":
                time_record = time_record + timezone.timedelta(hours=delta_value)
            else:
                time_record = time_record + timezone.timedelta(minutes=delta_value)
        # CAMBIO: Formato sin microsegundos y con espacio en lugar de T
        # YYYY-MM-DD HH:MM:SS
        # se eliminaron Microsegundo y cambiar o sustituir las T para garantizar minimo de
        # espacios
        time_record = time_record.strftime("%Y-%m-%d %H:%M:%S")
    except:
        pass
    return time_record
