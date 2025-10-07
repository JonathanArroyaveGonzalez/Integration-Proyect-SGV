import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from mercadolibre.utils.exceptions import UserMappingError, WMSRequestError
from mercadolibre.utils.mapper.data_mapper import CustomerMapper
from .base_customer_service import BaseCustomerService, ServiceResult

logger = logging.getLogger(__name__)


class MeliCustomerSyncService:
    """Service to synchronize MercadoLibre customers with WMS (create only)."""

    def __init__(self):
        self.base_service = BaseCustomerService()

    def _sync_single_customer(
        self, customer_id: str, original_request: Any = None
    ) -> ServiceResult:
        """Sync a single customer (create only)."""
        try:
            customer_data = self.base_service.get_customer_from_meli(customer_id)
            if not customer_data:
                return ServiceResult(
                    success=False,
                    action="error",
                    message="Customer not found in MercadoLibre",
                    error="not_found",
                )

            wms_customer: CustomerMapper = self.base_service.map_customer_to_wms(
                customer_data
            )
            result = self.base_service.create_customer_in_wms(
                wms_customer, original_request
            )

            # Keep raw WMS response
            result.wms_response = {
                "customer_id": customer_id,
                "wms_data": wms_customer,
                "raw": result.wms_response,
            }

            return result

        except (UserMappingError, WMSRequestError) as e:
            return ServiceResult(
                success=False,
                action="error",
                message=str(e),
                error=getattr(e, "status_code", "mapping_or_wms_error"),
            )
        except Exception as e:
            logger.exception(f"Unexpected error syncing customer {customer_id}")
            return ServiceResult(
                success=False, action="error", message=str(e), error="unexpected_error"
            )

    def sync_specific_customers(
        self, customer_ids: List[str], original_request: Any = None
    ) -> Dict[str, Any]:
        """Sync multiple customers in parallel (create only)."""
        results_summary = {
            "success": True,
            "message": "",
            "total_processed": 0,
            "total_created": 0,
            "total_failed": 0,
            "customers_created": [],
            "customers_failed": [],
            "processed_at": datetime.now().isoformat(),
        }

        if not customer_ids:
            results_summary.update(
                {
                    "success": False,
                    "total_failed": 1,
                    "customers_failed": [
                        {"customer_id": None, "message": "No customer IDs provided"}
                    ],
                }
            )
            return results_summary

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                cid: executor.submit(self._sync_single_customer, cid, original_request)
                for cid in customer_ids
            }

            for cid, future in futures.items():
                try:
                    result: ServiceResult = future.result()
                    results_summary["total_processed"] += 1

                    if result.success and result.action == "created":
                        results_summary["total_created"] += 1
                        results_summary["customers_created"].append(result.wms_response)
                    else:
                        results_summary["total_failed"] += 1
                        results_summary["customers_failed"].append(
                            {
                                "customer_id": cid,
                                "message": result.message,
                                "error": result.error or "unknown",
                            }
                        )

                except Exception as e:
                    logger.exception(f"Exception processing customer {cid}")
                    results_summary["total_processed"] += 1
                    results_summary["total_failed"] += 1
                    results_summary["customers_failed"].append(
                        {
                            "customer_id": cid,
                            "message": str(e),
                            "error": "exception",
                        }
                    )

        if results_summary["total_failed"] == 0:
            results_summary["message"] = (
                f"All {results_summary['total_processed']} customers created successfully"
            )
        elif results_summary["total_created"] > 0:
            results_summary["message"] = (
                f"{results_summary['total_created']} customers created, "
                f"{results_summary['total_failed']} failed"
            )
        else:
            results_summary["success"] = False
            results_summary["message"] = "All customers failed to sync"

        return results_summary


# Singleton + helper
_sync_service: Optional[MeliCustomerSyncService] = None


def get_customer_sync_service() -> MeliCustomerSyncService:
    """Get or create singleton instance of MeliCustomerSyncService."""
    global _sync_service
    if _sync_service is None:
        _sync_service = MeliCustomerSyncService()
    return _sync_service


def sync_customers(
    customer_ids: List[str], original_request: Any = None
) -> Dict[str, Any]:
    """Convenience function to sync customers without directly instantiating the service."""
    return get_customer_sync_service().sync_specific_customers(
        customer_ids, original_request
    )
