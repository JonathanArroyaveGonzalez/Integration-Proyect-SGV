"""
API v1 - Códigos de barras (WMS/ML)
"""
import json
from typing import Dict, Any, List
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from mercadolibre.services.barcode_service import (
    get_barcode_from_wms as svc_get_barcode,
    sync_or_update_barcode_from_meli_item as svc_sync_or_update_barcode,
)
from mercadolibre.utils.response_helpers import (
    create_success_response,
    create_error_response,
    handle_json_decode_error,
    handle_internal_server_error,
)
from mercadolibre.utils.auth_helpers import extract_auth_headers


@csrf_exempt
@require_http_methods(["GET"])

def get_barcode(request, ean: str):
    """Obtiene un código de barras desde el WMS por EAN."""
    try:
        if not ean or not ean.strip():
            return create_error_response(
                message="EAN requerido",
                errors="Debe proporcionar un EAN válido",
                status=400,
            )
        auth_headers = extract_auth_headers(request)
        result = svc_get_barcode(ean, auth_headers)
        if result.get("success"):
            return create_success_response(data=result.get("data", {}), message=result.get("message", "OK"))
        status = 404 if "no encontrado" in result.get("message", "").lower() else 400
        return create_error_response(message=result.get("message", "Error consultando"), status=status)
    except Exception as e:
        return handle_internal_server_error(e, f"consulta de código de barras {ean}")


@csrf_exempt
@require_http_methods(["POST"])

def sync_from_meli_items(request):
    """
    Sincroniza/actualiza códigos de barras a partir de items de MercadoLibre.
    Body:
      - meli_items: list[dict] o dict (un solo item)
      - assume_new: bool (opcional, por defecto False)
    """
    try:
        auth_headers = extract_auth_headers(request)
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return handle_json_decode_error()

        meli_items = data.get("meli_items")
        assume_new = data.get("assume_new", False)

        if not meli_items:
            return create_error_response(
                message="meli_items es requerido",
                errors="Debe enviar un diccionario de item o una lista de items de MercadoLibre",
                status=400,
            )

        # normalizar a lista
        if isinstance(meli_items, dict):
            meli_items = [meli_items]
        if not isinstance(meli_items, list):
            return create_error_response(
                message="meli_items debe ser dict o list",
                status=400,
            )

        processed, errors, results = 0, 0, []
        for item in meli_items:
            res = svc_sync_or_update_barcode(item, auth_headers=auth_headers, assume_new=assume_new)
            processed += 1 if res.get("success") else 0
            errors += 0 if res.get("success") else 1
            results.append({"item_id": item.get("id"), "result": res})

        msg = f"Códigos de barras: {processed} procesados exitosamente"
        if errors:
            msg += f", {errors} con errores"
        return create_success_response(data={"results": results}, message=msg, status=200 if errors == 0 else 207)
    except Exception as e:
        return handle_internal_server_error(e, "sincronización de códigos de barras desde ML")
