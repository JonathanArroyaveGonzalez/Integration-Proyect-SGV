"""
Capa de servicios para códigos de barras.
"""
from typing import Dict, Any, Optional
import logging

from mercadolibre.functions.BarCode.update import (
    update_barcode_from_meli_item as _update_barcode_from_meli_item,
    get_barcode_from_wms as _get_barcode_from_wms,
    sync_or_update_barcode_from_meli_item as _sync_or_update_barcode_from_meli_item,
)

logger = logging.getLogger(__name__)


def update_barcode_from_meli_item(meli_item: Dict[str, Any], auth_headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    return _update_barcode_from_meli_item(meli_item, auth_headers)


def get_barcode_from_wms(ean: str, auth_headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    return _get_barcode_from_wms(ean, auth_headers)


def sync_or_update_barcode_from_meli_item(meli_item: Dict[str, Any], auth_headers: Optional[Dict[str, str]] = None, assume_new: bool = False) -> Dict[str, Any]:
    return _sync_or_update_barcode_from_meli_item(meli_item, auth_headers, assume_new)
