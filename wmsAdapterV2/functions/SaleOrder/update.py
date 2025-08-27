from django.db.models import Q

from wmsAdapterV2.models import TdaWmsDpk, TdaWmsEpk
from wmsAdapterV2.utils.filter_by_field import filter_by_field
from wmsAdapterV2.utils.get_fields_filter import get_fields_filter
from wmsAdapterV2.utils.update_data import update_data
from wmsAdapterV2.utils.update_multiple_records import update_multiple_records
from wmsAdapterV2.utils.validate_fields import validate_fields
from wmsAdapterV2.utils.validate_fields_model_and_detail import validate_field_model_and_detail


def update_sale_order(request, db_name, request_data=None):
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
        
        if isinstance(request_data, dict):
            if 'order_detail' in request_data:
                    for ord in request_data['order_detail']:
                        if 'field_qtypedidabase' in ord:
                            del ord['field_qtypedidabase']
        elif isinstance(request_data, list):
            for r in request_data:
                if 'order_detail' in r:
                    for ord in r['order_detail']:
                        if 'field_qtypedidabase' in ord:
                            del ord['field_qtypedidabase']

        updated, errors = update_data(json_query_orm, request_data)
        return updated, errors

    except Exception as e:
        raise ValueError(e)