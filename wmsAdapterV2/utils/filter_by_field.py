from django.db import models
from django.db.models import Q


def filter_by_field(model, query, params):
    # Get the final fields
    filter_model_fields = {}

    model_fields = [field.name for field in model._meta.get_fields()]
    for f in model_fields:
        filter_model_fields[f] = params.get(f, "")

    # Check if the fields are empty
    for key, value in filter_model_fields.items():
        if value != "":
            value = value[0]
            if ":" in value:
                separated = value.split(":", 1)

                key_search = separated[0]
                if key_search in [
                    "contains",
                    "gt",
                    "gte",
                    "lt",
                    "lte",
                    "startswith",
                    "endswith",
                    "isnull",
                ]:
                    value_search = separated[1]

                    if key_search == "isnull":
                        value_search = True

                    query &= Q(**{f"{key}__{key_search}": value_search})
                else:
                    value_search = value
                    query &= Q(**{f"{key}": value_search})

            else:
                values = (
                    str(value)
                    .replace("[", "")
                    .replace("]", "")
                    .replace("'", "")
                    .split(",")
                )

                field = model._meta.get_field(key)
                final_values = []

                if len(values) > 1:
                    for v in values:
                        if isinstance(field, models.IntegerField):
                            final_values.append(int(v))
                        elif isinstance(field, models.FloatField):
                            final_values.append(float(v))
                        elif isinstance(field, models.CharField):
                            final_values.append(v.strip())
                        else:
                            final_values.append(v.strip())

                    if final_values:
                        query &= Q(**{f"{key}__in": final_values})

                elif len(values) == 1:
                    if values[0] == "" or values[0] == "isnull":
                        query &= Q(**{f"{key}__isnull": True})
                    else:
                        query &= Q(**{f"{key}": values[0]})

            del params[key]

    return query, params


def filter_by_primary_and_unique(model, query, params):
    # Get the final fields
    filter_model_fields = {}

    unique = model._meta.unique_together

    model_fields = []
    if unique:
        model_fields = [field for field in unique[0]]
    model_fields.append(model._meta.pk.name)

    for f in model_fields:
        filter_model_fields[f] = params.get(f, "")

    # Check if the fields are empty
    for key, value in filter_model_fields.items():
        if value != "":
            value = str(value)
            if value.startswith("contains:"):
                contains_value = value.replace("contains:", "").strip()
                query &= Q(**{f"{key}__icontains": contains_value})
            else:
                values = (
                    str(value)
                    .replace("[", "")
                    .replace("]", "")
                    .replace("'", "")
                    .split(",")
                )

                field = model._meta.get_field(key)
                final_values = []

                for v in values:
                    if isinstance(field, models.IntegerField):
                        final_values.append(int(v))
                    elif isinstance(field, models.FloatField):
                        final_values.append(float(v))
                    elif isinstance(field, models.CharField):
                        final_values.append(v.strip())
                    else:
                        final_values.append(v.strip())

                if final_values:
                    query &= Q(**{f"{key}__in": final_values})

            del params[key]

    params_copy = params.copy()
    for key, value in params_copy.items():
        if "__new" in key:
            params[str(key).replace("__new", "")] = value

            del params[key]

    return query, params


def filter_by_field_request_data(model, query, params):
    # Get the final fields
    filter_model_fields = {}

    model_fields = [field.name for field in model._meta.get_fields()]
    for f in model_fields:
        filter_model_fields[f] = params.get(f, "")

    # Check if the fields are empty
    for key, value in filter_model_fields.items():
        if value != "":
            value = value
            if str(value).startswith("contains:"):
                contains_value = value.replace("contains:", "").strip()
                query &= Q(**{f"{key}__icontains": contains_value})
            else:
                values = (
                    str(value)
                    .replace("[", "")
                    .replace("]", "")
                    .replace("'", "")
                    .split(",")
                )

                field = model._meta.get_field(key)
                final_values = []

                for v in values:
                    if isinstance(field, models.IntegerField):
                        final_values.append(int(v))
                    elif isinstance(field, models.FloatField):
                        final_values.append(float(v))
                    elif isinstance(field, models.CharField):
                        final_values.append(v.strip())
                    else:
                        final_values.append(v.strip())

                if final_values:
                    query &= Q(**{f"{key}__in": final_values})

            del params[key]

    return query, params
