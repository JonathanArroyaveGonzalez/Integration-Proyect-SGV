"""
Supplier update service.

Handles updating individual suppliers from MercadoLibre to WMS.
Only updates existing suppliers - does not create new ones.
Uses BaseSupplierService for core operations (fetching, mapping).
"""

import datetime
import logging
from typing import Any, Optional

from mercadolibre.functions.Supplier.base_supplier_service import (
    BaseSupplierService,
    ServiceResult,
)
from mercadolibre.utils.exceptions import (
    UserMappingError,
    WMSRequestError,
)

logger = logging.getLogger(__name__)

ENDPOINT_SUPPLIER = "wms/adapter/v2/prv"


class SupplierUpdateService:
    """Service for updating single MercadoLibre suppliers in WMS."""

    def __init__(self):
        self.base_supplier_service = BaseSupplierService()

    def update_supplier(
        self, supplier_id: str, original_request: Any = None
    ) -> ServiceResult:
        if not supplier_id:
            return ServiceResult(
                success=False,
                action="error",
                message="Supplier ID is None or empty",
                error="invalid_supplier_id",
            )

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

            # Ensure the item field is set for UPDATE identification
            wms_supplier_map["item"] = supplier_id

            supplier_response = self.base_supplier_service.get_internal_api().put(
                ENDPOINT_SUPPLIER,
                original_request=original_request,
                json=[wms_supplier_map],
            )

            # Parse JSON only if response has content
            try:
                resp_json = supplier_response.json() if supplier_response.text else {}
            except Exception:
                resp_json = {}

            if supplier_response.status_code in (200, 201):
                return ServiceResult(
                    success=True,
                    action="updated",
                    message="Supplier has been updated successfully",
                    wms_response={
                        "supplier_id": supplier_id,
                        "ml_data": supplier_data,
                        "wms_data": wms_supplier_map,
                        "raw": resp_json,
                        "updated_at": datetime.datetime.now().isoformat(),
                    },
                )

            elif supplier_response.status_code == 404:
                return ServiceResult(
                    success=False,
                    action="not_found",
                    message=f"Supplier {supplier_id} not found in WMS. Use create endpoint instead.",
                    error="supplier_not_found_in_wms",
                )

            elif supplier_response.status_code == 400:
                error_detail = resp_json.get(
                    "errors", resp_json.get("error", "Bad request")
                )
                return ServiceResult(
                    success=False,
                    action="error",
                    message=f"Bad request: {error_detail}",
                    error="bad_request",
                    wms_response=resp_json,
                )

            else:
                raise WMSRequestError(
                    status_code=supplier_response.status_code,
                    message=supplier_response.text[:200],
                )

        except (UserMappingError, WMSRequestError) as e:
            logger.exception(f"Mapping or WMS error for supplier {supplier_id}")
            return ServiceResult(
                success=False,
                action="error",
                message=str(e),
                error=getattr(e, "status_code", "mapping_or_wms_error"),
            )

        except Exception as e:
            logger.exception(f"Unexpected error updating supplier {supplier_id}")
            return ServiceResult(
                success=False,
                action="error",
                message=str(e),
                error="unexpected_error",
            )


# ----------------------------
# Singleton + convenience functions
# ----------------------------
_update_service: Optional[SupplierUpdateService] = None


def get_supplier_update_service() -> SupplierUpdateService:
    global _update_service
    if _update_service is None:
        _update_service = SupplierUpdateService()
    return _update_service


def update_single_supplier(
    supplier_id: str, original_request: Any = None
) -> ServiceResult:
    return get_supplier_update_service().update_supplier(supplier_id, original_request)
