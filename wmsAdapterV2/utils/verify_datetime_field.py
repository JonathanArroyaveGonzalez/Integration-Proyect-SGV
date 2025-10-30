from django.db.models import DateTimeField

from wmsAdapterV2.utils.date_parser import parse_date_string


def verify_datetime_field(model, data):
    for field in model._meta.fields:
        if isinstance(field, DateTimeField):
            for key, value in data.items():
                if key == field.name:
                    if value and value != '':
                        if isinstance(value, str):
                            data[key] = parse_date_string(value)
                        else:
                            data[key] = value
                    else: 
                        data[key] = None
    return data