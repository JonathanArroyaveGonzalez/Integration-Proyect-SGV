from django.db.models import Q

from wmsAdapterV2.utils.format_json_from_query import format_response_from_query_dict
from wmsAdapterV2.utils.validate_fields import get_transfer_state_field

def validate_transfer_state(db_name, model, query):
    transfer_field = get_transfer_state_field(model)

    if transfer_field:
        query &= Q(**{f'{transfer_field}__gte': 3})

        results = list(model.objects.using(db_name).filter(query))

        if len(results) > 0:
            return len(results)
        
    return 0


def validate_records_with_transfer_state(db_name, model, query, model_detail, query_detail, detail_records, flag_delete_order):
    if flag_delete_order:
        tranfers_model = validate_transfer_state(db_name, model, query)
        
        tranfers_detail_model = 0
        if model_detail:
            tranfers_detail_model = validate_transfer_state(db_name, model_detail, query)
        
        if tranfers_model > 0 or tranfers_detail_model > 0:
            raise ValueError('Record cannot be deleted, it has already been executed to forward to erp.')
                
    elif detail_records:
        tranfers_model = validate_transfer_state(db_name, model, query)
        
        if model_detail:
            for det in detail_records:
                tranfers_detail_model = validate_transfer_state(db_name, model_detail, det)
                if tranfers_model > 0 or tranfers_detail_model > 0:
                    raise ValueError('Record cannot be deleted, it has already been executed to forward to erp.')

    elif query_detail.children:
        tranfers_model = validate_transfer_state(db_name, model, query)
        
        tranfers_detail_model = 0
        if model_detail:
            tranfers_detail_model = validate_transfer_state(db_name, model_detail, query_detail)
        
        if tranfers_model > 0 or tranfers_detail_model > 0:
            raise ValueError('Record cannot be deleted, it has already been executed to forward to erp.')
        
        
def validate_delete_model(db_name, model, model_detail, records):
    aux_records = []
    errors = []
    for r in records:
        try:
            validate_records_with_transfer_state(db_name, model, r, model_detail, Q(), [], True)

            count = 0
            if model_detail:
                count = len(list(model_detail.objects.using(db_name).filter(r).values()))

            if count > 0:
                query_dict = dict(r.children)
                query_json = format_response_from_query_dict(query_dict)
                query_json['error'] = 'Cannot be deleted, there are still associated order details'
                errors.append(query_json)  
            else:
                aux_records.append(r)

        except Exception as e:
            query_dict = dict(r.children)
            query_json = format_response_from_query_dict(query_dict)
            query_json['error'] = str(e)
            errors.append(query_json)  

    return aux_records, errors
