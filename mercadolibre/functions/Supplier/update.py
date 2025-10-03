"""
Supplier update service.

Handles updating individual suppliers from MercadoLibre to WMS.
If a supplier does not exist in WMS, it will be created automatically.
Uses BaseSupplierService for core operations (fetching, mapping, creating).
"""

import logging
from typing import Any, Optional

from mercadolibre.functions.Supplier.base_supplier_service import (
    BaseSupplierService,
    ServiceResult,
)
from mercadolibre.utils.exceptions import UserMappingError, WMSRequestError

logger = logging.getLogger(__name__)

ENDPOINT_SUPPLIER = "wms/adapter/v2/supplier"


class SupplierUpdateService:
    """
    Service for updating single MercadoLibre suppliers in WMS.
    """

    def __init__(self):
        self.base_supplier_service = BaseSupplierService()

    def update_supplier(
        self, supplier_id: str, original_request: Any = None
    ) -> ServiceResult:
        try:
            supplier_data = self.base_supplier_service.get_supplier_from_meli(
                supplier_id
            )
            if not supplier_data:
                return ServiceResult(
                    success=False,
                    action="error",
                    message="Supplier not found in MercadoLibre",
                    error="meli_not_found",
                )

            wms_supplier_map = self.base_supplier_service.map_supplier_to_wms(
                supplier_data
            )

            supplier_response = self.base_supplier_service.get_internal_api().put(
                ENDPOINT_SUPPLIER,
                original_request=original_request,
                json=[wms_supplier_map],
            )

            if supplier_response.status_code in (200, 201):
                return ServiceResult(
                    success=True,
                    action="updated",
                    message="Supplier has been updated",
                    wms_response=supplier_response.json(),
                )

            # Fallback: si no existe en WMS, lo creo
            if supplier_response.status_code == 404:
                logger.warning(
                    f"Supplier {supplier_id} not found in WMS. Falling back to create."
                )
                create_result = self.base_supplier_service.create_supplier_in_wms(
                    wms_supplier_map, original_request
                )
                return ServiceResult(
                    success=create_result.success,
                    action="created_via_fallback",
                    message="Supplier did not exist in WMS, created instead.",
                    wms_response=create_result.wms_response,
                )

            return ServiceResult(
                success=False,
                action="error",
                message=f"WMS update failed: {supplier_response.text[:200]}",
                error=f"wms_{supplier_response.status_code}",
            )

        except Exception as e:
            logger.exception(f"Unexpected error updating supplier {supplier_id}")
            return ServiceResult(
                success=False, action="error", message=str(e), error="unexpected_error"
            )


# ----------------------------
# Singleton + convenience functions
# ----------------------------
_update_service: Optional[SupplierUpdateService] = None


def get_supplier_update_service() -> SupplierUpdateService:
    """Get or create singleton instance of SupplierUpdateService."""
    global _update_service
    if _update_service is None:
        _update_service = SupplierUpdateService()
    return _update_service


def update_single_supplier(
    supplier_id: str, original_request: Any = None
) -> ServiceResult:
    return get_supplier_update_service().update_supplier(supplier_id, original_request)
