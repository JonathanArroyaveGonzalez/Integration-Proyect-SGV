"""
API v1 - Clientes MercadoLibre/WMS
"""
import json
from typing import List
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from mercadolibre.services.customer_service import (
    create_customer as svc_create_customer,
    update_customer as svc_update_customer,
)
from mercadolibre.utils.response_helpers import (
    create_success_response,
    create_error_response,
    handle_json_decode_error,
    handle_internal_server_error,
)
from mercadolibre.utils.auth_helpers import extract_auth_headers


def _extract_ids(data: dict) -> List[str] | None:
    if "ml_customer_id" in data:
        return [data["ml_customer_id"]]
    if "ml_customer_ids" in data:
        ids = data["ml_customer_ids"]
        if isinstance(ids, list):
            return ids
    return None


@csrf_exempt
@require_http_methods(["POST"])

def create(request):
    try:
        auth_headers = extract_auth_headers(request)
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return handle_json_decode_error()

        ids = _extract_ids(data)
        if not ids:
            return create_error_response(
                message="Debes enviar 'ml_customer_id' o 'ml_customer_ids'",
                errors=["ml_customer_id (str) o ml_customer_ids (list) son requeridos"],
                status=400,
            )

        created, errors = [], []
        for cid in ids:
            if not cid:
                errors.append("ID vacío encontrado")
                continue
            res = svc_create_customer(cid, auth_headers=auth_headers)
            created.extend(res.get("created", []))
            errors.extend(res.get("errors", []))

        # 201 si solo éxitos, 207 si parcial, 400 si solo errores
        status = 201 if created and not errors else (207 if created and errors else 400)
        return create_success_response(data={"created": created, "errors": errors}, message="Procesado", status=status)
    except Exception as e:
        return handle_internal_server_error(e, "create customer")


@csrf_exempt
@require_http_methods(["PUT", "PATCH"])

def update(request):
    try:
        auth_headers = extract_auth_headers(request)
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return handle_json_decode_error()

        ids = _extract_ids(data)
        if not ids:
            return create_error_response(
                message="Debes enviar 'ml_customer_id' o 'ml_customer_ids'",
                errors=["ml_customer_id (str) o ml_customer_ids (list) son requeridos"],
                status=400,
            )

        updated, errors = [], []
        for cid in ids:
            if not cid:
                errors.append("ID vacío ignorado")
                continue
            res = svc_update_customer(cid, auth_headers=auth_headers)
            updated.extend(res.get("updated", []))
            errors.extend(res.get("errors", []))

        status = 200 if updated and not errors else (207 if updated and errors else 400)
        return create_success_response(data={"updated": updated, "errors": errors}, message="Procesado", status=status)
    except Exception as e:
        return handle_internal_server_error(e, "update customer")
