from django.db.models import Q

from wmsAdapterV2.utils.filter_by_field import filter_by_primary_and_unique
from wmsAdapterV2.utils.get_time_by_timezone import get_time_by_timezone
from wmsAdapterV2.utils.query_comparing import query_comparing
from wmsAdapterV2.utils.validate_fields import get_update_date_field
from wmsAdapterV2.utils.validate_fields_model_and_detail import (
    validate_field_model_and_detail,
)
from wmsAdapterV2.utils.validate_fields_not_unique import validate_fields_not_primary
from wmsAdapterV2.utils.validate_request_data import validate_request_data
from wmsAdapterV2.utils.verify_datetime_field import verify_datetime_field


def update_data(json_data, request_data):
    try:
        db_name = json_data.get("db_name")
        model = json_data.get("model")
        model_detail = json_data.get("model_detail", None)
        query = json_data.get("query", Q())
        query_detail = json_data.get("query_detail", Q())
        mult = json_data.get("mult", 0)

        if query.children or query_detail.children:
            request_data = validate_request_data(None, dict, request_data)
            updated, errors = _format_with_query(
                db_name, model, query, request_data, mult, model_detail, query_detail
            )

        else:
            request_data = validate_request_data(None, list, request_data)
            updated, errors = _format_without_query(
                db_name, model, request_data, mult, model_detail
            )

        return updated, errors

    except Exception as e:
        raise ValueError(e)


def _format_with_query(
    db_name, model, query, request_data, mult, model_detail, query_detail
):
    update_field = get_update_date_field(model)
    time_now = get_time_by_timezone(db_name)

    records = []
    detail_records = []
    updated = []
    errors = []
    query_d = Q()

    detail = request_data.get("order_detail", [])
    if detail:
        update_field_detail = get_update_date_field(model_detail)

        for d in detail:
            d = validate_fields_not_primary(model_detail, d)
            d[update_field_detail] = time_now

            if query_comparing(query, query_detail):
                query_d, d = filter_by_primary_and_unique(model_detail, query_detail, d)
            else:
                query_d = query_detail

            detail_records.append({"query": query_d, "params": d})

        del request_data["order_detail"]

    # request_data_copy = request_data.copy()
    request_data = validate_fields_not_primary(model, request_data)

    if request_data:
        if update_field:
            request_data[update_field] = time_now

        records.append({"query": query, "params": request_data})
    # else:
    #     request_data_copy['error'] = 'Can not modify primary key'
    #     errors.append(request_data_copy)

    if mult == 1:
        if records:
            u, error = _update_multiple_records(db_name, model, records)
            updated.extend(u)
            errors.extend(error)

        if detail_records:
            u, error = _update_multiple_records(db_name, model_detail, detail_records)
            updated.extend(u)
            errors.extend(error)

    else:
        if records:
            u, error = _update_single_record(db_name, model, records)
            updated.extend(u)
            errors.extend(error)

        if detail_records:
            u, error = _update_single_record(db_name, model_detail, detail_records)
            updated.extend(u)
            errors.extend(error)

    return updated, errors


def _format_without_query(db_name, model, request_data, mult, model_detail):
    update_field = get_update_date_field(model)
    time_now = get_time_by_timezone(db_name)

    records = []
    errors = []
    detail_records = []
    for rd in request_data:
        query = Q()
        try:
            query, params = filter_by_primary_and_unique(model, query, rd)

            detail = params.get("order_detail", [])
            if detail:
                detail_record = _format_detail_query(
                    db_name, model_detail, query, detail
                )
                del params["order_detail"]
                detail_records.extend(detail_record)

            if update_field:
                params[update_field] = time_now

            records.append({"query": query, "params": params})

        except Exception as e:
            rd["error"] = str(e)
            errors.append(rd)
            continue

    if not records:
        return [], errors

    if mult == 1:
        updated, error = _update_multiple_records(db_name, model, records)
        errors.extend(error)

        if detail_records:
            u, error = _update_multiple_records(db_name, model_detail, detail_records)
            updated.extend(u)
            errors.extend(error)

    else:
        updated, error = _update_single_record(db_name, model, records)
        errors.extend(error)

        if detail_records:
            u, error = _update_single_record(db_name, model_detail, detail_records)
            updated.extend(u)
            errors.extend(error)

    return updated, errors


def _update_multiple_records(db_name, model, records):
    updated = []
    errors = []
    for r in records:
        query = r["query"]
        query_dict = dict(query.children)
        query_json = _format_response_from_query_dict(query_dict)
        params = r["params"]

        params = verify_datetime_field(model, params)

        try:
            if not params:
                return [], []

            updated_count = model.objects.using(db_name).filter(query).update(**params)
            query_json["quantity_updated"] = updated_count

            if updated_count == 0:
                query_json["error"] = "No matching record found"
                errors.append(query_json)
            else:
                updated.append(query_json)

        except Exception as e:
            query_json["error"] = str(e)
            errors.append(query_json)

    return updated, errors


def _update_single_record(db_name, model, records):
    updated = []
    errors = []
    for r in records:
        query = r["query"]
        query_dict = dict(query.children)
        query_json = _format_response_from_query_dict(query_dict)
        params = r["params"]

        params = verify_datetime_field(model, params)

        try:
            exists_count = model.objects.using(db_name).filter(query).count()
            if exists_count == 0:
                query_json["error"] = "No matching record found"
                errors.append(query_json)
                continue
            elif exists_count > 1:
                query_json["error"] = (
                    "Cannot update multiple records without sending the confirmation parameter"
                )
                errors.append(query_json)
                continue
            else:
                model.objects.using(db_name).filter(query).update(**params)
                updated.append(query_json)

        except model.MultipleObjectsReturned:
            query_json["error"] = (
                "Cannot update multiple records without sending the confirmation parameter"
            )
            errors.append(query_json)
            continue

        except model.DoesNotExist:
            query_json["error"] = "No matching record found"
            errors.append(query_json)
            continue

        except Exception as e:
            query_json["error"] = str(e)
            errors.append(query_json)
            continue

    return updated, errors


def _format_detail_query(db_name, model_detail, query, params):
    update_field = get_update_date_field(model_detail)
    time_now = get_time_by_timezone(db_name)

    detail_records = []
    for p in params:
        query_detail, p = validate_field_model_and_detail(query, p)
        query_detail, p = filter_by_primary_and_unique(model_detail, query_detail, p)

        if update_field:
            p[update_field] = time_now

        detail_records.append({"query": query_detail, "params": p})

    return detail_records


def _format_response_from_query_dict(query_dict):
    p = {}
    for key, value in query_dict.items():
        key_condition = key.split("__")

        if len(key_condition) > 1:
            key = key_condition[0]
            condition = key_condition[1]

            if "contains" in condition:
                p[key.replace(f"__{condition}", "")] = "%" + str(value) + "%"

            if len(value) > 1:
                p[key.replace(f"__{condition}", "")] = value

            elif len(value) == 1:
                p[key.replace(f"__{condition}", "")] = value[0]

        else:
            p[key] = value

    return p
