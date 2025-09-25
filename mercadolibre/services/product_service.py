"""
Capa de servicios para operaciones con productos de MercadoLibre.
Encapsula la lógica de negocio y llamadas externas para mantener las vistas ligeras.
"""
from typing import Dict, Any, List, Optional
import logging

from mercadolibre.utils.api_client import (
    make_authenticated_request,
    get_meli_api_base_url,
)
from mercadolibre.functions.Product.update import update_product_from_meli_to_wms as _update_product_from_meli_to_wms

logger = logging.getLogger(__name__)


def list_products() -> Dict[str, Any]:
    """Obtiene listado de productos del usuario autenticado en MercadoLibre."""
    base_url = get_meli_api_base_url()
    url = f"{base_url}users/me/items/search"
    resp = make_authenticated_request("GET", url)
    if resp.status_code == 200:
        return {"success": True, "data": resp.json()}
    return {
        "success": False,
        "message": f"API error: {resp.status_code}",
        "errors": resp.text,
        "status": resp.status_code,
    }


def create_product(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Crea un producto en MercadoLibre."""
    base_url = get_meli_api_base_url()
    url = f"{base_url}items"
    resp = make_authenticated_request("POST", url, json=payload)
    if resp.status_code == 201:
        return {"success": True, "data": resp.json(), "status": 201}
    return {
        "success": False,
        "message": f"API error: {resp.status_code}",
        "errors": resp.text,
        "status": resp.status_code,
    }


def update_product_from_meli_to_wms(product_id: str, auth_headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Delegación a la función existente, expuesta como servicio."""
    return _update_product_from_meli_to_wms(product_id, auth_headers)
