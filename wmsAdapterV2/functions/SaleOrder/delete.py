from django.db.models import Q

from wmsAdapterV2.models import TdaWmsDpk, TdaWmsEpk
from wmsAdapterV2.utils.delete_data import delete_data
from wmsAdapterV2.utils.filter_by_field import filter_by_field
from wmsAdapterV2.utils.get_fields_filter import get_fields_filter
from wmsAdapterV2.utils.update_multiple_records import update_multiple_records
from wmsAdapterV2.utils.validate_fields import validate_fields
from wmsAdapterV2.utils.validate_fields_model_and_detail import validate_field_model_and_detail


def delete_sale_order(request, db_name, request_data=None):
    try:
        params = dict(request.GET)
    except Exception:
        params = {}

    try:
        query = Q()

        mult, params = update_multiple_records(params)
        fields, params = get_fields_filter(params)
        fields = validate_fields(fields, TdaWmsEpk)
        query, params = filter_by_field(TdaWmsEpk, query, params)
        query_detail, params = validate_field_model_and_detail(query, params)
        query_detail, params = filter_by_field(TdaWmsDpk, query_detail, params)
        
        json_query_orm = {
            'db_name': db_name, 
            'model': TdaWmsEpk, 
            'model_detail': TdaWmsDpk,
            'query': query, 
            'query_detail': query_detail,
            'mult': mult
        }
        
        updated, errors = delete_data(json_query_orm, request_data)
        return updated, errors

    except Exception as e:
        raise ValueError(e)