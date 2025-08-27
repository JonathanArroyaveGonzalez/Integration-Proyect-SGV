from django.db.models import Q
from collections import defaultdict


def exec_query_orm(json_data):
    db_name = json_data.get("db_name")
    model = json_data.get("model")
    model_detail = json_data.get("model_detail", None)
    query = json_data.get("query", Q())
    query_detail = json_data.get("query_detail", Q())
    fields = json_data.get("fields", [])
    include = json_data.get("include", [])
    default_limit = json_data.get("default_limit", 100)
    sort = json_data.get("sort", None)
    field_join = json_data.get("field_join", "")
    field_join_detail = json_data.get("field_join_detail", None)
    db_name_detail = json_data.get("db_name_detail", None)

    if not field_join_detail:
        field_join_detail = field_join

    if not db_name_detail:
        db_name_detail = db_name

    detail_list = []
    
    if not query and query_detail:
        detail_list = _execute_query_detail(
            db_name_detail, model_detail, query_detail, {}, field_join_detail
        )
        query = _update_query(query, detail_list, field_join, field_join_detail)
    
    model_list = _create_model_base_query(
        db_name, model, query, field_join, fields, sort, default_limit
    )
    
    records = []
    if include or query_detail:
        
        query_detail = _update_query(query_detail, model_list, field_join, field_join_detail)
        
        detail_list = _execute_query_detail(
            db_name_detail, model_detail, query_detail, include, field_join_detail
        )
        
        records = _include_filter_detail(
            model_list, detail_list, field_join, field_join_detail, fields, include
        )
    else:
        if field_join and field_join not in fields:
            for order in model_list:
                del order[field_join]
                records.append(order)
        else:
            records = model_list

    return records, query, query_detail


def _create_model_base_query(
    db_name, model, query, field_join, fields, sort, default_limit
):
    if field_join:
        if sort:
            model_list = list(model.objects.using(db_name).filter(query).values(*fields, field_join).order_by(sort)[:default_limit])
        else:
            model_list = list(model.objects.using(db_name).filter(query).values(*fields, field_join)[:default_limit])
    else:
        if sort:
            model_list = list(model.objects.using(db_name).filter(query).values(*fields).order_by(sort)[:default_limit])
        else:
            model_list = list(model.objects.using(db_name).filter(query).values(*fields)[:default_limit])

    return model_list


def _update_query(q, m_list, field_join, field_join_detail):
    list_field_join = []
    for obj in m_list:
        list_field_join.append(obj[field_join])

    q &= Q(**{f"{field_join_detail}__in": list_field_join})
    return q


def _execute_query_detail(db_name, m, q, f, field_join):
    m_list = list(m.objects.using(db_name).filter(q).values(*f, field_join))
    return m_list


def _include_filter_detail(model_list, detail_list, field_join, field_join_detail, fields, include):
    order_details_dict = defaultdict(list)

    orders = []
    for detail in detail_list:
        picking = detail.pop(field_join_detail)
        order_details_dict[picking].append(detail)

    for order in model_list:
        order_picking = order[field_join]
        order_detail = order_details_dict.get(order_picking, [])

        if order_detail:
            if include:
                order["order_detail"] = order_detail

            if field_join not in fields:
                order.pop(field_join, None)

        orders.append(order)

    return orders
