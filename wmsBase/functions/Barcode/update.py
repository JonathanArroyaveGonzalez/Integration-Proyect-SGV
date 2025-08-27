"""Dependencies"""

from django.db.models import Q


""" Functions and models """
from wmsBase.models.TRelacionCodbarras import TRelacionCodbarras
from wmsAdapterV2.utils.filter_by_field import filter_by_field
from wmsAdapterV2.utils.get_fields_filter import get_fields_filter
from wmsAdapterV2.utils.update_data import update_data
from wmsAdapterV2.utils.update_multiple_records import update_multiple_records
from wmsAdapterV2.utils.validate_fields import validate_fields


def update_barcode(request, db_name, request_data=None):
    try:
        params = dict(request.GET)
    except Exception:
        params = {}

    try:
        query = Q()

        mult, params = update_multiple_records(params)
        fields, params = get_fields_filter(params)
        fields = validate_fields(fields, TRelacionCodbarras)
        query, params = filter_by_field(TRelacionCodbarras, query, params)

        json_query_orm = {
            "db_name": db_name,
            "model": TRelacionCodbarras,
            "query": query,
            "mult": mult,
        }

        updated, errors = update_data(json_query_orm, request_data)
        return updated, errors

    except Exception as e:
        raise ValueError(e)
