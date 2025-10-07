from concurrent.futures import ThreadPoolExecutor
import datetime
from typing import Any, List, Optional, Dict
from mercadolibre.functions.Supplier.base_supplier_service import BaseSupplierService
from mercadolibre.functions.Customer.base_customer_service import ServiceResult
from mercadolibre.utils.exceptions import UserMappingError

import logging

logger = logging.getLogger(__name__)


class MeliSupplierService:

    def __init__(self):
        self.base_supplier_service = BaseSupplierService()

    def _sync_single_supplier(
        self, supplier_id: str, original_request: Any = None
    ) -> ServiceResult:
        """Sync a single supplier (create only)."""
        try:
            supplier_data = self.base_supplier_service.get_supplier_from_meli(
                supplier_id
            )
            if not supplier_data:
                return ServiceResult(
                    success=False,
                    action="error",
                    message="Supplier not found in MercadoLibre",
                    error="not_found",
                )

            wms_supplier = self.base_supplier_service.map_supplier_to_wms(supplier_data)

            result = self.base_supplier_service.create_supplier_in_wms(
                wms_supplier, original_request
            )

            # Keep raw WMS response
            result.wms_response = {
                "supplier_id": supplier_id,
                "wms_data": wms_supplier,
                "raw": result.wms_response,
            }

            return result

        except UserMappingError as e:
            return ServiceResult(
                success=False, action="error", message=str(e), error="mapping_error"
            )

    def sync_specific_suppliers(
        self,
        suppliers_ids: List[str],
        original_request: Any = None,
    ) -> Dict[str, Any]:

        results_summary = {
            "success": True,
            "message": "",
            "total_processed": 0,
            "total_created": 0,
            "total_failed": 0,
            "suppliers_created": [],
            "suppliers_failed": [],
            "processed_at": datetime.datetime.now().isoformat(),
        }

        if not suppliers_ids:
            results_summary.update(
                {
                    "success": False,
                    "total_failed": 1,
                    "suppliers_failed": [
                        {
                            "supplier_id": None,
                            "error_type": "empty_list",
                            "message": "No supplier IDs provided",
                        }
                    ],
                }
            )
            return results_summary

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                sid: executor.submit(self._sync_single_supplier, sid, original_request)
                for sid in suppliers_ids
            }

            for sid, future in futures.items():
                try:
                    result: ServiceResult = future.result()
                    results_summary["total_processed"] += 1

                    if result.success and result.action == "created":
                        results_summary["total_created"] += 1
                        results_summary["suppliers_created"].append(result.wms_response)
                    else:
                        results_summary["total_failed"] += 1
                        results_summary["suppliers_failed"].append(
                            {
                                "supplier_id": sid,
                                "error_type": result.error or "unknown",
                                "message": result.message,
                            }
                        )

                except Exception as e:
                    logger.exception(f"Exception processing supplier {sid}")
                    results_summary["total_processed"] += 1
                    results_summary["total_failed"] += 1
                    results_summary["suppliers_failed"].append(
                        {
                            "supplier_id": sid,
                            "error_type": "exception",
                            "message": str(e),
                        }
                    )

        if results_summary["total_failed"] == 0:
            results_summary["message"] = (
                f"All {results_summary['total_processed']} suppliers synced successfully"
            )
        elif results_summary["total_created"] > 0:
            results_summary["message"] = (
                f"{results_summary['total_created']} suppliers created, "
                f"{results_summary['total_failed']} failed"
            )
        else:
            results_summary["success"] = False
            results_summary["message"] = "All suppliers failed to sync"

        return results_summary


# Singleton + helper
_sync_service: Optional[MeliSupplierService] = None


def get_supplier_sync_service():
    """Get or create singleton instance of MeliSupplierService."""
    global _sync_service
    if _sync_service is None:
        _sync_service = MeliSupplierService()
    return _sync_service


def sync_suppliers(
    supplier_ids: List[str], original_request: Any = None
) -> Dict[str, Any]:
    """Convenience function to sync suppliers without directly instantiating the service."""
    return get_supplier_sync_service().sync_specific_suppliers(
        supplier_ids, original_request
    )
