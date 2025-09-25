"""
Capa de servicios para clientes MercadoLibre/WMS.
Delegación a funciones existentes y estandarización de interfaz.
"""
from typing import Dict, Any, Optional
import logging

from mercadolibre.functions.Customer.sync_customer import (
    create_customer_in_wms as _create_customer_in_wms,
    update_customer_in_wms as _update_customer_in_wms,
)

logger = logging.getLogger(__name__)


def create_customer(ml_customer_id: str, auth_headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Crea cliente en WMS desde datos de MercadoLibre."""
    return _create_customer_in_wms(ml_customer_id, auth_headers=auth_headers)


def update_customer(ml_customer_id: str, auth_headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Actualiza cliente en WMS desde datos de MercadoLibre."""
    return _update_customer_in_wms(ml_customer_id, auth_headers=auth_headers)
