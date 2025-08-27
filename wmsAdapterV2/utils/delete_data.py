from django.db.models import Q

from wmsAdapterV2.utils.filter_by_field import filter_by_field_request_data
from wmsAdapterV2.utils.query_comparing import query_comparing
from wmsAdapterV2.utils.update_data import _format_response_from_query_dict
from wmsAdapterV2.utils.validate_fields_model_and_detail import validate_field_model_and_detail
from wmsAdapterV2.utils.validate_request_data import validate_request_data
from wmsAdapterV2.utils.validate_transfer_state import validate_delete_model, validate_records_with_transfer_state

def delete_data(json_data, request_data):
    try:
        db_name = json_data.get("db_name")
        model = json_data.get("model")
        model_detail = json_data.get("model_detail", None)
        query = json_data.get("query", Q())
        query_detail = json_data.get("query_detail", Q())
        mult = json_data.get("mult", 0)

        if query.children or query_detail.children:
            if request_data:
                request_data = validate_request_data(None, dict, request_data)
            
            deleted, errors = _format_with_query(db_name, model, query, request_data, mult, model_detail, query_detail)
            
        else:
            request_data = validate_request_data(None, list, request_data)
            deleted, errors = _format_without_query(db_name, model, request_data, mult, model_detail)
        
        return deleted, errors

    except Exception as e:
        raise ValueError(e)


def _format_with_query(db_name, model, query, request_data, mult, model_detail, query_detail):
    records = []
    detail_records = []
    deleted = []
    errors = []
    flag_delete_order = None

    detail = request_data.get('order_detail', [])
    if detail:
        del request_data['order_detail']
        
    query, request_data = filter_by_field_request_data(model, query, request_data)
    
    if query_detail.children:
        flag_delete_order = query_comparing(query, query_detail)
    else:
        flag_delete_order = True

    if flag_delete_order:
        records.append(query)
    else:
        detail_records.append(query_detail)
    
    for d in detail:
        query_d, d = validate_field_model_and_detail(query, d)
        query_d, d = filter_by_field_request_data(model_detail, query_d, d)
        detail_records.append(query_d)

    for det in detail_records:
        if not query_comparing(query, det):
            flag_delete_order = False

    validate_records_with_transfer_state(db_name, model, query, model_detail, query_detail, detail_records, flag_delete_order)

    if mult == 1:
        if not flag_delete_order:
            u, error = _delete_multiple_records(db_name, model_detail, detail_records)
            deleted.extend(u)
            errors.extend(error)

        else:
            error = []
            if model_detail:
                u, error = _delete_multiple_records(db_name, model_detail, records)
                deleted.extend(u)
                errors.extend(error)

            if not error:
                u, error = _delete_multiple_records(db_name, model, records)
                deleted.extend(u)
                errors.extend(error)

    else:
        if not flag_delete_order:
            u, error = _delete_single_record(db_name, model_detail, detail_records)
            deleted.extend(u)
            errors.extend(error)
        else:
            error = []
            if model_detail:
                u, error = _delete_single_record(db_name, model_detail, records)
                deleted.extend(u)
                errors.extend(error)

            if not error:
                u, error = _delete_single_record(db_name, model, records)
                deleted.extend(u)
                errors.extend(error)

    return deleted, errors


def _format_without_query(db_name, model, request_data, mult, model_detail):
    records = []
    errors = []
    detail_records = []
    deleted = []
    
    for rd in request_data:
        rd_aux = rd.copy()
        query = Q()
        try:
            detail = rd.get('order_detail', [])
            if detail:
                del rd['order_detail']
            
            query, rd = filter_by_field_request_data(model, query, rd)
            
            flag_delete_order = True
            detail_records_aux = []
            for d in detail:
                query_detail, d = validate_field_model_and_detail(query, d)
                query_detail, d = filter_by_field_request_data(model_detail, query_detail, d)
            
                if not query_comparing(query, query_detail):
                    detail_records_aux.append(query_detail)  
                    flag_delete_order = False              
            
            validate_records_with_transfer_state(db_name, model, query, model_detail, Q(), detail_records_aux, flag_delete_order)
            if flag_delete_order:
                records.append(query)
            else:
                detail_records.extend(detail_records_aux)
            
        except Exception as e:
            rd_aux['error'] = str(e)
            errors.append(rd_aux)
            continue

    if mult == 1:
        if detail_records:
            u, error = _delete_multiple_records(db_name, model_detail, detail_records)
            deleted.extend(u)
            errors.extend(error)
            
            er = []
            if model_detail:
                u, er = _delete_multiple_records(db_name, model_detail, records)
                deleted.extend(u)
                errors.extend(er)

            aux_records, er = validate_delete_model(db_name, model, model_detail, records)
            errors.extend(er)

            u, error = _delete_multiple_records(db_name, model, aux_records)
            deleted.extend(u)
            errors.extend(error)
            
        else:
            error = []
            if model_detail:
                u, error = _delete_multiple_records(db_name, model_detail, records)
                deleted.extend(u)
                errors.extend(error)

            aux_records, er = validate_delete_model(db_name, model, model_detail, records)
            errors.extend(er)

            u, error = _delete_multiple_records(db_name, model, aux_records)
            deleted.extend(u)
            errors.extend(error)

    else:
        if detail_records:
            u, error = _delete_single_record(db_name, model_detail, detail_records)
            deleted.extend(u)
            errors.extend(error)

            er = []
            if model_detail:
                u, er = _delete_single_record(db_name, model_detail, records)
                deleted.extend(u)
                errors.extend(er)

            aux_records, er = validate_delete_model(db_name, model, model_detail, records)
            errors.extend(er)

            u, error = _delete_single_record(db_name, model, aux_records)
            deleted.extend(u)
            errors.extend(error)
        
        else:
            error = []
            if model_detail:
                u, error = _delete_single_record(db_name, model_detail, records)
                deleted.extend(u)
                errors.extend(error)

            aux_records, er = validate_delete_model(db_name, model, model_detail, records)
            errors.extend(er)

            u, error = _delete_single_record(db_name, model, aux_records)
            deleted.extend(u)
            errors.extend(error)

    return deleted, errors
        

def _delete_multiple_records(db_name, model, records):
    deleted = []
    errors = []
    for r in records:
        
        query_dict = dict(r.children)
        query_json = _format_response_from_query_dict(query_dict)
        try:         
            deleted_count, _ = model.objects.using(db_name).filter(r).delete()
            query_json['quantity_deleted'] = deleted_count

            if deleted_count == 0:
                query_json['error'] = 'No matching record found'
                errors.append(query_json)
            else:
                deleted.append(query_json)

        except Exception as e:
            query_json['error'] = str(e)
            errors.append(query_json)

    return deleted, errors


def _delete_single_record(db_name, model, records):
    deleted = []
    errors = []
    for r in records:
        query_dict = dict(r.children)
        query_json = _format_response_from_query_dict(query_dict)

        try:            
            model_instance = model.objects.using(db_name).get(r)
            model_instance.delete(using=db_name)
            deleted.append(query_json)
            
        except model.MultipleObjectsReturned:
            query_json['error'] = 'Cannot delete multiple records without sending the confirmation parameter'
            errors.append(query_json)
            continue

        except model.DoesNotExist:
            query_json['error'] = 'No matching record found'
            errors.append(query_json)
            continue

        except Exception as e:
            query_json['error'] = str(e)
            errors.append(query_json)
            continue
    
    return deleted, errors

