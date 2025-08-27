""" Dependencies """
from django.db.models import Q

from wmsAdapterV2.utils.delete_data import delete_data
from wmsAdapterV2.utils.filter_by_field import filter_by_field
from wmsAdapterV2.utils.get_fields_filter import get_fields_filter
from wmsAdapterV2.utils.update_multiple_records import update_multiple_records
from wmsAdapterV2.utils.validate_fields import validate_fields
from wmsBase.models.TDetalleRefenciaCv import TDetalleRefenciaCv

""" Functions and models """

def delete_logistic_variables(request, db_name, request_data=None):
    try:
        params = dict(request.GET)
    except Exception:
        params = {}

    try:
        query = Q()

        mult, params = update_multiple_records(params)
        fields, params = get_fields_filter(params)
        fields = validate_fields(fields, TDetalleRefenciaCv)
        query, params = filter_by_field(TDetalleRefenciaCv, query, params)
        
        json_query_orm = {
            'db_name': db_name, 
            'model': TDetalleRefenciaCv, 
            'query': query, 
            'mult': mult
        }
        
        updated, errors = delete_data(json_query_orm, request_data)
        return updated, errors

    except Exception as e:
        raise ValueError(e)