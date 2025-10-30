from datetime import datetime, timedelta
from django.db.models import Q

def get_date_range(query, query_detail, params, date_field=None):
    if not query_detail.children:
        start_date = None
        end_date = None

        if 'start_date' in params:
            start_date = datetime.strptime(params['start_date'][0], '%Y-%m-%d')
            params.pop('start_date')
        else:
            if not query.children:
                start_date = datetime.now().date() - timedelta(days=30)
                start_date = start_date.strftime('%Y-%m-%d')

        if 'end_date' in params:
            end_date = datetime.strptime(params['end_date'][0], '%Y-%m-%d') + timedelta(days=1)
            end_date = end_date.strftime('%Y-%m-%d')
            params.pop('end_date')
        else:
            if not query.children:
                end_date = datetime.now().date() + timedelta(days=1)
                end_date = end_date.strftime('%Y-%m-%d')
        
        if start_date and end_date:
            if not date_field:
                query &= Q(**{'fecharegistro__range': [start_date, end_date]})
            else:
                query &= Q(**{f'{date_field}__range': [start_date, end_date]})

    return query, params


def get_date_range_fechacrea(query, query_detail, params):
    if not query.children and not query_detail.children:
        if 'start_date' in params:
            start_date = datetime.strptime(params['start_date'][0], '%Y-%m-%d')
            params.pop('start_date')
        else:
            start_date = datetime.now().date() - timedelta(days=30)
            start_date = start_date.strftime('%Y-%m-%d')

        if 'end_date' in params:
            end_date = datetime.strptime(params['end_date'][0], '%Y-%m-%d') + timedelta(days=1)
            end_date = end_date.strftime('%Y-%m-%d')
            params.pop('end_date')
        else:
            end_date = datetime.now().date() + timedelta(days=1)
            end_date = end_date.strftime('%Y-%m-%d')
        
        query &= Q(**{'fechacrea__range': [start_date, end_date]})

    return query, params


def get_date_range_fhbascula5(query, query_detail, params):
    if not query.children and not query_detail.children:
        if 'start_date' in params:
            start_date = datetime.strptime(params['start_date'][0], '%Y-%m-%d')
            params.pop('start_date')
        else:
            start_date = datetime.now().date() - timedelta(days=30)
            start_date = start_date.strftime('%Y-%m-%d')

        if 'end_date' in params:
            end_date = datetime.strptime(params['end_date'][0], '%Y-%m-%d') + timedelta(days=1)
            end_date = end_date.strftime('%Y-%m-%d')
            params.pop('end_date')
        else:
            end_date = datetime.now().date() + timedelta(days=1)
            end_date = end_date.strftime('%Y-%m-%d')
        
        query &= Q(**{'fh_bascula_5__range': [start_date, end_date]})

    return query, params